#!/usr/bin/env python

# project name
__project__ = "pyetldb"

# project version
__version__ = "0.1"

# prohect author
__author__ = "natanaelfneto"
__authoremail__ = "natanaelfneto@outlook.com"

# project source code
__source__ = "https://github.com/natanaelfneto/pyetldb"

# project short description
short_description = '''Python module that allows an easy interconnection between Microsoft Access and a support server for SQL with data sync'''

# project general description
__description__ = f'''This Python module: {short_description}'''

# third party imports
import argparse
import getpass
import logging
import os
import pathlib
import sys
import time
import unidecode
#
import pypyodbc
import pyodbc

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from datetime import datetime

import cx_Oracle


class DatabaseCrawler(object):
    # init
    def __init__(self):
        '''
            Initiate a Main instance
        '''

        # self.schemas = self.schemas()
    
    # enter function for class basic rotine
    def __enter__(self):
        '''
            Function for entering class with python 3 standards of
            'with' parameter and a following __exit__ function for
            a cleanner use of the class instancies
        '''
        try:
            return self
        except StopIteration:
           raise RuntimeError("Instance could not be returned")
    
    #
    def sync(self, debug=False, source=None, target=None):
        
        databases = connect(debug=debug, databases=[source, target])
        source = databases[str(source)]
        target = databases[str(target)]

        LOGGER.adapter.info(f"Start syncing data from {source.provider} to {target.provider}...")

        # ORACLE AS TARGET
        if target.provider == Interface().db.ORACLE():
            # target.database.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            target_cursor = target.database.connection.cursor()
            query = f'''
                SELECT
                    table_name
                FROM
                    all_tables
                WHERE 
                    owner = '{target.database.dsn.user}' OR
                    owner = '{target.database.dsn.user.upper()}'
            '''
            target_cursor.execute(query)
            target_tables = [table[0] for table in target_cursor.fetchall()]
            target_cursor.close()

            # print(target.database.dsn.user, target_database)

            if len(target_tables) == len([]):
                LOGGER.adapter.debug(f"Database for user: {target.database.dsn.user} does not exist. Please create ir first.")
            #     target_cursor = target.database.connection.cursor()
            #     query = f'''CREATE DATABASE {target.database.dsn.name}'''
            #     LOGGER.adapter.debug(f"Querying {query}")
            #     target_cursor.execute(query)
            #     target_cursor.close()

            if source.provider == Interface().db.ODBC():
                source_cursor = source.database.connection.cursor()
                tables = list(filter(None, [table[2] if 'msy' not in str(table).lower() else None for table in source_cursor.tables()]))
                LOGGER.adapter.info(f"Found {len(tables)} tables to be copied")
                source_cursor.close()

                LOGGER.adapter.info(f"Copying...")
                for count, table in enumerate(tables, 1):

                    LOGGER.adapter.debug(f"Copying {count} out of {len(tables)} found tables")
                    table_name = table.replace(' ','_').replace('-','_').lower()
                    LOGGER.adapter.debug(f"Copying {table} as {table_name}")

                    source_cursor = source.database.connection.cursor()
                    try:
                        columns = source_cursor.columns(table=table)
                        columns = [
                            {
                                'name': unidecode.unidecode(column[3]),
                                'datatype': column[5],
                                'lenght': column[6],
                                'table': table
                            }
                            for column in columns
                        ]
                    except:
                        columns = []
                    query = f'''SELECT * FROM "{table.lower()}"'''
                    LOGGER.adapter.debug(f"Querying: {query}")

                    try: 
                        source_cursor.execute(query)
                        rows = source_cursor.fetchall()
                        source_cursor.close()
                    except:
                        rows = []
                    LOGGER.adapter.debug(f"Table has {len(rows)} rows with {len(columns)} columns")

                    cleared_columns = []
                    uncleared_columns = []
                    columns_with_datatypes = []

                    for column in columns:
                                                
                        column_name = column['name'].lower()
                        cleared_column_name = column['name'].replace('-','_').replace(' ','_').replace('#','').lower()

                        datatype = column['datatype']
                        lenght = f'''({column['lenght']})'''
                        
                        if datatype == 'DATETIME':
                            datatype = 'TIMESTAMP'
                            lenght = '(0)'

                        else:
                            datatype = 'varchar2'
                            lenght = '(1000)'

                        column_with_datatype = f'''{cleared_column_name} {datatype}{lenght}'''

                        if column_with_datatype in columns_with_datatypes:
                            column_with_datatype = f'''{cleared_column_name}_ {datatype}{lenght} NULL'''
                        
                        columns_with_datatypes.append(column_with_datatype)
                        cleared_columns.append(cleared_column_name)

                        if cleared_column_name == column_name:
                            uncleared_columns.append(column_name)

                        else:
                            uncleared_columns.append(f'''"{column_name}" as {cleared_column_name}''')

                    table_name = unidecode.unidecode(f'pyetl_{table_name}')
                    
                    if not columns_with_datatypes:
                        LOGGER.adapter.debug(f"No value to be retrieved from {table_name}")   
                    else:
                        query = f'''CREATE TABLE {table_name} ({', '.join(columns_with_datatypes)})'''
                        LOGGER.adapter.debug(f"Querying: {query}")

                        if not (table_name in target_tables or table_name.upper() in target_tables):
                            
                            target_cursor = target.database.connection.cursor()
                            target_cursor.execute(query)
                            target_cursor.close()

                            target_cursor = target.database.connection.cursor()
                            query = f'''TRUNCATE {table_name}; COMMIT;'''
                            target_cursor.execute(query)
                            target_cursor.close()
                            
                        for count, row in enumerate(rows):
                            cleared_row = []
                            for value in row:

                                if type(value) in [type(''), type(1)]:
                                    cleared_row.append(value)
                                    pass

                                elif type(value) == type(datetime(2000, 1, 1, 1, 1)):
                                    cleared_row.append(f'#timestamp#{value}')
                                
                                elif type(value) == type(None):
                                    cleared_row.append(None)

                                elif 'bytearray' in str(value):
                                    s = str(value)
                                    found = s[s.find("(")+3:s.find(")")-1]
                                    arr = bytearray(found, 'utf-8')
                                    cleared_row.append(1)
                                
                                elif str(value) == str(True):
                                    cleared_row.append(True)
                                
                                elif str(value) == str(False):
                                    cleared_row.append(False)

                                else:
                                    cleared_row.append(str(value))

                            # print(cleared_row)
                            row = [f"'{value}'" if value else 'NULL' for value in cleared_row]
                            row = [True if str(value) == str(True) else value for value in row]
                            row = [False if str(value) == str(False) else value for value in row]
                            row = [f"TO_DATE({value.replace('#timestamp#', '')}, 'yyyy/mm/dd hh24:mi:ss')" if '#timestamp#' in value else value for value in row]

                            target_cursor = target.database.connection.cursor()
                            query = f'''INSERT INTO {table_name} ({', '.join(cleared_columns)}) VALUES ({", ".join(row)})'''
                            LOGGER.adapter.debug(f"Querying: {query}")
                            target_cursor.execute(query)
                            target.database.connection.commit()
                            target_cursor.close()
                            print(f"Inserted {count} of {len(rows)} rows in {target.provider}'s {table_name} from {source.provider}'s {table_name}", end="\r")
                            
        # POTGRES AS TARGET
        if target.provider == Interface().db.POSTGRES():
            target.database.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            target_cursor = target.database.connection.cursor()
            query = f'''
                SELECT
                    datname
                FROM
                    pg_catalog.pg_database
                WHERE 
                    datname = '{target.database.dsn.name}'
            '''
            target_cursor.execute(query)
            target_database = [db for db in target_cursor.fetchall()]
            target_cursor.close()

            if len(target_database) == len([]):
                LOGGER.adapter.debug(f"Database {target.database.dsn.name} does not exist. Creating...")
                target_cursor = target.database.connection.cursor()
                query = f'''CREATE DATABASE {target.database.dsn.name}'''
                LOGGER.adapter.debug(f"Querying {query}")
                target_cursor.execute(query)
                target_cursor.close()

            if source.provider == Interface().db.ODBC():
                source_cursor = source.database.connection.cursor()
                tables = [table[2] for table in source_cursor.tables()]
                LOGGER.adapter.info(f"Found {len(tables)} tables to be copied")
                source_cursor.close()

                LOGGER.adapter.info(f"Copying...")
                for count, table in enumerate(tables, 1):

                    LOGGER.adapter.debug(f"Copying {count} out of {len(tables)} found tables")
                    table_name = table.replace(' ','_').replace('-','_').lower()
                    LOGGER.adapter.debug(f"Copying {table} as {table_name}")

                    source_cursor = source.database.connection.cursor()
                    try:
                        columns = source_cursor.columns(table=table)
                        columns = [
                            {
                                'name': column[3],
                                'datatype': column[5],
                                'lenght': column[6],
                                'table': table
                            }
                            for column in columns
                        ]
                    except:
                        columns = []
                    query = f'''SELECT * FROM "{table.lower()}"'''
                    LOGGER.adapter.debug(f"Querying: {query}")

                    try: 
                        source_cursor.execute(query)
                        rows = source_cursor.fetchall()
                        source_cursor.close()
                    except:
                        rows = []
                    LOGGER.adapter.debug(f"Table has {len(rows)} rows with {len(columns)} columns")

                    cleared_columns = []
                    uncleared_columns = []
                    columns_with_datatypes = []

                    for column in columns:
                                                
                        column_name = column['name'].lower()
                        cleared_column_name = column['name'].replace('-','_').replace(' ','_').replace('#','').lower()

                        datatype = column['datatype']
                        lenght = f'''({column['lenght']})'''
                        
                        if datatype == 'DATETIME':
                            datatype = 'TIMESTAMP'
                        else:
                            datatype = 'character varying'
                            lenght = ''

                        column_with_datatype = f'''{cleared_column_name} {datatype}{lenght}'''

                        if column_with_datatype in columns_with_datatypes:
                            column_with_datatype = f'''{cleared_column_name}_ {datatype}{lenght} NULL'''
                        
                        columns_with_datatypes.append(column_with_datatype)
                        cleared_columns.append(cleared_column_name)

                        if cleared_column_name == column_name:
                            uncleared_columns.append(column_name)

                        else:
                            uncleared_columns.append(f'''"{column_name}" as {cleared_column_name}''')

                    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_with_datatypes)});"
                    LOGGER.adapter.debug(f"Querying: {query}")

                    if 'msy' not in str(table).lower():

                        target_cursor = target.database.connection.cursor()
                        target_cursor.execute(query)
                        target_cursor.close()

                        target_cursor = target.database.connection.cursor()
                        query = f'''TRUNCATE {table_name}'''
                        target_cursor.execute(query)
                        target_cursor.close()
                        
                        for count, row in enumerate(rows):

                            cleared_row = []
                            for value in row:

                                if type(value) in [type(''), type(1)]:
                                    cleared_row.append(value)
                                    pass

                                elif type(value) == type(datetime(2000, 1, 1, 1, 1)):
                                    cleared_row.append(str(value))
                                
                                elif type(value) == type(None):
                                    cleared_row.append(None)

                                elif 'bytearray' in str(value):
                                    s = str(value)
                                    found = s[s.find("(")+3:s.find(")")-1]
                                    arr = bytearray(found, 'utf-8')
                                    cleared_row.append(1)
                                
                                elif str(value) == str(True):
                                    cleared_row.append(True)
                                
                                elif str(value) == str(False):
                                    cleared_row.append(False)

                                else:
                                    cleared_row.append(str(value))

                            # print(cleared_row)
                            row = [f"'{value}'" if value else 'NULL' for value in cleared_row]
                            row = [True if str(value) == str(True) else value for value in row]
                            row = [False if str(value) == str(False) else value for value in row]

                            target_cursor = target.database.connection.cursor()
                            query = f'''INSERT INTO {table_name} ({', '.join(cleared_columns)}) VALUES ({", ".join(row)})'''
                            print(query)
                            LOGGER.adapter.debug(f"Querying: {query}")
                            target_cursor.execute(query)
                            target_cursor.close()
                            print(f"Inserted {count} of {len(rows)} rows in {target.provider}'s {table_name} from {source.provider}'s {table_name}", end="\r")
        
        LOGGER.adapter.debug(f"Waiting to finish runtime...")
                    
        return None

    #  exit function for class basic routine
    def __exit__(self, exc_type, exc_value, traceback):
        self = None
        pass

