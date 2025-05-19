<details>
<summary>RU 🇷🇺</summary>

# Документация для school_tg_bot 🚀

## Описание проекта  
  
Этот проект представляет собой Telegram-бота, созданного для упрощения взаимодействия учеников с информацией о  
расписании и домашних заданиях 📚. Бот предоставляет пользователям возможность быстро и удобно получать актуальную  
информацию о занятиях, домашних заданиях и оценках учеников в школе.  
  
Проект нацелен на оптимизацию учебного процесса, позволяя учащимся быть в курсе своих обязанностей и обеспечивая легкий  
доступ к необходимой информации (в отличие от школьного портала 😁).  
  
### Основные функции:  
  
1. **Получение расписания**:  
   - Пользователи могут запрашивать расписание на текущий день или на неделю 📆.  

2. **Домашнее задание**:  
   - Бот позволяет пользователям видеть свои домашние задания на текущий день или на всю неделю в зависимости от  
      настроек 🛠️.  
   - Домашние задания загружаются с сайта школы, что обеспечивает актуальность данных 💾.  

3. **Настройки пользователя**:  
   - Пользователи могут настраивать предпочтения получения информации о домашних заданиях (на день или на неделю) и  
      уведомлениях (включенные или выключенные).  
   - Все настройки удобно сохраняются и могут быть изменены в любое время ⏳.  

4. **Логирование**:  
   - Все действия пользователей и ошибки логируются с помощью библиотеки `loguru`, что позволяет отслеживать работу  
      бота и быстро находить возможные проблемы 🔍.  

### Технические детали:  

