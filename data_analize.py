import pandas as pd
import matplotlib.pyplot as plt

from data_info import getDF


def experienceRate(vacancy) -> tuple:
    df = getDF(f'''
        SELECT experience AS labels,
            COUNT(*) AS count,
            (SELECT COUNT(*) FROM public."{vacancy}") AS length
        FROM public."{vacancy}"
        GROUP BY experience
    ''')

    fig, ax = plt.subplots()
    ax.pie(df['count'], labels=df['labels'], autopct='%1.1f%%', pctdistance=0.7, wedgeprops=dict(width=0.5))

    res = ('graph.png', df['length'][0])
    fig.savefig(res[0], dpi=200, bbox_inches='tight')
    return res


def averageSalary(vacancy) -> tuple:
    df = getDF(f'''
        SELECT experience,
            ROUND(AVG(salaries)) AS salaries,
            COUNT(*) AS count,
            (SELECT COUNT(*) FROM public."{vacancy}") AS length
        FROM public."{vacancy}"
        WHERE salaries <> 0
        GROUP BY experience
        ORDER BY
            CASE
                WHEN experience='Нет опыта' THEN 1
                WHEN experience='От 1 года до 3 лет' THEN 2
                WHEN experience='От 3 до 6 лет' THEN 3
                WHEN experience='Более 6 лет' THEN 4
            END;
    ''')

    if df.empty:
        raise Exception('Зарпалата не указана ни в одной вакансии')

    if len(df) == 1:
        res = ('No graph', round(sum(df['salaries'])/len(df)), sum(df['count']), df['length'][0])
        return res

    res = ('graph.png', round(sum(df['salaries'])/len(df)), sum(df['count']), df['length'][0])
    fig, ax = plt.subplots()
    ax.plot(df['experience'], df['salaries'])
    plt.ylabel("Зарпалата в рублях")
    fig.savefig(res[0], dpi=200, bbox_inches='tight')
    return res


def headSkills(vacancy) -> tuple:
    df = getDF(f'SELECT key_skills FROM public."{vacancy}"')

    length = len(df)

    skills = []
    for key_skills in df['key_skills']:
        for skill in key_skills.split(', '):
            if skill:
                skills.append(skill)

    df = pd.DataFrame(skills)
    count = df[0].value_counts()

    res = ('graph.png', count.head(3).keys(), length)

    head = count.head(20)[::-1]

    fig, ax = plt.subplots()
    ax.barh(head.keys(), head.values)
    fig.set_figwidth(10)
    fig.set_figheight(10)
    plt.xlabel("Упоминания")
    fig.savefig(res[0], dpi=200, bbox_inches='tight')
    return res
