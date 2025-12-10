from mysql.connector import connect, ProgrammingError
from modulos import logger
from contextlib import contextmanager
from sqlalchemy import create_engine
from modulos.logger_config import logging
import pandas as pd

global paramts_connect

# def connect_params(**kwargs):
#     return dict(
#         host='172.18.150.36',
#         port=3306,
#         user='invent',
#         passwd='Invent@4321',
#         database='inventario',
#     )

def connect_params(**kwargs):
    paramts_connect =  dict(
        host='192.168.0.123',
        port=3306,
        user='Guilherme',
        passwd='Crhono12#',
        database='GoBook',
    )
    
    paramts_connect.update(kwargs)

    return paramts_connect

@contextmanager
def new_connect():
    conexao = connect(**connect_params())
    try:
        yield conexao
    finally:
        if (conexao and conexao.is_connected()):
            conexao.close()


@contextmanager
def engine_sql():
    paramts_connect = connect_params()
    url_connect = f"mysql+mysqlconnector://{paramts_connect['user']}:{paramts_connect['passwd'].replace('@','%40')}@{paramts_connect['host']}/{paramts_connect['database']}"
    try:
        engine = create_engine(url_connect)
        connect_sql = engine.connect()
        yield connect_sql
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")

    finally:
        if (connect_sql and not connect_sql.closed):
            connect_sql.close()


def connect_execute(command, *args):
    with new_connect() as connect:
        try:
            cursor = connect.cursor()
            cursor.execute(command, args)
            connect.commit()
            last_id = cursor.lastrowid
            return last_id
        except ProgrammingError as e:
            logger.error(f'Erro: {e.msg}')


def connect_consulta(command, *args, dictonary=False,):
    with new_connect() as connect:
        try:
            cursor = connect.cursor(dictionary=dictonary)
            cursor.execute(command, args)
            return cursor.fetchall()
        except ProgrammingError as e:
            print(f'Erro: {e.msg}')


def delete_table(table):
    # Ativar database
    connect_params()
    delete_table = f'DROP TABLE IF EXISTS {table}'
    connect_execute(delete_table)


def read_table_df(table='etiquetas'):
    # Ativando database
    connect_params()
    # Ativando comando
    with engine_sql() as engine:
        df = pd.read_sql_table(f'{table}', con=engine)
        return df


def atualizar_table(df, table, if_exists='append', edit='yes'):
    from sqlalchemy import create_engine
    from sqlalchemy.exc import SQLAlchemyError
    from sqlalchemy.orm import sessionmaker

    try:
        # Gerando Engine
        url = f"mysql+mysqlconnector://{paramts_connect['user']}:{paramts_connect['passwd'].replace('@','%40')}@{paramts_connect['host']}/{paramts_connect['database']}"
        connect = create_engine(url)

        # Inicie uma nova sessão
        Session = sessionmaker(bind=connect)
        session = Session()

        with connect.begin() as con:
            df.to_sql(table, con, if_exists=if_exists, index=False)

            # Commit da transação
            session.commit()

        return True
    except SQLAlchemyError as e:
        logging.error(f'Erro em atualizar; {e}')
        session.rollback()

        return False

    finally:
        # Feche a sessão, se existir
        if 'session' in locals():
            session.close()


def listar_table():
    table_list = []
    connect_params()
    with new_connect() as conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute('SHOW TABLES')
            for i, table in enumerate(cursor, start=1):
                table_list.append(table[0])
            return table_list

        except ProgrammingError as e:
            print(f'erro: {e.msg}')


def listar_database():
    database_list = []
    with new_connect() as conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute('SHOW DATABASES')
            for i, table in enumerate(cursor, start=1):
                database_list.append(table[0])
            return database_list

        except ProgrammingError as e:
            print(f'erro: {e.msg}')

paramts_connect = connect_params()



def creat_database(name):
    connect_params()
    database = 'CREATE DATABASE IF NOT EXISTS %s'
    connect_execute(database,name)