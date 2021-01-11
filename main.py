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

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')


def commandsKeyboard(vacancy):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton(f'Показать {vacancy}'),
               telebot.types.KeyboardButton(f'Зарплата {vacancy}'),
               telebot.types.KeyboardButton(f'Навыки {vacancy}'),
               telebot.types.KeyboardButton(f'Опыт {vacancy}'),
               telebot.types.KeyboardButton(f'Скачать {vacancy}'),
               telebot.types.KeyboardButton(f'/db'))
    return markup


def tablesKeyboard(names):
    markup = telebot.types.InlineKeyboardMarkup()

    for name in names:
        markup.add(telebot.types.InlineKeyboardButton(name, callback_data=name))
    return markup


def vacanciesKeyboard(vacancy): # vacancy = ''vacancy_number_on_the_next_page'_'vacancy_name''
    markup = telebot.types.InlineKeyboardMarkup()

    if int(vacancy.split('_')[0]) > 5:
        markup.add(telebot.types.InlineKeyboardButton('В начало', callback_data=f'{vacancy}_first'),
                    telebot.types.InlineKeyboardButton('Вперёд', callback_data=f'{vacancy}_next'))
    else:
        markup.add(telebot.types.InlineKeyboardButton('Вперёд', callback_data=f'{vacancy}_next'))
    return markup


@bot.callback_query_handler(func=lambda message: True)
def ans(message):
    if message.data in info.getTablesNames():
        bot.send_message(message.message.chat.id,
                f'Какую информацию по запросу <code>{message.data}</code> хочешь получить?',
                reply_markup=commandsKeyboard(message.data))
    else:
        try:
            # msg = [vacancy_number_on_the_next_page, vacancy_name, callback(first/next)]
            msg = message.data.split('_')
            if msg[2] == 'next':
                text = info.getVacancies(msg[1], int(msg[0]), int(msg[0]) + 5)

                # take int(vacancy_number) from string
                count = 3
                while text[count] != '.':
                    count += 1
                num = int(text[3:count]) + 4

                bot.edit_message_text(text, message.message.chat.id, message.message.id,
                                    reply_markup=vacanciesKeyboard(str(num) + '_' + msg[1]),
                                    disable_web_page_preview=True)
            elif msg[2] == 'first':
                text = info.getVacancies(msg[1])
                bot.edit_message_text(text, message.message.chat.id, message.message.id,
                                    reply_markup=vacanciesKeyboard(str(5) + '_' + msg[1]),
                                    disable_web_page_preview=True)
        except Exception as e:
            init.updateErrors(message.message.chat.id, message.message.chat.first_name, message.data, e)


@bot.message_handler(commands=['start'])
def welcome(message):
    init.updateStatistics(message.chat.id, message.chat.first_name, 'start')
    bot.send_message(message.chat.id, 'Привет! Смотри, что я умею /help\n' \
        ' Используй /db, чтобы посмотреть уже скачанные вакансии')


@bot.message_handler(commands=['help'])
def help(message):
    init.updateStatistics(message.chat.id, message.chat.first_name, 'help')

    text = '<b>Я могу скачивать вакансии с hh.ru, а затем анализировать их</b>\n\n' \
        '<b>Пример запроса:</b> <code>вакансия data scientist</code> или <code>зарплата data scientist</code>\n\n' \
        'Скачать или обновить вакансии в базе данных: <code>вакансия "название вакансии" </code>\n' \
        'Запросы дело не быстрое, так что придётся недолго подождать или долго, если ищешь джаву\n\n' \
        'Список вакансий в базе данных: /db\n\n' \
        'Для работы следующих команд вакансия должна находиться в базе данных\n' \
        'Показать вакансии: <code>показать "название вакансии"</code>\n' \
        'Средняя зарплата: <code>зарплата "название вакансии"</code>\n' \
        'Популярные навыки: <code>навыки "название вакансии"</code>\n' \
        'Распределение опыта: <code>опыт "название вакансии"</code>\n' \
        'Скачать таблицу в csv: <code>скачать "название вакансии"</code>\n' \
        '\nP.S.: Пока что ищу только в default city\n' \
        'P.S.s.: Ожидаю добавление поддержки заданий от фиксеров\n'
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['db'])
def db(message):
    init.updateStatistics(message.chat.id, message.chat.first_name, 'db')

    names = info.getTablesNames()
    if names:
        bot.send_message(message.chat.id,
                'Доступны вакансии по запросам:', reply_markup=tablesKeyboard(names))
        bot.send_message(message.chat.id,
                'Чтобы скачать или обновить вакансии напиши: <code>вакансия "название вакансии"</code>')
    else:
        bot.send_message(message.chat.id, 'Список вакансий пуст. /help')


