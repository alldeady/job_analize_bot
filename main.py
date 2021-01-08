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


def commandsKeyboard(vacancy):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton(f'Показать {vacancy}'),
               telebot.types.KeyboardButton(f'Зарплата {vacancy}'),
               telebot.types.KeyboardButton(f'Навыки {vacancy}'),
               telebot.types.KeyboardButton(f'Опыт {vacancy}'),
               telebot.types.KeyboardButton(f'Скачать {vacancy}'))
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, 'Привет! Смотри, что я умею /help')


@bot.message_handler(commands=['help'])
def help(message):
    init.updateStatistics(message.chat.id, message.chat.first_name, 'help')

    text = '*Я могу скачивать вакансии с hh.ru, а затем анализировать их*\n\n' \
        '*Пример запроса:* _зарплата data scientist_ или _зп data scientist_\n\n' \
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
def db(message):
    init.updateStatistics(message.chat.id, message.chat.first_name, 'db')

    names = info.getTablesNames()
    if names == '':
        bot.send_message(message.chat.id, 'Список вакансий пуст. /help')
    else:
        bot.send_message(message.chat.id, f'Доступны вакансии по запросам:\n{names}')


@bot.message_handler(content_types=['text'])
def parser(message):
    init.updateStatistics(message.chat.id, message.chat.first_name, message.text)

    msg = message.text.lower().split()
    vacancy = ' '.join(msg[1:])

    # msg[0] is command -> 'full name' or 'short rus' or 'short translit'
    if msg[0] == 'вакансия' or msg[0] == 'в' or msg[0] == 'v':
        try:
            bot.send_message(message.chat.id, 'Это может занять некторое время')
            init.getData(vacancy, message.chat.id, bot)
            bot.send_message(message.chat.id, 'Данные по вакансии доступны к анализу',
                             reply_markup=commandsKeyboard(vacancy))
        except Exception as e:
            bot.send_message(message.chat.id, 'Что-то пошло не так :с /help')
            bot.send_message(message.chat.id, e)

    elif msg[0] == 'скачать' or msg[0] == 'с' or msg[0] == 'c':
        try:
            doc_name = info.getCSV(f'select * from public."{vacancy}"')
            doc = open(doc_name, 'rb')
            bot.send_document(message.chat.id, doc,
                              reply_markup=commandsKeyboard(vacancy))
            doc.close()
            if os.path.isfile(doc_name):
                os.remove(doc_name)
        except Exception as e:
            bot.send_message(message.chat.id, e)

    elif msg[0] == 'показать' or msg[0] == 'п' or msg[0] == 'p':
        try:

            #keyboard = telebot.types.InlineKeyboardMarkup()
            #next = telebot.types.InlineKeyboardButton(text='Вперёд', callback_data='nextVac')
            #keyboard.add(next)

            text = info.getVacancies(vacancy)
            bot.send_message(message.chat.id, text)


        except Exception as e:
            bot.send_message(message.chat.id, e)

    elif msg[0] == 'зарплата' or msg[0] == 'зп'  or msg[0] == 'zp':
        try:
            res = analize.averageSalary(vacancy)
            photo = open(res[0], 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()
            if os.path.isfile(res[0]):
                os.remove(res[0])

            text = f'*{res[1]}* - средняя зарплата по запросу {vacancy}\n' \
                    f'Из {res[3]} вакансий зарплата указана только в {res[2]}'
            bot.send_message(message.chat.id, text,
                             reply_markup=commandsKeyboard(vacancy))
        except Exception as e:
            bot.send_message(message.chat.id, e)

    elif msg[0] == 'навыки' or msg[0] == 'н' or msg[0] == 'n':
        try:
            res = analize.headSkills(vacancy)
            photo = open(res[0], 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()
            if os.path.isfile(res[0]):
                os.remove(res[0])

            text = f'Самые популярные навыки в {res[2]} вакансиях по запросу ' \
                    f'{vacancy}: *{res[1][0]}, {res[1][1]}, {res[1][2]}*'
            bot.send_message(message.chat.id, text,
                             reply_markup=commandsKeyboard(vacancy))
        except Exception as e:
            bot.send_message(message.chat.id, e)

    elif msg[0] == 'опыт' or msg[0] == 'о' or msg[0] == 'o':
        try:
            res = analize.experienceRate(vacancy)
            photo = open(res[0], 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()
            if os.path.isfile(res[0]):
                os.remove(res[0])

            text = f'На основе {res[1]} вакансий по запросу {vacancy}'
            bot.send_message(message.chat.id, text,
                             reply_markup=commandsKeyboard(vacancy))
        except Exception as e:
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

    else:
        bot.send_message(message.chat.id, 'Где-то закралась ошибка! /help')


if __name__ == "__main__":
    bot.polling(none_stop=True)
