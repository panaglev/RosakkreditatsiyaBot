import os
import telebot
from model_config import Model

bot = os.getenv("TGBOTAPIKEY")

def send_start_message(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("Как работает данный бот")
    btn2 = telebot.types.KeyboardButton("Проверить")
    markup.add(btn1, btn2)
    bot.send_message(chat_id, text="Выбери что ты хочешь узнать", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    send_start_message(message.chat.id)
    
@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Как работает данный бот":
        bot.send_message(message.chat.id, text="Целью моего существования является помощь людям с сертификацией их "
                                               "продуктов. Выбирай вариант который тебе больше всего подходит во "
                                               "вкладке 'Проверить' и используй!")

    elif message.text == "Проверить":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        back = telebot.types.KeyboardButton("Вернуться в главное меню")
        markup.add(back)
        bot.send_message(message.chat.id, text="Загрузить EXCEL файл/Введите наименование товара", reply_markup=markup)
    
    elif message.text == "Загрузить EXCEL файл/Введите наименование товара":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = telebot.types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1)
        bot.send_message(message.chat.id, text="Выбери что ты хочешь узнать", reply_markup=markup)

    elif message.text == "Вернуться в главное меню":
        send_start_message(message.chat.id)
    
    else:
        model = Model(model_name='multi-qa-MiniLM-L6-cos-v1')
        if len(message.text) > 0:
            bot.send_message(message.chat.id, text=f"{model.get_recommendation_card(query=message.text)}")
        else:
            bot.send_message(message.chat.id, text="Я затрудняюсь ответить на ваш вопрос")
        send_start_message(message.chat.id)


@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    local_file_path = f'{file_info.file_path}'
    with open(local_file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    model = Model(model_name='multi-qa-MiniLM-L6-cos-v1')
    processed_file = model.preprocess_input_user_file(path=local_file_path)

    processed_file_path = 'documents/new_file_updated.csv'
    processed_file.to_csv(processed_file_path)

    with open(processed_file_path, 'rb') as processed_file:
        bot.send_document(message.chat.id, document=processed_file)

bot.polling(none_stop=True)