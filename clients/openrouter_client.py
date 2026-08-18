from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
import os

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL")

openrouter_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
