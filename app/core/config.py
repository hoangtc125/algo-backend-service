import json
import os
import firebase_admin
from firebase_admin import credentials
from os import getenv
from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(BASE_DIR + r"/.env")


class ProjectConfig(BaseSettings):
    SERVICE_NAME = getenv("SERVICE_NAME", "ALGO_BACKEND")
    SECRET_KEY = getenv("SECRET_KEY")
    SECURITY_ALGORITHM = getenv("SECURITY_ALGORITHM")
    MONGO_URL = getenv("MONGO_URL")
    MONGO_DB = "algo"
    ALGO_PORT = int(getenv("ALGO_PORT", 8001))
    MAIL_USER = str(getenv("MAIL_USER", ""))
    MAIL_PASS = str(getenv("MAIL_PASS", ""))
    RESPONSE_CODE_DIR = BASE_DIR + r"/resources/response_code.json"
    FIREBASE_CONFIG = BASE_DIR + r"/resources/algo-firebase.json"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 


project_config = ProjectConfig()
print("--- Algo Backend Config:\n", json.dumps(project_config.dict(), indent=4))

cred = credentials.Certificate(project_config.FIREBASE_CONFIG)
firebase_admin.initialize_app(cred)
