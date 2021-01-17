import requests
import telebot
import logging
import os

from config import TOKEN
import data_init as init
import data_analize as analize
import data_info as info


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

def startKeyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton(f'Список вакансий'),
               telebot.types.KeyboardButton(f'/help'))
    return markup


def commandsKeyboard(vacancy: str):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton(f'Показать {vacancy}'),
               telebot.types.KeyboardButton(f'Зарплата {vacancy}'),
               telebot.types.KeyboardButton(f'Навыки {vacancy}'),
               telebot.types.KeyboardButton(f'Опыт {vacancy}'),
               telebot.types.KeyboardButton(f'Скачать {vacancy}'),
               telebot.types.KeyboardButton(f'Список вакансий'))
    return markup


def tablesKeyboard(names: list):
    markup = telebot.types.InlineKeyboardMarkup()

    for name in names:
        markup.add(telebot.types.InlineKeyboardButton(name, callback_data=name))
    return markup


def vacanciesKeyboard(vacancy: str): # vacancy = ''vacancy_number_on_current_page'_'vacancy_name''
    markup = telebot.types.InlineKeyboardMarkup()

    vacancy_number = int(vacancy.split('_')[0])
    if vacancy_number > 5:
        markup.add(telebot.types.InlineKeyboardButton('В начало', callback_data=f'{vacancy}_first'),
                    telebot.types.InlineKeyboardButton('Вперёд', callback_data=f'{vacancy}_next'))
    elif vacancy_number == 0:
        markup.add(telebot.types.InlineKeyboardButton('В начало', callback_data=f'{vacancy}_first'))
    else:
        markup.add(telebot.types.InlineKeyboardButton('Вперёд', callback_data=f'{vacancy}_next'))
    return markup


@bot.callback_query_handler(func=lambda message: True)
def callback_answer(message):
    if message.data in info.getTablesNames():
        bot.send_message(message.message.chat.id,
                f'Какую информацию по запросу <code>{message.data}</code> хочешь получить?',
                reply_markup=commandsKeyboard(message.data))
    else:
        # msg = [vacancy_number_on_current_page, vacancy_name, callback(first/next)]
        msg = message.data.split('_')
        try:
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
        except IndexError:
            bot.edit_message_reply_markup(message.message.chat.id, message.message.id,
                                    reply_markup=vacanciesKeyboard(str(0) + '_' + msg[1]))
        except Exception as e:
            init.updateErrors(message.message.chat.id, message.message.chat.username,
                              message.data, e)


@bot.message_handler(commands=['start'])
def welcome(message):
    init.updateStatistics(message.chat.id, message.chat.username, 'start')
    bot.send_message(message.chat.id, 'Привет! Гайд по моему использованию смотри в /help\n',
                        reply_markup=startKeyboard())


@bot.message_handler(commands=['help'])
def help(message):
    init.updateStatistics(message.chat.id, message.chat.username, 'help')

    text = '<b>Я могу скачивать вакансии с hh.ru, а затем анализировать их</b>\n\n' \
        'Список вакансий в базе данных: <code>список вакансий</code> или /db\n\n' \
        'Скачать или обновить вакансии в базе данных: <code>вакансия "название вакансии" </code>\n' \
        'Запросы дело не быстрое, так что придётся недолго подождать или долго, если ищешь джаву\n\n' \
        '<b>Пример запроса:</b> <code>вакансия data scientist</code> или ' \
        '<code>зарплата data scientist</code>\n\n' \
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
    init.updateStatistics(message.chat.id, message.chat.username, 'db')
    listVacancy(message)


def updateVacancy(message, vacancy: str):
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
            init.updateErrors(message.chat.id, message.chat.username, message.text, e)


def downloadVacancy(message, vacancy: str):
    try:
        doc_name = info.getCSV(f'select * from public."{vacancy}"')
        with open(doc_name, 'rb') as document:
            bot.send_document(message.chat.id, document,
                        reply_markup=commandsKeyboard(vacancy))
        if os.path.isfile(doc_name):
            os.remove(doc_name)
    except Exception as e:
        bot.send_message(message.chat.id, e)
        init.updateErrors(message.chat.id, message.chat.username, message.text, e)