class DataSourceName(object):

    # init
    def __init__(self,database_type=None):
        '''
            Initiate a Main instance
        '''

        self.database = lambda: None
        self.dsn = lambda: None
        self.error = lambda: None
        self.error.status = True
        self.error.message = None
        self.type = database_type
        self.connection = None
    
    # enter function for class basic rotine
    def __enter__(self):
        '''
            Function for entering class with python 3 standards of
            'with' parameter and a following __exit__ function for
            a cleanner use of the class instancies
        '''
        try:
            return self
        except StopIteration:
           raise RuntimeError("Instance could not be returned")
    
    def parse_dsn(self, source=None):
        
        # dsn lambda function 'variable'
        dsn = lambda: None
        
        try:            
            dsn.engine = source.get('ENGINE', None)
            dsn.name = source.get('NAME', None)
            dsn.user = source.get('USER', None)
            dsn.host = source.get('HOST', None)
            dsn.port = source.get('PORT', None)
            dsn.password = source.get('PASSWORD', None)
        except Exception as e:
            dsn.engine = None
            dsn.name = source

        self.dsn = dsn

    #  exit function for class basic routine
    def __exit__(self, exc_type, exc_value, traceback):
        self = None
        pass

# main class
class Interface(object):
    
    # init
    def __init__(self):
        '''
            Initiate a Main instance
        '''

        self.db = lambda: None
        self.db.ODBC = lambda:'ODBC'
        self.db.ODBC.drivers = lambda:pypyodbc.drivers()
        self.db.ODBC.drivers_count = len(self.db.ODBC.drivers())
        self.db.POSTGRES = lambda:'POSTGRESQL'
        self.db.MYSQL = lambda:'MYSQL'
        self.db.SQLITE = lambda:'SQLITE'
        self.db.ORACLE = lambda:'ORACLE'
        self.db.ALL = lambda:[att for att in dir(self.db) if att not in dir(lambda: None) and att != 'ALL']

    # enter function for class basic rotine
    def __enter__(self):
        '''
            Function for entering class with python 3 standards of
            'with' parameter and a following __exit__ function for
            a cleanner use of the class instancies
        '''
        try:
            return self
        except StopIteration:
           raise RuntimeError("Instance could not be returned")
    
    def database_classifier(self, databases):
        
        classified_databases = {}

        for count, database in enumerate(databases):
            LOGGER.adapter.debug(f"Running classifier function on source {count}...")

            classified_databases[str(database)] = None
            data = lambda: None
            data.database = None
            data.provider = None

            #
            if isinstance(database, pathlib.Path):
                LOGGER.adapter.debug(f"Trying to parse database as {self.db.ODBC()}...")
                connection = self.connect(self.db.ODBC(), database)
                provider = self.db.ODBC()
            else:
                #
                for SQL_DB in self.db.ALL():
                    if SQL_DB != self.db.ODBC():
                        LOGGER.adapter.debug(f"Trying to parse database as {getattr(self.db, SQL_DB)()}...")
                        connection = self.connect(getattr(self.db, SQL_DB)(), database)
                        if connection.error.status == False:
                            provider = getattr(self.db, SQL_DB)()
                            break                
            
            data.database = connection
            connection = None

            data.provider = provider
            provider = None

            classified_databases[str(database)] = data

        return classified_databases

    def parse_as_odbc(self, source=None):

        for count, driver in enumerate(self.db.ODBC.drivers(), 1):
            error_status = False
            self.dsn = f'''Driver={{{driver}}};DBQ={source}'''
    
            LOGGER.adapter.debug(f"Atempt {count} of {self.db.ODBC.drivers_count} to make connection using ODBC driver: {driver}...")

            # temp exception handler until timeout connection fixed
            if count < 8:
                try:
                    connection = pypyodbc.connect(self.dsn)
                    LOGGER.adapter.debug(f"SUCCESS on connection using ODBC driver: {driver}")
                except Exception as e:
                    LOGGER.adapter.debug(f"FAIL on connection using ODBC driver: {driver} due to {e}")
                    connection, error_status = None, True        

            if error_status == False:
                break

        return connection, error_status

    def parse_as_postgresql(self, dsn={}):
        error_status = False

        try:
            connection = psycopg2.connect(
                dbname=dsn.name,
                user=dsn.user,
                host=dsn.host,
                password=dsn.password,
                port=dsn.port,
            )

            # retrieved dsn parameters
            dsn_parameters = connection.get_dsn_parameters()

            LOGGER.adapter.debug(f"SUCCESS on connection using DSN: {dsn_parameters}")
        except Exception as e:
            LOGGER.adapter.debug(f"FAIL on connection using DSN: {dsn} due to {e}")
            connection, error_status = None, True
            
        return connection, error_status
    
    def parse_as_mysql(self, dsn={}):
        return None, True
    
    def parse_as_sqlite(self, dsn={}):
        return None, True

    def parse_as_oracle(self, dsn={}):
        error_status = False

        try:
            connection = cx_Oracle.connect(
                dsn.user,
                dsn.password,
                dsn.name
            )

            pseudo_dsn = f'''{dsn.engine}://{dsn.name}'''
            LOGGER.adapter.debug(f"SUCCESS on connection using DSN: {pseudo_dsn}")
        except Exception as e:
            LOGGER.adapter.debug(f"FAIL on connection using DSN: {pseudo_dsn} due to {e}")
            connection, error_status = None, True

        return connection, error_status

    # function for ...
    def connect(self, database_type, source):

        connection = DataSourceName(database_type)
        connection.parse_dsn(source)

        # ODBC
        if connection.type == self.db.ODBC():
            connection.connection, connection.error.status = self.parse_as_odbc(source)
            
        # POSTGRES
        elif connection.type == self.db.POSTGRES() and connection.dsn.engine.upper() == self.db.POSTGRES():
            pseudo_dsn = f'''{connection.dsn.engine}://{connection.dsn.user}@{connection.dsn.host}:{connection.dsn.port}/{connection.dsn.name}'''
            LOGGER.adapter.debug(f"Atempt to make {self.db.POSTGRES()} connection using DSN: {pseudo_dsn}...")
            connection.connection, connection.error.status = self.parse_as_postgresql(connection.dsn)

        # MYSQL
        elif connection.type == self.db.MYSQL() and connection.dsn.engine.upper() == self.db.MYSQL():
            LOGGER.adapter.debug(f"Connections with {self.db.MYSQL()} to be available in future release")
            connection.connection, connection.error.status = self.parse_as_mysql(connection.dsn)

        # SQLITE
        elif connection.type == self.db.SQLITE() and connection.dsn.engine.upper() == self.db.SQLITE():
            LOGGER.adapter.debug(f"Connections with {self.db.SQLITE()} to be available in future release")
            connection.connection, connection.error.status = self.parse_as_sqlite(connection.dsn)

        # ORACLE
        elif connection.type == self.db.ORACLE() and connection.dsn.engine.upper() == self.db.ORACLE():
            pseudo_dsn = f'''{connection.dsn.engine}://{connection.dsn.name}'''
            LOGGER.adapter.debug(f"Atempt to make {self.db.ORACLE()} connection using DSN: {pseudo_dsn}...")
            connection.connection, connection.error.status = self.parse_as_oracle(connection.dsn)
            
        # RETURN
        return connection
    
    #  exit function for class basic routine
    def __exit__(self, exc_type, exc_value, traceback):
        pass

