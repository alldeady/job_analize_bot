import json
import time
import pandas as pd
from sqlalchemy import engine as sql
import matplotlib.pyplot as plt

from data_info import getDF

def averageSalary(vacancy):
    command = f'select * from public."{vacancy}"'
    df = getDF(command)
    summ = [0, 0, 0, 0]
    n = [0, 0, 0, 0]
    exp = ['Нет опыта', 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет']

    for i in range(len(df)):
        if df['experience'][i] == exp[0]:
            if df['salarys'][i] > 0 :
                summ[0] += df['salarys'][i]
                n[0] += 1
        elif df['experience'][i] == exp[1]:
            if df['salarys'][i] > 0:
                summ[1] += df['salarys'][i]
                n[1] += 1
        elif df['experience'][i] == exp[2]:
            if df['salarys'][i] > 0:
                summ[2] += df['salarys'][i]
                n[2] += 1
        elif df['experience'][i] == exp[3]:
            if df['salarys'][i] > 0:
                summ[3] += df['salarys'][i]
                n[3] += 1

    # if n[0] == 0:
    #     n[0] = 1
    # if n[1] == 0:
    #     n[1] = 1
    # if n[2] == 0:
    #     n[2] = 1
    # if n[3] == 0:
    #     n[3] = 1

    # if summ[0] == 0:
    #     summ[0] = 1
    # if summ[1] == 0:
    #     summ[1] = 1
    # if summ[2] == 0:
    #     summ[2] = 1
    # if summ[3] == 0:
    #     summ[3] = 1

    av_n = n[0] + n[1] + n[2] + n[3]
    av_summ = (summ[0] + summ[1] + summ[2] + summ[3]) // av_n
    summ = [summ[0]//n[0], summ[1]//n[1], summ[2]//n[2], summ[3]//n[3]]
    res = ['graph.png', av_summ, av_n, len(df)]

    fig, ax = plt.subplots()
    ax.plot(summ, exp)
    fig.savefig(res[0])

    return (res)
