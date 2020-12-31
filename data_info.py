import json
import pandas as pd
from sqlalchemy import engine as sql
import os
import re

def getDF(command):
    eng = sql.create_engine('postgresql://postgres:root@127.0.0.1:5432/hh_bot')
    conn = eng.connect()

    sql_req = f'{command}'
    df = pd.read_sql(sql_req, conn)
    conn.close()

    return df

def getTableNames():
    command = """
            SELECT * FROM information_schema.tables
            WHERE table_schema = 'public'
            """
    df = getDF(command)

    names = ''
    for table_name in df['table_name']:
        names += table_name + '\n'

    return names

def getCSV(command):
    df = getDF(command)

    file_name ='data_set.csv'
    df.to_csv(f'{file_name}', encoding='utf-8', index=False)

    return file_name

def clearStr(raw_str):
    mr_proper = re.compile('[{}"]')
    clean_text = re.sub(mr_proper, '', raw_str)
    return clean_text

def getVacancies(db_name, start=0, end=10):
    df = getDF(f'select * from public."{db_name}"')
    text = ''

    for i in range(start, end + 1):
        text += '*' + df['names'][i] + '*\n' +\
                '_Зарплата:_ ' + str(df['salarys'][i]) + '\n' +\
                '_Опыт:_ ' + df['experience'][i] + '\n' +\
                '_Компания:_ ' + df['employers'][i] + '\n' +\
                '_Навыки:_ ' + clearStr(df['key_skills'][i]).replace(',', ', ') + '\n' +\
                df['alternate_urls'][i] + '\n\n'

    return text
