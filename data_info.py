import json
import pandas as pd
from sqlalchemy import engine as sql

from config import DB

def getDF(command):
    eng = sql.create_engine(DB)
    conn = eng.connect()

    df = pd.read_sql(command, conn)
    conn.close()

    return df

def getTablesNames():
    command = """
            SELECT * FROM information_schema.tables
            WHERE table_schema = 'public'
            """
    df = getDF(command)

    names = ''
    for table_name in df['table_name']:
        if table_name != 'statistics':
            names += table_name + '\n'

    return names

def getCSV(command):
    df = getDF(command)

    file_name ='data_set.csv'
    df.to_csv(file_name, encoding='utf-8', index=False)

    return file_name

def getVacancies(db_name, start=0, end=5):
    df = getDF(f'select * from public."{db_name}"')
    text = ''

    for i in range(start, end + 1):
        if i >= len(df):
            break

        if df['salaries'][i] == 0:
            salary = 'Не указана'
        else:
            salary = str(df['salaries'][i])

        text += '*' + df['names'][i] + '*\n' \
                '_Зарплата:_ ' + salary + '\n' \
                '_Компания:_ ' + df['employers'][i] + '\n' \
                '_Опыт:_ ' + df['experience'][i] + '\n' \
                '_Навыки:_ ' + df['key_skills'][i] + '\n' \
                '_Требования:_ ' + df['requirement'][i] + '\n' \
                '_Обязанности:_ ' + df['responsibility'][i] + '\n' + \
                df['alternate_urls'][i] + '\n\n'

    return text
