import json
import time
import pandas as pd
from sqlalchemy import engine as sql

from data_info import getDF

def averageSalary(vacancy):
    # eng = sql.create_engine('postgresql://postgres:root@127.0.0.1:5432/hh_bot')
    # conn = eng.connect()

    # sql_req = f'select salarys from public."{vacancy}"'
    # salary = pd.read_sql(sql_req, conn)
    # conn.close()
    command = f'select salarys from public."{vacancy}"'
    df = getDF(command)

    sum_sal = 0
    n = 0
    n_o = 0
    for sal in df['salarys']:
        if sal > 0:
            sum_sal += sal
            n += 1

    return [sum_sal//n, n, len(df)]
