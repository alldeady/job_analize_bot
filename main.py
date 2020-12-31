import requests
import telebot
import logging
import os

import config
import data_init as init
import data_analize as analize
import data_info as info


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

bot = telebot.TeleBot(config.TOKEN, parse_mode='MARKDOWN')

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, 'Привет! Смотри, что я умею /help')

@bot.message_handler(commands=['help'])
def help(message):
    text = '*Я могу скачивать вакансии с hh.ru, а затем творить с ними всякие непотребства*\n\n' +\
        'Скачать или обновить вакансии в базе данных: _вакансия(в, v) <название вакансии>_\n' +\
        'Запросы дело не быстрое, так что придётся недолго подождать или долго, если ищещь джаву\n\n' +\
        'Список уже скачанных вакансий: _/db_\n\n' +\
        'Для работы следующих команд вакансия должна находиться в базе данных\n\n' +\
        'Средняя зарплата: _зп(zp) <название вакансии>_\n' +\
        'Скачать таблицу в csv: _скачать(с, d) <название вакансии>_\n' +\
        'Показать вакансии: показать(п, p) _<название вакансии>_\n' +\
        '\nP.S.: Пока что ищу только в default city\n' +\
        'P.S.s.: Ожидаю добавление поддержки заданий от фиксеров\n'
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['db'])
def bd_names(message):
    names = info.getTableNames()
    bot.send_message(message.chat.id, f'{names}')

@bot.message_handler(content_types=['text'])
def parser(message):
    msg = message.text.lower().split()
    vacancy = ' '.join(msg[1:])

    if msg[0] == 'вакансия' or msg[0] == 'v' or msg[0] == 'в':
        try:
            bot.send_message(message.chat.id, 'Это может занять некторое время')
            init.getData(vacancy, message.chat.id, bot)
            bot.send_message(message.chat.id, 'Данные по вакансии доступны к анализу')
        except Exception as e:
            bot.send_message(message.chat.id, 'Что-то пошло не так :с')
            bot.send_message(message.chat.id, f'{e}')

    elif msg[0] == 'sql':
        try:
            doc_name = info.getCSV(command=vacancy)
            doc = open(f'{doc_name}', 'rb')
            bot.send_document(message.chat.id, doc)
            doc.close()
            if os.path.isfile(f'{doc_name}'):
                os.remove(f'{doc_name}')
        except Exception as e:
            bot.send_message(message.chat.id, f'{e}')

    elif msg[0] == 'скачать' or msg[0] == 'с' or msg[0] == 'd':
        try:
            command = f'select * from public."{vacancy}"'
            doc_name = info.getCSV(command)
            doc = open(f'{doc_name}', 'rb')
            bot.send_document(message.chat.id, doc)
            doc.close()
            if os.path.isfile(f'{doc_name}'):
                os.remove(f'{doc_name}')
        except Exception as e:
            bot.send_message(message.chat.id, f'{e}')

    elif msg[0] == 'показать' or msg[0] == 'п' or msg[0] == 'p':
        try:
            text = info.getVacancies(vacancy)
            bot.send_message(message.chat.id, f'{text}')
        except Exception as e:
            bot.send_message(message.chat.id, f'{e}')

    elif msg[0] == 'зарплата' or msg[0] == 'zp' or msg[0] == 'зп':
        try:
            res = analize.averageSalary(vacancy)
            photo = open(f'{res[0]}', 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()

            text = f'{res[1]} - средняя зарплата вакансии {vacancy}\n' +\
                    f'Из {res[3]} вакансий зарплата указана только в {res[2]}'
            bot.send_message(message.chat.id, text)
            if os.path.isfile(f'{res[0]}'):
                os.remove(f'{res[0]}')
        except Exception as e:
            bot.send_message(message.chat.id, f'{e}')

    else:
        bot.send_message(message.chat.id, 'Чекни команды в /help')

#run
if __name__ == "__main__":
    bot.polling(none_stop=True)
