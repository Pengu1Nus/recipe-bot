import os
from dotenv import load_dotenv

load_dotenv()

RECIPES_URL = 'https://recipe-api.sytes.net/api/recipe/recipes/'
TOKEN = os.getenv('RECIPE_BOT_TOKEN')
