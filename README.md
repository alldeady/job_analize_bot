### Telegram bot for search and analysis job [@job_analize_bot](t.me/job_analize_bot)

### Bot abilities
* Bot can take a list of vacancies from hh.ru and write it to data base
* After that, build several graphs based on the received data
* And show vacancies, ofc
* You can check all available commands with small guide: ```'/help'```
* Check all downloaded vacancies: ```'/db'```
* All commands have same syntax: ```'<command> <vacancy name>'```
* You can download any vacancy table as .csv file: ```'скачать <vacancy name>'```
* You can use direct SQL queries of any complexity: ```'sql <sql query>'```, bot will execute it and send .csv

### For run bot you need:
* Create ```config.py``` which contains:
```
TOKEN = '<token from @botfather>'
UE = '<USD exchange rate in RUR>'
DB = 'postgresql://postgres:root@0.0.0.0:5432/hh_bot' # for SQLAlchemy
```

* Install docker if not yet: https://docs.docker.com/engine/install/

* Build:
```sudo docker-compose up --build``` or smth similar for your os

### Some info
* Bot worked with PostgreSQL
* Right now based on AWS
