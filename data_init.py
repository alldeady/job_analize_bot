import json
import requests
import time
import pandas as pd
import re
from sqlalchemy import engine as sql

def sendMessage(message, chat_id, bot):
    bot.send_message(chat_id, f'{message}')

def clearHtml(raw_html):
    mr_proper = re.compile('<.*?>')
    clean_text = re.sub(mr_proper, '', raw_html)
    return clean_text

def getMoreData(url):
    req = requests.get(url)
    data = json.loads(req.content.decode())
    req.close()
    time.sleep(0.2)
    return data

def getData(vacancy, chat_id, bot):
    vac_id = []
    name = []
    salarys = []
    employer = []
    alternate_url = []
    url = []
    experience = []
    key_skills = []
    description = []

    ue = 70

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
        time.sleep(0.2)

        for data in item['items']:
            data_vacancy = getMoreData(data['url'])

            skills = []
            for skill in data_vacancy['key_skills']:
                skills += [skill['name']]

            salary = 0
            if data['salary'] != None:
                if data['salary']['from'] != None:
                    salary = data['salary']['from']
                elif data['salary']['to'] != None:
                    salary = data['salary']['to']
                if data['salary']['currency'] != 'RUR':
                    salary *= ue

            vac_id.append(data_vacancy['id'])
            name.append(data['name'])
            salarys.append(salary)
            employer.append(data['employer']['name'])
            alternate_url.append(data['alternate_url'])
            url.append(data['url'])
            experience.append(data_vacancy['experience']['name'])
            key_skills.append(skills)
            description.append(clearHtml(data_vacancy['description']))

        num_vac = len(vac_id)
        sendMessage(f'Вакансий собрано: {num_vac}', chat_id, bot)

        if (item['pages'] - page) <= 1:
            break

    if num_vac == 0:
        return # do raise exception

    df = pd.DataFrame({
        'vac_id': vac_id,
        'request': vacancy,
        'names': name,
        'salarys': salarys,
        'employers': employer,
        'alternate_urls': alternate_url,
        'urls': url,
        'experience': experience,
        'key_skills': key_skills,
        'descriptions': description
    })

    eng = sql.create_engine('postgresql://postgres:root@postgres:5432/hh_bot')
    conn = eng.connect()

    df.to_sql(f'{vacancy}', conn, schema='public', if_exists='replace', index=False)
    conn.close()

