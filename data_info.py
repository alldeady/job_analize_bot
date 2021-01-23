import pandas as pd
from sqlalchemy import engine as sql

from config import DB


def getDF(command):
    eng = sql.create_engine(DB)
    conn = eng.connect()

    df = pd.read_sql(command, conn)
    conn.close()
    return df


def getTablesNames() -> tuple:
    command = """
            SELECT * FROM information_schema.tables
            WHERE table_schema = 'public'
            """
    df = getDF(command)

    names = []
    for table_name in df['table_name']:
        if table_name != 'statistics' and table_name != 'errors':
            names.append(table_name)
    return tuple(names)


def getCSV(command) -> str:
    df = getDF(command)

    file_name ='data_set.csv'
    df.to_csv(file_name, encoding='utf-8', index=False)
    return file_name


def getVacancies(vacancy, start=0, end=5) -> str:
    df = getDF(f'SELECT * FROM public."{vacancy}"')
    text = ''

    for i in range(start, end):
        if i >= len(df):
            break

        if df['salaries'][i] == 0:
            salary = 'Не указана'
        else:
            salary = str(df['salaries'][i])

        text += '<b>' + str(i + 1) + '. ' + df['names'][i] + '</b>\n' \
                '<code>Зарплата:</code> ' + salary + '\n' \
                '<code>Компания:</code> ' + df['employers'][i] + '\n' \
                '<code>Опыт:</code> ' + df['experience'][i] + '\n' \
                '<code>Навыки:</code> ' + df['key_skills'][i] + '\n' \
                '<code>Требования:</code> ' + df['requirement'][i] + '\n' \
                '<code>Обязанности:</code> ' + df['responsibility'][i] + '\n' + \
                df['alternate_urls'][i][8::] + '\n\n'
    return text