# paths argument parser
class Validity(object):

    # path validity init
    def __init__(self):
        ''' 
            Initiate a Path Validity instance.
        '''

        # get loggert on a self instance
        self.logger = logger.adapter
        
    # path validity checker function
    def path_check(self, files):
        '''
            Function to check if each parsed path is a valid system file
            and if it can be accessed by the code.

            Arguments:
                paths: array of files to be checked
        '''

        # set basic variable for valid files
        valid_files = []

        # loop check through parsed path
        self.logger.debug('Checking validity of inputed sources')
        for analysed_file in files:

            # append path if it exists, is accessible and is a file
            if (
                os.access(analysed_file, os.F_OK) and 
                os.access(analysed_file, os.R_OK) and 
                os.path.isfile(analysed_file)
            ):
                if DEBUG:
                    output = f"Source path {analysed_file} was successfully parsed"
                    # log output
                    self.logger.debug(output)

                # append valid file to array
                valid_files.append(analysed_file)

            # if not, log the error
            else:
                if DEBUG:
                    output = f"Source path {analysed_file} could not be accessed as a file"
                    # log output
                    self.logger.debug(output)
        
        # return all parsed valid files
        return valid_files

# class for logger instancies and configurations
class Logger(object):

    # path validity init
    def __init__(self):
        ''' 
            Initiate a Logger instance.
            Argument:
                logger: a logging instance for output and log
        '''

        self.folder = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                '../log/' 
            )
        )

        # check if log folder exists
        if not os.path.exists(self.folder):
            try:
                os.makedirs(self.folder)
            except Exception  as e:
                raise ValueError(f"Log folder: {self.folder} could not be created, error: {e}")
                sys.exit()

        formatter = logging.Formatter(
            '%(asctime)-8s %(levelname)-5s [%(project)s-%(version)s] user: %(user)s LOG: %(message)s'
        )

        adapter = logging.getLogger(f"{__project__}-{__version__}")

        if not len(adapter.handlers):
            adapter.setLevel('INFO')
            if DEBUG == True:
                adapter.setLevel('DEBUG')

            # setup of file handler
            file_handler = logging.FileHandler(f"{self.folder}/{__project__}.log")     
            file_handler.setFormatter(formatter)

            # setup of stream handler
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)

            # add handler to the logger
            adapter.addHandler(file_handler)
            adapter.addHandler(stream_handler)

        # update logger to receive formatter within extra data
        self.adapter = logging.LoggerAdapter(
            adapter, 
            extra = {
                'project':  __project__,
                'version':  __version__,
                'user':     getpass.getuser()
            }
        )
    
    # enter function for class basic rotine
    def __enter__(self):
        '''
            Function for entering class with python 3 standards of
            'with' parameter and a following __exit__ function for
            a cleanner use of the class instancies
        '''
        try:
            return self
        except StopIteration:
           raise RuntimeError("Instance could not be returned")

    def __exit__(self, exc_type, exc_value, traceback):
        LOGGER = None
        self = None