def showVacancy(message, vacancy: str):
    try:
        text = info.getVacancies(vacancy)
        bot.send_message(message.chat.id, text,
                        reply_markup=vacanciesKeyboard(str(5) + '_' + vacancy),
                        disable_web_page_preview=True)
    except Exception as e:
        bot.send_message(message.chat.id, e)
        init.updateErrors(message.chat.id, message.chat.username, message.text, e)


def salaryVacancy(message, vacancy: str):
    try:
        # res = ['file_name', averageSalary, count_vacancies_with_salary, count_vacancies]
        res = analize.averageSalary(vacancy)
        if res[0] != 'No graph':
            with open(res[0], 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            if os.path.isfile(res[0]):
                os.remove(res[0])
        text = f'<b>{res[1]}</b> - средняя зарплата по запросу <code>{vacancy}</code>\n' \
                f'Из {res[3]} вакансий зарплата указана только в {res[2]}'
        bot.send_message(message.chat.id, text,
                        reply_markup=commandsKeyboard(vacancy))
    except Exception as e:
        if str(e) == 'Зарпалата не указана ни в одной вакансии':
            bot.send_message(message.chat.id, e,
                            reply_markup=commandsKeyboard(vacancy))
        else:
            bot.send_message(message.chat.id, e)
            init.updateErrors(message.chat.id, message.chat.username, message.text, e)


def skillsVacancy(message, vacancy: str):
    try:
        # res = ['file_name', [skills], count_vacancies]
        res = analize.headSkills(vacancy)
        with open(res[0], 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        if os.path.isfile(res[0]):
            os.remove(res[0])
        text = f'Самые популярные навыки в {res[2]} вакансиях по запросу ' \
                f'<code>{vacancy}</code>: <b>{res[1][0]}, {res[1][1]}, {res[1][2]}</b>'
        bot.send_message(message.chat.id, text,
                        reply_markup=commandsKeyboard(vacancy))
    except Exception as e:
        bot.send_message(message.chat.id, e)
        init.updateErrors(message.chat.id, message.chat.username, message.text, e)


def experienceVacancy(message, vacancy: str):
    try:
        # res = ['file_name', count_vacancies]
        res = analize.experienceRate(vacancy)
        with open(res[0], 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        if os.path.isfile(res[0]):
            os.remove(res[0])
        text = f'На основе {res[1]} вакансий по запросу <code>{vacancy}</code>'
        bot.send_message(message.chat.id, text,
                        reply_markup=commandsKeyboard(vacancy))
    except Exception as e:
        bot.send_message(message.chat.id, e)
        init.updateErrors(message.chat.id, message.chat.username, message.text, e)


def listVacancy(message, vacancy=None):
    names = info.getTablesNames()
    if names:
        bot.send_message(message.chat.id,
                'Доступны вакансии по запросам:', reply_markup=tablesKeyboard(names))
        bot.send_message(message.chat.id,
                'Чтобы скачать или обновить вакансии напиши: ' \
                '<code>вакансия "название вакансии"</code>')
    else:
        bot.send_message(message.chat.id, 'Список вакансий пуст \n' \
                'Чтобы скачать вакансии напиши: <code>вакансия "название вакансии"</code>')


def sqlQuery(message, vacancy: str):
    try:
        doc_name = info.getCSV(command=vacancy)
        with open(doc_name, 'rb') as document:
            bot.send_document(message.chat.id, document)
        if os.path.isfile(doc_name):
            os.remove(doc_name)
    except Exception as e:
        bot.send_message(message.chat.id, e)
        init.updateErrors(message.chat.id, message.chat.username, message.text, e)


@bot.message_handler(content_types=['text'])
def parser(message):
    init.updateStatistics(message.chat.id, message.chat.username, message.text)

    msg = message.text.lower().split()
    vacancy = ' '.join(msg[1:])

    commands = {
        'вакансия': updateVacancy,
        'скачать': downloadVacancy,
        'показать': showVacancy,
        'зарплата': salaryVacancy,
        'навыки': skillsVacancy,
        'опыт': experienceVacancy,
        'список': listVacancy,
        'sql': sqlQuery
    }

    if msg[0] in commands:
        commands[msg[0]](message, vacancy)
    else:
        bot.send_message(message.chat.id, 'Где-то закралась ошибка! /help')


if __name__ == "__main__":
    bot.polling(none_stop=True)
