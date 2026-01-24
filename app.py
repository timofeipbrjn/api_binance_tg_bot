'''Telegram api binance bot'''
import os
import requests
from dotenv import load_dotenv
import telebot
from telebot import types


load_dotenv()

TOKEN = os.environ.get('BOT_TOKEN')
YOUR_CONTACT = os.environ.get('ACCOUNT')
btn_back = types.KeyboardButton('Вернуться в главное меню')

if TOKEN is None:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена.")

if YOUR_CONTACT is None:
    raise ValueError("Контакт не указан.")

contact: str = YOUR_CONTACT

URL = 'https://api.binance.com/api/v3/ticker/price'
bot = telebot.TeleBot(TOKEN)

CRYPTO = {
    'Bitcoin': 'BTC',
    'Ethereum': 'ETH',
    'Binance coin': 'BNB',
    'Doge': 'DOGE',
    'Dollar': 'USDT',
    'Euro': 'EUR',
    'Pound': 'GBP',
    'Frank': 'CHF'
}

user_sessions = {}

#main handlers-----------------------------------------------------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    '''Sends welcome message.'''
    bot.reply_to(message, '''
    Привет, введи "/menu" или зайди в меню через вкладку возле строки для отправки сообщения, чтобы начать работу с ботом🤖
    ''')


@bot.message_handler(commands=['restart'])
def restart_bot(message):
    '''Restarts bot.'''
    user_id = message.from_user.id
    user_sessions[user_id] = {
        'data': {},
        'steps': 0
    }
    bot.send_message(message.chat.id, 'Бот перезапущен, все настройки сброшены')
    bot.send_message(message.chat.id, 'Снова привет😁')
    show_menu(message)


@bot.message_handler(commands=['menu'])
def show_menu(message):
    '''Displays the main keyboard menu to the user.'''
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard = True)

    btn1 = types.KeyboardButton('Криптовалюта')
    # btn2 = types.KeyboardButton('Настройки')
    btn3 = types.KeyboardButton('О боте')
    btn4 = types.KeyboardButton('Обратная связь')
    btn5 = types.KeyboardButton('Помощь (доступные команды)')

    markup.add(btn1, btn3, btn4, btn5)

    bot.send_message(
        message.chat.id,
        'Выберите опцию из меню',
        reply_markup = markup
    )


@bot.message_handler(commands=['contact'])
def contact_bot(message):
    '''Handles the /contact command'''
    show_contact(message)

#lambda------------------------------------------------------------------

@bot.message_handler(func=lambda message: message.text == 'Криптовалюта')
def handle_first_step(message):
    '''Displays the first keyboard crypto menu to the user.'''

    markup = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
    item_buttons = []
    for key in CRYPTO.keys():
        item_buttons.append(key)

    markup.add(*item_buttons, btn_back)

    bot.send_message(
        message.chat.id,
        'Выберите первую валюту',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text in CRYPTO)
def handle_second_step(message):
    '''The second step of getting result'''
    user_id = message.from_user.id
    user_sessions[user_id] = {
        'first_currency': CRYPTO[message.text]
    }

    markup = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
    item_buttons = []
    for key in CRYPTO.keys():
        item_buttons.append(key)

    markup.add(*item_buttons, btn_back)

    bot.send_message(
        message.chat.id,
        'Выберите вторую валюту',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text in CRYPTO)
def handle_final_step(message):
    '''Finally sending currency'''
    user_id = message.from_user.id
    coin1 = CRYPTO[user_sessions[user_id]['first_currancy']]
    coin2 = CRYPTO[message.text]

    try:
        first_coin = requests.get(URL, params={'symbol': coin1}, timeout=5)
        second_coin = requests.get(URL, params={'symbol': coin2}, timeout=5)
        first_coin.raise_for_status()
        second_coin.raise_for_status()

        price1 = first_coin.json().get('price')
        price2 = second_coin.json().get('price')

        price = float(price1 / price2)

        formatted_price = f"{price:.8f}".rstrip('0').rstrip('.')

        bot.send_message(message.chat.id, f"💎 1 {coin1} = {formatted_price} {coin2}")
    except (requests.exceptions.RequestException, ValueError, TypeError):
        bot.send_message(message.chat.id, '⚠️ Ошибка при получении данных')


# @bot.message_handler(func=lambda message: message.text in CRYPTO)
# def handle_price_request(message):
#     '''Fetches price for binance and sends it to the user.'''
#     symbol = CRYPTO[message.text]
#     try:
#         response = requests.get(URL, params={'symbol': symbol}, timeout=5)
#         response.raise_for_status()

#         raw_price = response.json().get('price')
#         price = float(raw_price)

#         formatted_price = f"{price:.8f}".rstrip('0').rstrip('.')
#         bot.send_message(message.chat.id, f"💎 1 {message.text} = {formatted_price} usdt")
#     except (requests.exceptions.RequestException, ValueError, TypeError):
#         bot.send_message(message.chat.id, '⚠️ Ошибка при получении данных')



# @bot.message_handler(func=lambda message: message.text == 'Криптовалюта')
# def handle_crypto(message):
#     '''Displays keyboard crypto menu to the user.'''
#     markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     item_buttons = []
#     for key in CRYPTO:
#         item_buttons.append(types.KeyboardButton(key))

#     btn_back = types.KeyboardButton('Вернуться в главное меню')

#     markup.add(*item_buttons, btn_back)

#     bot.send_message(
#         message.chat.id,
#         'Раздел криптовалюты',
#         reply_markup = markup
#     )



# Work in progress
# @bot.message_handler(func=lambda message: message.text == 'Настройки')
# def show_settings(message):
#     markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     btn1 = types.KeyboardButton('Язык')
#     btn2 = types.KeyboardButton('Уведомления')
#     btn_back = types.KeyboardButton('Вернуться в главное меню')
#
#     markup.add(btn1, btn2, btn_back)
#
#     bot.send_message(message.chat.id, 'Раздел настроек', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Обратная связь')
def show_contact(message):
    '''Sends my contact'''
    bot.send_message(message.chat.id, contact)


@bot.message_handler(commands=['about'])
@bot.message_handler(func=lambda message: message.text == 'О боте')
def handle_about(message):
    '''Sends info about bot.'''
    about_text = """
Этот бот помогает отслеживать курсы криптовалют и валют в реальном времени.

 Функции бота:
• Курсы криптовалют (Bitcoin, Ethereum и др.)
• Курсы валют (EUR, GBP)
• Простой и удобный интерфейс

 Используемые технологии:
• Python + pyTelegramBotAPI
• Binance API для данных
        """
    bot.send_message(message.chat.id, about_text)


@bot.message_handler(func=lambda message: message.text == 'Вернуться в главное меню')
def back(message):
    '''Back the user to main menu.'''
    user_id = message.from_user.id
    user_sessions[user_id] = {'state': 'main_menu'}
    show_menu(message)


@bot.message_handler(func=lambda message: message.text == 'Помощь (доступные команды)')
def show_help(message):
    '''Sends all commands.'''
    help_text = '''
Доступные команды на данный момент 🤠
/restart - перезапуск бота
/menu - главное меню
/about - о боте
/contact - обратная связь
    '''
    bot.send_message(message.chat.id, help_text)


#---------------------------------------------------------------------
if __name__ == '__main__':
    bot.infinity_polling()