# command line argument parser
def args(args):
    '''
        Main function for terminal call of library
        Arguments:
            args: receive all passed arguments and filter them using
                the argparser library
    '''

    # argparser init
    parser = argparse.ArgumentParser(description=short_description)

    # prevent follow and lines flag to be setted at the same time
    # group = parser.add_mutually_exclusive_group(required=False)

    # path argument parser
    parser.add_argument(
        'sources',
        nargs='+',
        help='Microsoft Access .mdb and .accdb files paths', 
        default=[]
    )

    parser.add_argument(
        'target',
        nargs='+',
        help='connection parameters of target SQL database', 
        default={}
    )

    # debug flag argument parser
    parser.add_argument(
        '-d','--debug',
        action='store_true', 
        help='enable debug log',
        default=False,
        required=False
    )

    # version output argument parser
    parser.add_argument(
        '-v','--version',
        action='version',
        help='output software version',
        default=False,
        version=(__project__+"-"+__version__)
    )

    # passing filtered arguments as array
    args = parser.parse_args(args)
    
    # call --
    interface(
        debug=args.debug,
        sources=args.sources,
        target=args.target
    )

# function to -
def connect(debug=False, databases=[]):

    global DEBUG
    DEBUG = debug

    global LOGGER
    
    with Logger() as logger:
        LOGGER = logger
        
        # 
        LOGGER.adapter.info(f"DEBUG flags was setted as: {DEBUG}")
        LOGGER.adapter.info(f"An application transaction was created due to command or module call...")
        LOGGER.adapter.info(f"Log file is being stored at directory: {logger.folder}")

        #
        LOGGER.adapter.info(f"Begining database classifier instance...")
        LOGGER.adapter.info(f"Instance found {len(databases)} sources to be parsed as database")
        interface = Interface()

        #
        output = ""
        for count, database in enumerate(databases, 1):
            output += f"\t{count}: {database}\n"

        #
        LOGGER.adapter.info(f'''SOURCES = [\n\r{output}]''')
        dbs = interface.database_classifier(databases)

        return dbs

# run function on command call
if __name__ == "__main__":
    args(sys.argv[1:])
# end of code