import requests
import telebot
import logging

import config
import data_init as init

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, 'Привет! Возможности бота смотри в /help')

@bot.message_handler(commands=['help'])
def welcome(message):
    bot.send_message(message.chat.id, 'вакансия data sciense')

@bot.message_handler(content_types=['text'])
def parser(message):
    msg = message.text.lower().split()
    if msg[0] == 'вакансия' or msg[0] == 'vacancy':
        bot.send_message(message.chat.id, 'Вакансия')
    elif msh[0] == 't':
        bot.send_message(message.chat.id, 'Hey ya')
    else:
        bot.send_message(message.chat.id, 'Чекни команды в /help')

#run
bot.polling(none_stop=True)

if __name__ == "__main__":
    pass
