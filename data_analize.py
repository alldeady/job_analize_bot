import json
import pandas as pd
from sqlalchemy import engine as sql
import matplotlib.pyplot as plt

from data_info import getDF

def experienceRate(vacancy):
    df = getDF(f'select experience from public."{vacancy}"')

    labels = ['Нет опыта', 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет']
    count = [0, 0, 0, 0]

    for exp in df['experience']:
        if exp == labels[0]:
            count[0] += 1
        elif exp == labels[1]:
            count[1] += 1
        elif exp == labels[2]:
            count[2] += 1
        elif exp == labels[3]:
            count[3] += 1

    fig, ax = plt.subplots()
    ax.pie(count, labels=labels, autopct='%1.1f%%', pctdistance=0.7, wedgeprops=dict(width=0.5))

    res = ['graph.png', len(df)]
    fig.savefig(res[0], dpi=200, bbox_inches='tight')

    return res

def averageSalary(vacancy):
    df = getDF(f'select salaries, experience from public."{vacancy}"')
    summ = [0, 0, 0, 0]
    n = [0, 0, 0, 0]
    exp = ['Нет опыта', 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет']

    for i in range(len(df)):
        if df['experience'][i] == exp[0]:
            if df['salaries'][i] > 0 :
                summ[0] += df['salaries'][i]
                n[0] += 1
        elif df['experience'][i] == exp[1]:
            if df['salaries'][i] > 0:
                summ[1] += df['salaries'][i]
                n[1] += 1
        elif df['experience'][i] == exp[2]:
            if df['salaries'][i] > 0:
                summ[2] += df['salaries'][i]
                n[2] += 1
        elif df['experience'][i] == exp[3]:
            if df['salaries'][i] > 0:
                summ[3] += df['salaries'][i]
                n[3] += 1

    # raise exception division by zero

    av_n = n[0] + n[1] + n[2] + n[3]
    av_summ = (summ[0] + summ[1] + summ[2] + summ[3]) // av_n
    summ = [summ[0]//n[0], summ[1]//n[1], summ[2]//n[2], summ[3]//n[3]]
    res = ['graph.png', av_summ, av_n, len(df)]

    fig, ax = plt.subplots()
    ax.plot(exp, summ)
    plt.ylabel("Зарпалата в рублях")
    fig.savefig(res[0], dpi=200, bbox_inches='tight')

    return res

def headSkills(vacancy):
    df = getDF(f'select key_skills from public."{vacancy}"')

    lenght = len(df)

    skills = []
    for key_skills in df['key_skills']:
        for skill in key_skills.split(', '):
            if skill:
                skills.append(skill)

    df = pd.DataFrame(skills)
    count = df[0].value_counts()

    res = ['graph.png', count.head(3).keys(), lenght]

    head = count.head(20)[::-1]

    fig, ax = plt.subplots()
    ax.barh(head.keys(), head.values)
    fig.set_figwidth(10)
    fig.set_figheight(10)
    plt.xlabel("Упоминания")

    fig.savefig(res[0], dpi=200, bbox_inches='tight')

    return res
