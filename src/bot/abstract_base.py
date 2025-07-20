from abc import ABC, abstractmethod

from telebot import TeleBot

from consts import TOKEN


class BaseTelegramBot(ABC):
    def __init__(self) -> None:
        self.token: str = TOKEN
        if not self.token:
            raise ValueError(f'Токен {TOKEN} отсутствует!')

        self.bot = TeleBot(token=self.token)

    @abstractmethod
    def _fetch_all_recipes(self):
        pass

    @abstractmethod
    def _setup_handlers(self):
        pass

    @staticmethod
    @abstractmethod
    def create_buttons():
        pass

    @abstractmethod
    def greet_user(self, message):
        pass

    @abstractmethod
    def get_random_recipe_data(self):
        pass

    @abstractmethod
    def get_recipe_by_tag(self, tag):
        pass


    @staticmethod
    @abstractmethod
    def format_ingredients(ingredients):
        pass

    @staticmethod
    @abstractmethod
    def format_recipe_details(recipe):
        pass

    @abstractmethod
    def send_recipe(self, message):
        pass

    @abstractmethod
    def send_breakfast(self, message):
        pass

    @abstractmethod
    def send_dessert(self, message):
        pass

    @abstractmethod
    def _start_periodic_refresh(self):
        pass

    @abstractmethod
    def run(self):
        pass
