import os
import sys

from dotenv import load_dotenv
from loguru import logger

log_format = '{time:H:mm:ss} | "{function}" | {line} ({module}) | <level>{level}</level> | {message}'

logger.remove()
logger.add(
        sink=sys.stdout,
        level='DEBUG',
        format=log_format,
)
logger.add(
        sink='..//temp//log.log',
        level='INFO',
        mode='w',
        format=log_format,
)

load_dotenv()

BD_PATH = '../temp/DataBase.db'
API_BOT = os.getenv('API_BOT')
ADMIN_ID = int(os.getenv('MY_ID'))

from until.BaseDate import BaseDate

db = BaseDate(BD_PATH)
from encryption_functions import encrypt_password, decrypt_password
