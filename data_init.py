import json
import requests
import time
import re

def clearHtml(raw_html):
    mr_proper = re.compile('<.*?>')
    clean_text = re.sub(mr_proper, '', raw_html)
    return clean_text

def getMoreData(url):
    req = requests.get(url)
    data = json.loads(req.content.decode())
    req.close()
    time.sleep(0.25)
    return data

def getData(vacancy):
    name = []
    salarys = []
    employer = []
    alternate_url = []
    url = []
    experience = []
    key_skills = []
    description = []

    ue = 70

    for page in range(10):
        params = {
            'text': f'NAME:{vacancy}',
            'area': 1,
            'page': page,
            'per_page': 100
        }
        req = requests.get('https://api.hh.ru/vacancies', params)
        item = json.loads(req.content.decode())

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

            name.append(data['name'])
            salarys.append(salary)
            employer.append(data['employer']['name'])
            alternate_url.append(data['alternate_url'])
            url.append(data['url'])
            experience.append(data_vacancy['experience']['name'])
            key_skills.append(skills)
            description.append(clearHtml(data_vacancy['description']))

        req.close()
        if (data['pages'] - page) <= 1:
            break
        time.sleep(0.25)


    df = pd.DataFrame({
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
    #print(df)
    df.to_csv('python_developer.csv', encoding='utf-8', index=False)
    return(df)
