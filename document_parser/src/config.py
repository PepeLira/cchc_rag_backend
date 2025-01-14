# import the ../.env file and make the environment variables available
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path("../.env").resolve()
print(f"Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
SECRET_KEY = os.getenv("SECRET_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TEST_PARSE_FOLDER = os.getenv("TEST_PARSE_FOLDER")
