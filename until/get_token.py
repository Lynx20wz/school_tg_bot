"""Tool using selenium to get authorization token for "gosuslugi" by login and password.

NOT USED NOW due to impossibility to provide security guarantees for login data
"""

import os
import time

from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def get_token(login, password):
    logger.debug(f'{login}, {password}')
    service = Service('.//geckodriver.exe')
    firefox_options = Options()
    firefox_options.add_argument('--headless')  # Running in silent mode (without browser window)
    firefox_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Firefox(service=service, options=firefox_options)
    logger.info('Ищу куки!')
    try:
        logger.debug('Перехожу на страницу')
        driver.get('https://authedu.mosreg.ru/diary/schedules/schedule/')

        logger.debug('На гос. услугах')
        WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.CLASS_NAME, 'loginForm_LoginFormButtonGos__FlI2F'))
        ).click()

        username_field = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.NAME, 'Телефон  /  Email  /  СНИЛС'))
        )
        password_field = driver.find_element(By.NAME, 'Пароль')

        username_field.send_keys(login)
        password_field.send_keys(password)

        WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Войти')]"))
        ).click()
        logger.debug('Захожу на школьный портал')
        time.sleep(1)
        cookies = driver.get_cookies()
        return {cookie['name']: cookie['value'] for cookie in cookies}

    finally:
        driver.quit()


if __name__ == '__main__':
    cookies = get_token(os.getenv('GMAIL'), os.getenv('PASSWORD'))
    cookies['active_student'] = '1530640'
    cookies['JSESSIONID'] = 'node0hp6xu059ggkfh3mg75dk8vi3119422664.node0'
    print(cookies)
