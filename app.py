'''Telegram api binance bot'''
import os
import requests
from dotenv import load_dotenv
import telebot
from telebot import types

load_dotenv()

TOKEN = os.environ.get('BOT_TOKEN')

if TOKEN is None:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена.")

URL = 'https://api.binance.com/api/v3/ticker/price'
bot = telebot.TeleBot(TOKEN)

CRYPTO = {
    'Bitcoin': 'BTCUSDT',
    'Ethereum': 'ETHUSDT',
    'Doge': 'DOGEUSDT',
    'Euro': 'EURUSDT',
    'Binance coin': 'BNBUSDT',
    'Pound': 'GBPUSDT'
}

user_sessions = {}

#main handlers-----------------------------------------------------------

@bot.message_handler(commands = ['start'])
def send_welcome(message):
    '''welcome message'''
    bot.reply_to(message, '''
    Привет, введи "/menu" или зайди в меню через вкладку возле строки для отправки сообщения, чтобы начать работу с ботом🤖
    ''')


@bot.message_handler(commands = ['restart'])
def restart_bot(message):
    '''restart'''
    user_id = message.from_user.id
    user_sessions[user_id] = {
        'data': {},
        'steps': 0
    }
    bot.send_message(message.chat.id, 'Бот перезапущен, все настройки сброшены')
    bot.send_message(message.chat.id, 'Снова привет😁')
    show_menu(message)


@bot.message_handler(commands = ['menu'])
def show_menu(message):
    '''show menu'''
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


@bot.message_handler(commands = ['about'])
def about_bot(message):
    '''show info about bot'''
    handle_about(message)


@bot.message_handler(commands = ['contact'])
def contact_bot(message):
    '''func for /contact'''
    show_contact(message)

#lambda------------------------------------------------------------------

@bot.message_handler(func=lambda message: message.text == 'Криптовалюта')
def handle_crypto(message):
    '''crypto menu'''
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard = True)
    item_buttons = []
    for key in CRYPTO:
        item_buttons.append(types.KeyboardButton(key))

    btn_back = types.KeyboardButton('Вернуться в главное меню')

    markup.add(*item_buttons, btn_back)

    bot.send_message(
        message.chat.id,
        'Раздел криптовалюты',
        reply_markup = markup
    )


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
    '''send my contact'''
    bot.send_message(message.chat.id, '@iiiooyyyyyyy')


@bot.message_handler(func=lambda message: message.text == 'О боте')
def handle_about(message):
    '''show bot info'''
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
    '''back to main menu'''
    user_id = message.from_user.id
    user_sessions[user_id] = {'state': 'main_menu'}
    show_menu(message)


@bot.message_handler(func=lambda message: message.text == 'Помощь (доступные команды)')
def show_help(message):
    '''show commands'''
    help_text = '''
/restart - перезапуск бота
/menu - главное меню
/about - о боте
/contact - обратная связь
    '''
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(func=lambda message:message.text in CRYPTO)
def handle_result(message):
    '''show currency rate'''
    try:
        response = requests.get(URL, params={'symbol': CRYPTO[message.text]}, timeout=5)
        bot.send_message(message.chat.id,
                        f"1 {message.text} = {float(response.json()['price'])} usdt"
                        )
    except requests.exceptions.RequestException:
        bot.send_message(message.chat.id, 'Ошибка при получении данных')

#just chatting---------------------------------------------------------

@bot.message_handler(content_types = ['text'])
def handle_text(message):
    '''base replies'''
    if message.text.startswith('/'):
        return

    if message.text == '@iiiooyyyyyyy':
        return

    user_text = message.text.lower()
    if 'как дела' in user_text:
        bot.reply_to(message, 'Неплохо, а ты?')
    elif 'привет' in user_text:
        bot.reply_to(message, 'Привет🤖')
    else:
        bot.reply_to(message, 'Пока что не могу ответить😢')


@bot.message_handler(content_types = ['photo'])
def handle_photo(message):
    '''reply to photo'''
    bot.reply_to(message, 'Крутая фотка!')


@bot.message_handler(content_types = ['document'])
def handle_docs(message):
    '''reply to doc'''
    bot.reply_to(message, 'Файл получен')

@bot.message_handler(content_types = ['audio'])
def handle_audio(message):
    '''reply to audio'''
    bot.reply_to(message, 'Классный трек')


@bot.message_handler(content_types = ['sticker'])
def handle_sticker(message):
    '''reply to emoji'''
    bot.reply_to(message, '🤨')

#---------------------------------------------------------------------

if __name__ == '__main__':
    bot.infinity_polling()
