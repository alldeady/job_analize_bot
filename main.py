import requests
import telebot
import logging
import os

from config import TOKEN
import data_init as init
import data_analize as analize
import data_info as info


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

bot = telebot.TeleBot(TOKEN, parse_mode='MARKDOWN')

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, 'Привет! Смотри, что я умею /help')

@bot.message_handler(commands=['help'])
def help(message):
    text = '*Я могу скачивать вакансии с hh.ru, а затем творить с ними всякие непотребства*\n\n' \
        '*Пример запроса: _зп data scientist_*\n\n' \
        'Скачать или обновить вакансии в базе данных: _вакансия, в, v <название вакансии>_\n' \
        'Запросы дело не быстрое, так что придётся недолго подождать или долго, если ищещь джаву\n\n' \
        'Список вакансий в базе данных: _/db_\n\n' \
        'Для работы следующих команд вакансия должна находиться в базе данных\n' \
        'Показать вакансии: _показать, п, p <название вакансии>_\n' \
        'Средняя зарплата: _зарплата, зп, zp <название вакансии>_\n' \
        'Популярные навыки: _навыки, н, n <название вакансии>_\n' \
        'Распределение опыта: _опыт, о, o <название вакансии>_\n' \
        'Скачать таблицу в csv: _скачать, с, c <название вакансии>_\n' \
        '\nP.S.: Пока что ищу только в default city\n' \
        'P.S.s.: Ожидаю добавление поддержки заданий от фиксеров\n'
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['db'])
def bd_names(message):
    names = info.getTableNames()
    if names == '':
        bot.send_message(message.chat.id, 'Список вакансий пуст. /help')
    else:
        bot.send_message(message.chat.id, f'Доступны вакансии по запрасам:\n{names}')

@bot.message_handler(content_types=['text'])
def parser(message):
    init.updateStatistics(message.chat.id, message.chat.first_name, message.text)
    msg = message.text.lower().split()
    vacancy = ' '.join(msg[1:])

    if msg[0] == 'вакансия' or msg[0] == 'Вакансия' \
                        or msg[0] == 'в' or msg[0] == 'В' \
                        or msg[0] == 'v' or msg[0] == 'V':
        try:
            bot.send_message(message.chat.id, 'Это может занять некторое время')
            init.getData(vacancy, message.chat.id, bot)
            bot.send_message(message.chat.id, 'Данные по вакансии доступны к анализу')
        except Exception as e:
            bot.send_message(message.chat.id, 'Что-то пошло не так :с')
            bot.send_message(message.chat.id, e)

    elif msg[0] == 'sql':
        try:
            doc_name = info.getCSV(command=vacancy)
            doc = open(doc_name, 'rb')
            bot.send_document(message.chat.id, doc)
            doc.close()
            if os.path.isfile(doc_name):
                os.remove(doc_name)
        except Exception as e:
            bot.send_message(message.chat.id, e)

    elif msg[0] == 'скачать' or msg[0] == 'Скачать' \
                        or msg[0] == 'с' or msg[0] == 'С' \
                        or msg[0] == 'c' or msg[0] == 'C':
        try:
            doc_name = info.getCSV(f'select * from public."{vacancy}"')
            doc = open(doc_name, 'rb')
            bot.send_document(message.chat.id, doc)
            doc.close()
            if os.path.isfile(doc_name):
                os.remove(doc_name)
        except Exception as e:
            bot.send_message(message.chat.id, e)

    elif msg[0] == 'показать' or msg[0] == 'Показать' \
                        or msg[0] == 'п' or msg[0] == 'П' \
                        or msg[0] == 'p'  or msg[0] == 'P':
        try:
            text = info.getVacancies(vacancy)
            bot.send_message(message.chat.id, text)
        except Exception as e:
            bot.send_message(message.chat.id, e)

    elif msg[0] == 'зарплата' or msg[0] == 'Зарплата'\
                            or msg[0] == 'зп'  or msg[0] == 'Зп'\
                            or msg[0] == 'zp' or msg[0] == 'Zp':
        try:
            res = analize.averageSalary(vacancy)
            photo = open(res[0], 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()

            text = f'*{res[1]}* - средняя зарплата по запросу {vacancy}\n' \
                    f'Из {res[3]} вакансий зарплата указана только в {res[2]}'
            bot.send_message(message.chat.id, text)

            if os.path.isfile(res[0]):
                os.remove(res[0])
        except Exception as e:
            bot.send_message(message.chat.id, e)

    elif msg[0] == 'навыки' or msg[0] == 'Навыки' \
                        or msg[0] == 'н' or msg[0] == 'Н' \
                        or msg[0] == 'n' or msg[0] == 'N':
        try:
            res = analize.headSkills(vacancy)
            photo = open(res[0], 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()

            text = f'Самые популярные навыки в {res[2]} вакансиях по запросу ' \
                    f'{vacancy}: *{res[1][0]}, {res[1][1]}, {res[1][2]}*'
            bot.send_message(message.chat.id, text)

            if os.path.isfile(res[0]):
                os.remove(res[0])
        except Exception as e:
            bot.send_message(message.chat.id, e)

    elif msg[0] == 'опыт' or msg[0] == 'Опыт' \
                        or msg[0] == 'о' or msg[0] == 'О' \
                        or msg[0] == 'o' or msg[0] == 'O':
        try:
            res = analize.experienceRate(vacancy)
            photo = open(res[0], 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()

            text = f'На основе {res[1]} вакансий по запросу {vacancy}'
            bot.send_message(message.chat.id, text)

            if os.path.isfile(res[0]):
                os.remove(res[0])
        except Exception as e:
            bot.send_message(message.chat.id, e)

    else:
        bot.send_message(message.chat.id, 'Где-то закралась ошибка! /help')

if __name__ == "__main__":
    bot.polling(none_stop=True)
