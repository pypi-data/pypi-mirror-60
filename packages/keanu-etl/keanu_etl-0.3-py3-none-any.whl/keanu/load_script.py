import operator
import click
from glob import glob
import re
from sqlalchemy import text
import click
from .run_statement import RunStatement
from . import util
import os
from pymysql.err import MySQLError
from sqlalchemy.exc import IntegrityError, InternalError, ProgrammingError, DataError
from .tracing import tracer

class LoadScript(RunStatement):
    """
    Class that runs load scripts, that is SQL that loads some data in keanu database.
    It can read extra metadata from the script comments.

    Pass path to file of SQL script.

    options can be:
    incremental - run incremental variant of the script (no by default)
    display - displays full SQL while executing (no by default)
    warn - do show warnings from mysql driver (no by default)
    """
    def __init__(_, filename, mode, source, destination):
        # filename and class options
        _.filename = filename
        _.options = {
            'incremental': False,
            'display': False,
            'warn': False
        }
        _.options.update(mode)
        _.source = source
        _.destination = destination
        _.script_tracer_tags = {}

        # defaults
        _.deleteSql = []
        _.order = 100

        # parse SQL
        _.lines = _.parse(open(filename, 'r').readlines())
        _.statements = _.split_statements(_.lines)

    @staticmethod
    def from_directory(sqldir, mode, source, destination):
        files = glob(os.path.join(sqldir, '**/*.sql'), recursive=True)
        if len(files) == 0:
            raise click.BadParameter('No script files found in {}'.format(sqldir), param_hint='config_or_dir')
        scripts = list(map(lambda fn: LoadScript(fn, mode, source, destination), files))
        return scripts

    def __str__(_):
        return '{} ({})'.format(_.filename, _.order)

    """
    Parse script lines and load metadata. Returns list of lines after parsing (will be modified).
    Has effects of setting fields on object.
    """
    def parse(_, lines):
        out = []
        contexts = []
        comment_line = lambda x: '-- ' + x

        lines = map(_.interpolate_environ, lines)

        for l in lines:
            m = re.match(r" *-- *ORDER: (\d+)", l)
            if m:
                _.order = int(m.group(1))
                continue

            m = re.match(r" *-- *TAGS: ?(.+)$", l)
            if m:
                kv = {x.group(1) : x.group(2)
                      for x in
                      re.finditer(r"([\w\d_-]+) *= *([\w\d_-]+)", m.group(1))}
                _.script_tracer_tags.update(kv)

                continue

            m = re.match(r" *-- *((DELETE|TRUNCATE) .*)$", l)
            if m:
                _.deleteSql.append(m.group(1))
                continue


            m = re.match(r" *-- *BEGIN (\w+)", l)
            if m:
                contexts.append(m.group(1).upper())
                continue

            m = re.match(r" *-- *END (\w+)", l)
            if m:
                try:
                    contexts.remove(m.group(1).upper())
                except ValueError:
                    raise ValueError("{}: found END {} but context stack is {}".format(
                        _.filename,
                        m.group(1),
                        ', '.join(contexts)))
                continue

            m = re.match(r" *-- *IGNORE", l)
            if m:
                break

            if 'INCREMENTAL' in contexts and not _.options['incremental']:
                l = comment_line(l)

            if 'INITIAL' in contexts and _.options['incremental']:
                l = comment_line(l)


            out.insert(0, l)

        if len(contexts) > 0:
            raise VelueError("Script {} ended with contexts {} unclosed",
                             _.filename, ', '.join(contexts))

        out.reverse()
        return out

    """
    Performs interpolation on string, replacing ${FOO} with FOO environment variable.
    """
    def interpolate_environ(_, line):
        env = {}
        if _.source:
            env.update(_.source.environ())
        if _.destination:
            env.update(_.destination.environ())
        def get_var(m):
            return env[m.group(1)]
        return re.subn(r"[$]{([A-Za-z1-9_]+)}", get_var, line)[0]

    """
    Predicate - is this line just a comment line?
    """
    @staticmethod
    def noop_line(line):
        return (re.match(r" *--", line)
                or re.match(r"^[\s;]*$", line)) is not None

    """
    Will split the lines of script into SQL statements (separated by semicolon)
    """
    def split_statements(_, lines):
        def non_empty_block(statements):
            return len(statements) > 0 and any(map(lambda a: not _.noop_line(a), statements))

        # output list of statement lists, and current list
        out = []
        c = []

        # current delimiter
        delimiter = ';'

        for l in lines:
            # For delimiter MySQL client command, change the regex and continue
            m = re.match(r"DELIMITER (.+)\s*$", l)
            if m:
                delimiter = re.escape(m.group(1))
                continue

            # For end of statement block (according to delimiter), store in out
            m = re.search(r"(.*)" + delimiter + r"\s*($|--.*$)", l)
            if m:
                c.append(m.group(1))

                if non_empty_block(c):
                    out.append(c)
                c = []
            else:
                c.append(l)

        # join lines into str for each statement
        return list(map(lambda a: ''.join(a).lstrip(), out))

    def replace_sql_object(_, before, after):
        before = "`{}`".format(before)
        after = "`{}`".format(after)
        _.statements = list(map(lambda st: st.replace(before, after), _.statements))

    def statement_abbrev(_, statement):
        if _.options['display']:
            return statement

        trim_to = max(50, int(os.get_terminal_size().columns / 2))
        lines = statement.split("\n")
        lines = filter(lambda x: not re.match(r" *--", x) and not re.match(r"\s*$", x), lines)
        try:
            first = next(lines)
            if len(first) > trim_to:
                first =  first[0:trim_to] + '...'
            return first
        except StopIteration:
            return ''

    def delete(_):
        if len(_.deleteSql) == 0:
            return

        connection = _.destination.connection()
        with tracer.start_active_span(
                'delete.{}'.format(_.filename.replace('/', '.')),
                tags=_.tracer_tags):
            with connection.begin() as transaction:
                yield 'sql.script.start.delete', { 'script': _ }
                try:
                    for event, data in super().execute(connection, _.deleteSql, warn=_.options['warn']):
                        yield event, data
                except KeyboardInterrupt as ctrlc:
                    transaction.rollback()
                    raise ctrlc
                yield 'sql.script.end.delete', { 'script': _ }


    def execute(_):
        if len(_.statements) == 0:
            return

        connection = _.destination.connection()
        with tracer.start_active_span(
                'script.{}'.format(_.filename.replace('/', '.')),
                tags=_.tracer_tags):
            with connection.begin() as transaction:
                try:
                    yield 'sql.script.start', { 'script': _ }
                    for event, data in super().execute(connection, _.statements, warn=_.options['warn']):
                        yield event, data
                    yield 'sql.script.end', { 'script': _ }
                except KeyboardInterrupt as ctrlc:
                    transaction.rollback()
                    raise click.Abort("aborted.")
                except (ProgrammingError, IntegrityError, MySQLError, InternalError, DataError) as e:
                    transaction.rollback()
                    msg = str(e.args[0])
                    msg = msg.replace('\\n', "\n")
                    click.echo(message=msg, err=True)
                    raise click.Abort(msg)
            

    @staticmethod
    def sort(scripts):
        return scripts.sort(key=operator.attrgetter('order'))

    @property
    def tracer_tags(_):
        t = {
            'incremental': _.options['incremental'] == True,
            }
        if _.source:
            t['source_name'] = _.source.name
        if _.destination:
            t['destination_name'] = _.destination.name
        t.update(_.script_tracer_tags)
        return t

