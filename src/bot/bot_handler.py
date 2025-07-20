import random
import threading
import time

import requests
from dotenv import load_dotenv
from telebot import types

from consts import RECIPES_URL

from .abstract_base import BaseTelegramBot

load_dotenv()


class RecipeBot(BaseTelegramBot):
    def __init__(self):
        super().__init__()

        self.recipes_url = RECIPES_URL
        self.recipes = self._fetch_all_recipes()
        self.previous_recipe_id = None
        self._setup_handlers()
        self._start_periodic_refresh()

    def _fetch_all_recipes(self):
        return requests.get(self.recipes_url).json()

    def _setup_handlers(self):
        self.bot.message_handler(commands=['start'])(self.greet_user)
        self.bot.message_handler(
            func=lambda msg: msg.text == 'Рецепт'
        )(self.send_recipe)
        self.bot.message_handler(
            func=lambda msg: msg.text == 'Завтрак'
        )(self.send_breakfast)
        self.bot.message_handler(
            func=lambda msg: msg.text == 'Десерт'
        )(self.send_dessert)

    @staticmethod
    def create_buttons():
        """Создание кнопок для взаимодействия с ботом"""
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        get_random_recipe = types.KeyboardButton('Рецепт')
        get_breakfast = types.KeyboardButton('Завтрак')
        get_dessert = types.KeyboardButton('Десерт')
        keyboard.add(get_random_recipe, get_breakfast, get_dessert)
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
        """
        Получение случайного рецепта из локального списка
        не повторяя предыдущий
        """
        recipes = self.recipes
        total_recipes = len(recipes)

        if total_recipes == 0:
            return None
        if total_recipes == 1:
            self.previous_recipe_id = recipes[0]['id']
            return recipes[0]

        filtered = [r for r in recipes if r['id'] != self.previous_recipe_id]
        if not filtered:
            recipe = recipes[0]
        else:
            recipe = random.choice(filtered)
        self.previous_recipe_id = recipe['id']
        return recipe

    def get_recipe_by_tag(self, tag):
        """
        Получение случайного рецепта по тегу, не повторяя предыдущий
        """
        response = requests.get(f'{self.recipes_url}?tags={tag}').json()
        total_recipes = len(response)

        if total_recipes == 0:
            return None
        if total_recipes == 1:
            self.previous_recipe_id = response[0]['id']
            return response[0]

        filtered = [r for r in response if r['id'] != self.previous_recipe_id]
        if not filtered:
            recipe = response[0]
        else:
            recipe = random.choice(filtered)
        self.previous_recipe_id = recipe['id']
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

    def send_breakfast(self, message):
        chat = message.chat
        breakfast_recipe = self.get_recipe_by_tag('Завтрак')
        title = breakfast_recipe['title']

        self.bot.send_photo(
            chat_id=chat.id,
            photo=breakfast_recipe['image'],
            caption=f'🍽️ *Рецепт Завтрака:* {title}',
            parse_mode='Markdown',
        )
        self.bot.send_message(
            chat_id=chat.id,
            text=self.format_recipe_details(breakfast_recipe),
            parse_mode='Markdown',
        )

    def send_dessert(self, message):
        chat = message.chat
        dessert_recipe = self.get_recipe_by_tag('Десерт')
        title = dessert_recipe['title']

        self.bot.send_photo(
            chat_id=chat.id,
            photo=dessert_recipe['image'],
            caption=f'🍽️ *Рецепт Десерта:* {title}',
            parse_mode='Markdown',
        )
        self.bot.send_message(
            chat_id=chat.id,
            text=self.format_recipe_details(dessert_recipe),
            parse_mode='Markdown',
        )

    def _start_periodic_refresh(self, interval=300):
        """Запускает фоновое обновление рецептов каждые 300 секунд"""

        def refresh_loop():
            while True:
                time.sleep(interval)
                try:
                    self.recipes = self._fetch_all_recipes()
                except Exception as e:
                    print(f'Ошибка обновления рецептов: {e}')

        thread = threading.Thread(target=refresh_loop, daemon=True)
        thread.start()

    def run(self):
        print('\x1b[6;30;42m' + 'Бот начал работу!' + '\x1b[0m')
        self.bot.polling()
        print('\x1b[6;30;41m' + 'Бот остановлен!' + '\x1b[0m')