@bot.message_handler(content_types=['text'])
def parser(message):
    init.updateStatistics(message.chat.id, message.chat.first_name, message.text)

    msg = message.text.lower().split()
    vacancy = ' '.join(msg[1:])

    # msg[0] is command -> 'full name' or 'short rus' or 'short translit'
    if msg[0] == 'вакансия' or msg[0] == 'в' or msg[0] == 'v':
        try:
            bot.send_message(message.chat.id, 'Это может занять некторое время')
            init.getData(vacancy, message, bot)
            bot.send_message(message.chat.id, 'Данные по вакансии доступны к анализу',
                             reply_markup=commandsKeyboard(vacancy))
        except Exception as e:
            if str(e) == 'Вакансий по запросу не найдено':
                bot.send_message(message.chat.id, f'{e}, проверь правильность запроса /help')
            else:
                bot.send_message(message.chat.id, 'Что-то пошло не так :с /help')
                bot.send_message(message.chat.id, e)
                init.updateErrors(message.chat.id, message.chat.first_name, message.text, e)

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
            init.updateErrors(message.chat.id, message.chat.first_name, message.text, e)

    elif msg[0] == 'показать' or msg[0] == 'п' or msg[0] == 'p':
        try:
            text = info.getVacancies(vacancy)
            bot.send_message(message.chat.id, text,
                             reply_markup=vacanciesKeyboard(str(5) + '_' + vacancy),
                             disable_web_page_preview=True)
        except Exception as e:
            bot.send_message(message.chat.id, e)
            init.updateErrors(message.chat.id, message.chat.first_name, message.text, e)

    elif msg[0] == 'зарплата' or msg[0] == 'зп'  or msg[0] == 'zp':
        try:
            # res = ['file_name', averageSalary, count_vacancies_with_salary, count_vacancies]
            res = analize.averageSalary(vacancy)
            if res == 'Зарпалата не указана ни в одной вакансии':
                bot.send_message(message.chat.id, res,
                                reply_markup=commandsKeyboard(vacancy))
            else:
                if res[0] != 'No graph':
                    photo = open(res[0], 'rb')
                    bot.send_photo(message.chat.id, photo)
                    photo.close()
                    if os.path.isfile(res[0]):
                        os.remove(res[0])
                text = f'<b>{res[1]}</b> - средняя зарплата по запросу <code>{vacancy}</code>\n' \
                        f'Из {res[3]} вакансий зарплата указана только в {res[2]}'
                bot.send_message(message.chat.id, text,
                                reply_markup=commandsKeyboard(vacancy))
        except Exception as e:
            bot.send_message(message.chat.id, e)
            init.updateErrors(message.chat.id, message.chat.first_name, message.text, e)

    elif msg[0] == 'навыки' or msg[0] == 'н' or msg[0] == 'n':
        try:
            # res = ['file_name', [skills], count_vacancies]
            res = analize.headSkills(vacancy)
            photo = open(res[0], 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()
            if os.path.isfile(res[0]):
                os.remove(res[0])
            text = f'Самые популярные навыки в {res[2]} вакансиях по запросу ' \
                    f'<code>{vacancy}</code>: <b>{res[1][0]}, {res[1][1]}, {res[1][2]}</b>'
            bot.send_message(message.chat.id, text,
                             reply_markup=commandsKeyboard(vacancy))
        except Exception as e:
            bot.send_message(message.chat.id, e)
            init.updateErrors(message.chat.id, message.chat.first_name, message.text, e)

    elif msg[0] == 'опыт' or msg[0] == 'о' or msg[0] == 'o':
        try:
            # res = ['file_name', count_vacancies]
            res = analize.experienceRate(vacancy)
            photo = open(res[0], 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()
            if os.path.isfile(res[0]):
                os.remove(res[0])
            text = f'На основе {res[1]} вакансий по запросу <code>{vacancy}</code>'
            bot.send_message(message.chat.id, text,
                             reply_markup=commandsKeyboard(vacancy))
        except Exception as e:
            bot.send_message(message.chat.id, e)
            init.updateErrors(message.chat.id, message.chat.first_name, message.text, e)

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
            init.updateErrors(message.chat.id, message.chat.first_name, message.text, e)

    else:
        bot.send_message(message.chat.id, 'Где-то закралась ошибка! /help')


if __name__ == "__main__":
    bot.polling(none_stop=True)
