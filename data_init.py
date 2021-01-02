import re
import json
import requests
import pandas as pd
from sqlalchemy import engine as sql
from time import gmtime, strftime, sleep

from config import DB, UE

def sendMessage(message, chat_id, bot):
    bot.send_message(chat_id, message)

def clearHtml(raw_html):
    mr_proper = re.compile('<.*?>')
    clean_text = re.sub(mr_proper, '', raw_html)
    return clean_text

def getMoreData(url):
    req = requests.get(url)
    data = json.loads(req.content.decode())
    req.close()
    sleep(0.2)
    return data

def toSQL(df, table_name, if_exists='replace'):
    eng = sql.create_engine(DB)
    conn = eng.connect()

    df.to_sql(table_name, conn, schema='public', if_exists=if_exists, index=False)
    conn.close()

def updateStatistics(chat_id, first_name, request):
    df = pd.DataFrame({
        'chat_id': chat_id,
        'first_name': first_name,
        'time': strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),
        'requests': request
    }, index=[0])
    toSQL(df, 'statistics', if_exists='append')

def getData(vacancy, chat_id, bot):
    name = []
    salaries = []
    employer = []
    alternate_url = []
    url = []
    experience = []
    key_skills = []
    description = []
    requirement = []
    responsibility = []

    for page in range(100):
        params = {
            'text': f'NAME:{vacancy}',
            'area': 1,
            'page': page,
            'per_page': 100
        }
        req = requests.get('https://api.hh.ru/vacancies', params)
        item = json.loads(req.content.decode())
        req.close()
        sleep(0.2)

        for data in item['items']:
            data_vacancy = getMoreData(data['url'])

            skills = ''
            for skill in data_vacancy['key_skills']:
                skills += skill['name'] + ', '

            salary = 0
            if data['salary'] != None:
                if data['salary']['from'] != None:
                    salary = data['salary']['from']
                elif data['salary']['to'] != None:
                    salary = data['salary']['to']
                if data['salary']['currency'] != 'RUR':
                    salary *= UE

            name.append(data['name'])
            salaries.append(salary)
            employer.append(data['employer']['name'])
            alternate_url.append(data['alternate_url'])
            url.append(data['url'])
            experience.append(data_vacancy['experience']['name'])
            key_skills.append(skills[:-2])
            description.append(clearHtml(data_vacancy['description']))
            requirement.append(clearHtml(str(data['snippet']['requirement'])))
            responsibility.append(clearHtml(str(data['snippet']['responsibility'])))

        count_vac = len(salaries)
        sendMessage(f'Вакансий собрано: {count_vac}', chat_id, bot)

        if (item['pages'] - page) <= 1:
            break

    if count_vac == 0:
        return # do raise exception

    df = pd.DataFrame({
        'request': vacancy,
        'names': name,
        'salaries': salaries,
        'employers': employer,
        'alternate_urls': alternate_url,
        'urls': url,
        'experience': experience,
        'key_skills': key_skills,
        'descriptions': description,
        'requirement': requirement,
        'responsibility': responsibility
    })

    toSQL(df, vacancy)
