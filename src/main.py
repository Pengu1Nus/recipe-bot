import os
from random import randint

import requests
from dotenv import load_dotenv
from telebot import TeleBot, types

load_dotenv()

RECIPE_BOT_TOKEN = os.getenv('RECIPE_BOT_TOKEN')
CHAT_ID = os.getenv('MY_CHAT_ID')
ALL_RECIPES_URL = 'https://recipe-api.sytes.net/api/recipe/recipes/'

bot = TeleBot(token=RECIPE_BOT_TOKEN)


def create_buttons():
    """Создание кнопок для взаимодействия с ботом"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    get_random_recipe = types.KeyboardButton('/Рецепт')
    keyboard.add(get_random_recipe)
    return keyboard


@bot.message_handler(commands=['start'])
def greet_user(message):
    """Приветственное сообщение пользователю"""
    keyboard = create_buttons()
    chat = message.chat
    bot.send_message(
        chat_id=chat.id,
        text='Привет! Это бот с идеями простых рецептов',
        reply_markup=keyboard,
    )


def get_random_recipe_data():
    """Получение случайного рецепта из API"""
    response = requests.get(ALL_RECIPES_URL).json()
    random_id = randint(0, len(response) - 1)
    return response[random_id]


def format_ingredients(ingredients):
    """Форматирование списка ингредиентов для сообщения"""
    return '\n'.join(
        [
            f'- {ingredient["name"]}: {ingredient["amount"]} '
            f'{ingredient["measurement_unit"]}'
            for ingredient in ingredients
        ]
    )


def format_recipe_details(recipe):
    """Форматирование детального сообщения о рецепте"""
    cooking_time = recipe['cooking_time']
    description = recipe['description']
    ingredients = format_ingredients(recipe['ingredients_display'])

    return (
        f'⏳ *Время готовки:* {cooking_time} минут\n'
        f'🍪 *Описание:* {description}\n\n'
        f'🛒 *Ингредиенты:* \n{ingredients}'
    )


@bot.message_handler(commands=['Рецепт'])
def send_recipe(message):
    """Получение и отправка случайного рецепта пользователю"""
    chat = message.chat
    random_recipe = get_random_recipe_data()
    title = random_recipe['title']

    # Отправляем фото с названием рецепта
    bot.send_photo(
        chat_id=chat.id,
        photo=random_recipe['image'],
        caption=f'🍽️ *Рецепт дня:* {title}',
        parse_mode='Markdown',
    )

    # Отправляем описание, время готовки и ингредиенты отдельным сообщением
    bot.send_message(
        chat_id=chat.id,
        text=format_recipe_details(random_recipe),
        parse_mode='Markdown',
    )


bot.polling()
