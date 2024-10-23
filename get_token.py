import json
import sys
import time
from os import getenv

from dotenv import load_dotenv
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from seleniumwire import webdriver

load_dotenv()

logger.remove()
logger.add(
        sink=sys.stdout,
        level='DEBUG',
        format='{time:H:mm:ss} | <level>{level}</level> | {message}',
)


def get_token():
    service = Service('D:\\System folder\\Documents\\Lynx_python\\school_tg_bot\\geckodriver.exe')
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Запуск в тихом режиме (без окна браузера)
    firefox_options.add_argument("--disable-dev-shm-usage")  # (Опционально) для ресурсов
    driver = webdriver.Firefox(service=service, options=firefox_options)
    logger.info('Ищу куки!')
    try:
        logger.debug('Перехожу на страницу')
        driver.get('https://authedu.mosreg.ru/diary/schedules/schedule/')
        time.sleep(3)

        logger.debug('На гос. услугах')
        driver.find_element(By.CLASS_NAME, 'loginForm_LoginFormButtonGos__FlI2F').click()
        time.sleep(3)

        username_field = driver.find_element(By.NAME, "Телефон  /  Email  /  СНИЛС")
        password_field = driver.find_element(By.NAME, "Пароль")

        username_field.send_keys(getenv('GMAIL'))
        password_field.send_keys(getenv('PASSWORD'))

        password_field.find_element(By.XPATH, "//button[contains(text(),'Войти')]").click()
        logger.debug('Захожу на школьный портал')
        time.sleep(5)
        cookies = driver.get_cookies()

    except:
        return 'Что-то не так!'
    finally:
        driver.quit()
        return {cookie['name']: cookie['value'] for cookie in cookies}


if __name__ == '__main__':
    with open('cache_school_bot.json', 'r') as cache_file:
        file = json.loads(cache_file.read())
    cookies = get_token()
    cookies['active_student'] = '1530640'
    cookies['JSESSIONID'] = 'node0hp6xu059ggkfh3mg75dk8vi3119422664.node0'
    file['cache']['cookies'] = cookies
    with open('cache_school_bot.json', 'w') as cache_file:
        json.dump(file, cache_file, indent=4)
    print('Готово!')