- #### **Используемые библиотеки**:  
- [![  
  `Aiogram`](https://img.shields.io/badge/aiogram-3.14.0-blue?style=flat-square)](https://pypi.org/project/aiogram/) -  
  библиотека для асинхронной работы с API Telegram 📞.  
- [![  
  `Aiosqlite`](https://img.shields.io/badge/aiosqlite-0.20.0-green?style=flat-square)](https://pypi.org/project/aiosqlite/) -  
  для асинхронной работы с базами данных SQLite 🗄️.  
- [![  
  `Loguru`](https://img.shields.io/badge/loguru-0.7.3-red?style=flat-square)](https://pypi.org/project/loguru/) -  
  для логирования 🔍.  
- [![  
  `Requests`](https://img.shields.io/badge/requests-2.32.2-pink?style=flat-square)](https://pypi.org/project/requests/) -  
  для выполнения HTTP-запросов к школьному порталу для получения расписаний и  
  домашних заданий 🚀.  
- ~~[![  
  `Selenium`](https://img.shields.io/badge/selenium-4.29.0-orange?style=flat-square)](https://pypi.org/project/selenium/) -  
  для парсинга нового токена авторизации 🔑. (не используется)~~
  
### TODO-лист:
  
#### Основная работа 🛠️:
  
- [x] ([6d42](https://github.com/Lynx20wz/school_tg_bot/commit/6d4270b)) Авторизация пользователей  
- [x] ([e0ae](https://github.com/Lynx20wz/school_tg_bot/commit/e0aecf3)) Реализовать систему кэша (уже с помощью **sqlite!**)  
- [x] ([4c95](https://github.com/Lynx20wz/school_tg_bot/commit/4c95aa7b])) Реализовать систему предупреждения об отсутствии токена для домашнего задания, оценок и расписания  
- [ ] Чек-лист сборки портфеля 📝✅  
- [ ] Уведомления о полученных оценках 🔔  
- [ ] Выложить код на автономный сервер  
- [ ] Уведомления о новом дз/оценках сразу после соответствующего урока  
- [ ] Система API "моя школа" на основе ООП  
- [ ] Поддержка других школьных дневников  
- [ ] Реализовать логирование на уровне middleware  
  
#### ГДЗ 🔢✅:
  
- [ ] Автоматическая отправка ответов на цдз  
- [ ] Написать свою систему (мечта)  
- [ ] Автоматическое решение ЦДЗ  
  
#### Настройки ⚙️:

- [x] ([5f43](https://github.com/Lynx20wz/school_tg_bot/commit/5f4301fd)) Настройка дз день/неделя 🛠️  
- [x] ([5f43](https://github.com/Lynx20wz/school_tg_bot/commit/5f4301fd)) Настройка уведомлений 🔔  
  
---
### **Структура кода**:  
  
#### bin:  
  
> - `main.py` - Основная логика взаимодействия с пользователем реализована в файле  
> - `parser_school.py` - Функции для парсинга данных с сайта школы сгруппированы в файле  
> - ~~`get_token.py` - Для получения нового токена используется файл~~ (_сейчас не используется_)  
> - `KeyBoards.py` - Файл с функциями для создания клавиатур **aiogram**  
> - `Start tg bot.cmd` - Быстрый запуска бота в терминале.  
  
#### classes:  
  
> - `UserClass.py` - Класс для хранения информации о пользователе  
> - `BaseDate.py` - Класс для работы с базой данных  
  
#### handlers:  
  
> - `registration.py` - Получение токена  
> - `debug.py` - Функции для дебага  
  
### Если вы хотите внести свой вклад в проект, вы можете сделать это следующим образом:  
  
1. Создайте форк репозитория  
2. Внесите свои изменения  
3. Создайте Pull Request  
  
---  
  
### Лицензия:  
  
Этот проект лицензирован под лицензией MIT. Подробности можно найти в файле [LICENSE](LICENSE).  
  
---  
"Спасибо за внимание!" - [Lynx20wz](https://github.com/Lynx20wz)

</details>
<details>
<summary>EN 🇺🇸</summary>

# Documentation for school_tg_bot 🚀

## Project Description 
 
This project is a Telegram bot created to simplify the interaction of students with information about
schedules and homework 📚. The bot provides users with the ability to quickly and conveniently receive up-to-date
information about classes, homework, and grades of students at school. 
 
The project aims to optimize the learning process by allowing students to keep abreast of their responsibilities and providing easy
access to the necessary information (unlike the school portal 😁). 
 
### Main Functions:

1. **Getting a schedule**:
    - Users can request a schedule for the current day or for the week 📆.

2. **Homework**:
    - The bot allows users to see their homework for the current day or for the whole week,
      depending on
      the settings 🛠️.
    - Homework assignments are downloaded from the school's website, which ensures that the data is
      up-to-date 💾.

3. **User Settings**:
   - Users can customize preferences for receiving homework information (daily or weekly) and notifications (on or off).
      notifications (on or off).
   - All settings are conveniently saved and can be changed at any time ⏳.

4. **Logging**:  
   - All user actions and errors are logged using the `loguru` library, which allows you to track the work of the 
      bot and quickly find possible problems 🔍.

### Technical details:

- #### **Libraries used**: 
- [![  
  `Aiogram`](https://img.shields.io/badge/aiogram-3.14.0-blue?style=flat-square)](https://pypi.org/project/aiogram/) -  
  library for asynchronous work with Telegram API 📞.  
- [![  
  `Aiosqlite`](https://img.shields.io/badge/aiosqlite-0.20.0-green?style=flat-square)](https://pypi.org/project/aiosqlite/) -  
  for asynchronous work with SQLite databases 🗄️.  
- [![  
  `Loguru`](https://img.shields.io/badge/loguru-0.7.3-red?style=flat-square)](https://pypi.org/project/loguru/) -  
  for logging 🔍.  
- [![  
  `Requests`](https://img.shields.io/badge/requests-2.32.3-pink?style=flat-square)](https://pypi.org/project/requests/) -  
  to perform HTTP requests to the school portal to retrieve schedules and
  homework 🚀.  
- ~~[![  
  `Selenium`](https://img.shields.io/badge/selenium-4.29.0-orange?style=flat-square)](https://pypi.org/project/selenium/) -  
  to parsing a new authorization token 🔑. (not used)~~
  
### TODO list:
  
#### Main work 🛠️:

- [x] ([6d42](https://github.com/Lynx20wz/school_tg_bot/commit/6d4270b)) User authorization
- [x] ([e0ae](https://github.com/Lynx20wz/school_tg_bot/commit/e0aecf3)) Implement a cache system (already using **sqlite!**)
- [x] ([4c95](https://github.com/Lynx20wz/school_tg_bot/commit/4c95aa7b])) Implement a token warning system for homework, grades, and schedules
- [ ] Portfolio assembly checklist 📝✅
- [ ] Notifications of grades received 🔔
- [ ] Upload code to offline server
- [ ] Notifications about new assignments/assessments immediately after the corresponding lesson
- [ ] OOP-based "my school" API system
- [ ] Support for other school diaries
- [ ] Implement middleware level logging


#### GDS 🔢✅:

- [ ] Automatically send answers to gdz
- [ ] Write your own system (dream)
- [ ] Automatic solution of digital homework 

#### Settings ⚙️:

- [x] ([5f43](https://github.com/Lynx20wz/school_tg_bot/commit/5f4301fd)) Customize dz day/week 🛠️
- [x] ([5f43](https://github.com/Lynx20wz/school_tg_bot/commit/5f4301fd)) Customizing notifications 🔔

---
### **Code Structure**:

#### bin:

> - `main.py` - The basic logic of user interaction is implemented in the file
> - `parser_school.py` - Functions for parsing data from the school website are grouped in the file
> - ~~`get_token.py` - The file~~ (_not used now_) is used to get a new token.
> - `KeyBoards.py` - A file with functions for creating **aiogram** keyboards
> - `Start tg bot.cmd` - Quick start bot in terminal.

  
#### classes:  
  
> - `UserClass.py` - A class for storing user information
> - `BaseDate.py` - Class for working with database
  
#### handlers:  
  
> - `registration.py` - Getting token
> - `debug.py` - Functions for debugging

---  

### If you would like to contribute to the project, you may do so as follows:

1. Create a fork of the repository
2. Make your changes
3. Create a Pull Request
  
---  
  
### License:  
  
This project is licensed under the MIT license. Details can be found in the [LICENSE](LICENSE) file.

---
"Thank you for your attention!" - [Lynx20wz](https://github.com/Lynx20wz)
</details>