import os
from random import randint

import requests
from dotenv import load_dotenv
from telebot import TeleBot, types

load_dotenv()


class RecipeBot:
    def __init__(self):
        self.token = os.getenv('RECIPE_BOT_TOKEN')
        self.chat_id = os.getenv('MY_CHAT_ID')
        self.recipes_url = 'https://recipe-api.sytes.net/api/recipe/recipes/'
        self.bot = TeleBot(token=self.token)
        self.previous_recipe = None
        self._setup_handlers()

    def _setup_handlers(self):
        self.bot.message_handler(commands=['start'])(self.greet_user)
        self.bot.message_handler(commands=['Рецепт'])(self.send_recipe)

    @staticmethod
    def create_buttons():
        """Создание кнопок для взаимодействия с ботом"""
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        get_random_recipe = types.KeyboardButton('/Рецепт')
        keyboard.add(get_random_recipe)
        return keyboard

    def greet_user(self, message):
        """Приветственное сообщение пользователю"""
        keyboard = self.create_buttons()
        chat = message.chat
        self.bot.send_message(
            chat_id=chat.id,
            text='Привет! Это бот с идеями простых рецептов',
            reply_markup=keyboard,
        )

    def get_random_recipe_data(self):
        """Получение случайного рецепта из API"""
        response = requests.get(self.recipes_url).json()
        total_recipes = len(response)

        if total_recipes <= 1:
            return response[0]

        while True:
            random_id = randint(0, total_recipes - 1)
            recipe = response[random_id]
            if recipe['title'] != self.previous_recipe:
                self.previous_recipe = recipe['title']
                return recipe

    @staticmethod
    def format_ingredients(ingredients):
        """Форматирование списка ингредиентов для сообщения"""
        return '\n'.join(
            [
                f'- {ingredient["name"]}: {ingredient["amount"]} '
                f'{ingredient["measurement_unit"]}'
                for ingredient in ingredients
            ]
        )

    @staticmethod
    def format_recipe_details(recipe):
        """Форматирование детального сообщения о рецепте"""
        cooking_time = recipe['cooking_time']
        description = recipe['description']
        ingredients = RecipeBot.format_ingredients(
            recipe['ingredients_display']
        )

        return (
            f'⏳ *Время готовки:* {cooking_time} минут\n'
            f'🍪 *Описание:* {description}\n\n'
            f'🛒 *Ингредиенты:* \n{ingredients}'
        )

    def send_recipe(self, message):
        """Получение и отправка случайного рецепта пользователю"""
        chat = message.chat
        random_recipe = self.get_random_recipe_data()
        title = random_recipe['title']

        # Отправляем фото с названием рецепта
        self.bot.send_photo(
            chat_id=chat.id,
            photo=random_recipe['image'],
            caption=f'🍽️ *Рецепт дня:* {title}',
            parse_mode='Markdown',
        )

        # Отправляем описание, время готовки и ингредиенты отдельным сообщением
        self.bot.send_message(
            chat_id=chat.id,
            text=self.format_recipe_details(random_recipe),
            parse_mode='Markdown',
        )

    def run(self):
        self.bot.polling()


if __name__ == '__main__':
    recipe_bot = RecipeBot()
    recipe_bot.run()
