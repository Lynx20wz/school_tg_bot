The documentation for this project is available in a few languages:

- [English](#documentation-for-school_tg_bot-)
- [Русский](#документация-для-school_tg_bot-)

<details>
<summary>EN</summary>

# Documentation for school_tg_bot 🚀

## Project Overview

`school_tg_bot` is a Telegram bot designed to streamline students’ access to information about
schedules, homework, and grades 📚. The bot enables users to quickly retrieve up-to-date data on
classes, assignments, and academic performance, enhancing the learning experience.

The project aims to optimize the educational process, keeping students informed of their
responsibilities and providing easy access to information, unlike the school portal 😊.

### Key Features

1. **Homework**:
    - View homework for the current day or the entire week based on user settings 🛠️.
    - Homework is fetched from the school website, ensuring data accuracy 💾.

2. **Schedule**:
    - Request schedules for the current day or the week 📆.

3. **Grades**:
    - Check grades for the current day or week based on user preferences.

4. **User Settings**:
    - Customize homework display (daily or weekly) and notification preferences (enabled/disabled).
    - Settings are saved and modified at any time ⏳.

5. **Logging**:
    - All user actions and errors are logged using the `loguru` library, facilitating monitoring and
      debugging 🗿.

### Technical Details

#### Installation

1. Clone the repository: `git clone https://github.com/Lynx20wz/school_tg_bot`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Start the bot: `python .` or `Start_tg_bot.cmd`.

#### Allowable start arguments

- `-back` - the database backup will not be loaded when the bot is started.
- `-debug` - the bot will be launched in debug mode (additional logs).

#### Libraries Used

- [![
  `Aiogram`](https://img.shields.io/badge/aiogram-3.14-blue?style=flat-square)](https://github.com/aiogram/aiogram) —
  Asynchronous library for the Telegram API 📋.
- [![
  `Aiosqlite`](https://img.shields.io/pypi/v/aiosqlite?color=aiosqlite)](https://github.com/omnilib/aiosqlite) —
  Asynchronous SQLite operations �️.
- [![`Loguru`](https://img.shields.io/pypi/v/loguru)](https://github.com/Delgan/loguru) — Logging of
  actions and errors 📜.
- [![`Requests`](https://img.shields.io/pypi/v/requests)](https://github.com/psf/requests) — HTTP
  requests to the school portal for schedules and assignments 🚀.
-
~~[![`Selenium`](https://img.shields.io/pypi/v/selenium)](https://github.com/SeleniumHQ/selenium) —
Token parsing (deprecated).~~

<details>
<summary>Project structure</summary>

##### root

- `__main__.py` — Program entry point.
- `start_tg_bot.cmd` — Script for launching the bot in the terminal.
- `LICENSE` — Project license.
- `README.md` — Project description.
- `pyproject.toml` — Project configuration.
- `requirements.txt` — Bot dependencies.

##### bot

> bin
> - `bot.py` — Core logic for Telegram API interaction.

> classes
> - `BaseData.py` — Class for SQLite database operations.
> - `UserClass.py` — Class for storing user data.
> - `Homework.py` — Class for handling homework.
> - `Parser.py` — Class for parsing "My School" data.

> filters
> - `is_admin.py` — Administrator filter.

> handlers
> - `registration.py` — Authorization and token handling.
> - `debug.py` — Debugging functions.
> - `unknown.py` — Handling unknown messages.

> utils
> - ~~`get_token.py` — Token retrieval (deprecated)~~.
> - `Keyboards.py` — Functions for creating `aiogram` keyboards.
> - `Exceptions.py` — Custom exception classes.

</details>

---

### TODO List

#### Core Tasks 🛠️

- [x] ([6d42](https://github.com/Lynx20wz/school_tg_bot/commit/6d4270b)) User authorization.
- [x] ([e0ae](https://github.com/Lynx20wz/school_tg_bot/commit/e0aecf3)) Database (SQLite).
- [x] ([4c95](https://github.com/Lynx20wz/school_tg_bot/commit/4c95aa7b)) Token absence.
- [x] Middleware-level logging.
  notifications for homework, grades, and schedules.
- [ ] "My School" API system based on OOP:
    - [x] ([29e6](https://github.com/Lynx20wz/school_tg_bot/commit/29e6e3fa)) `Homework` class.
    - [x] ([003e](https://github.com/Lynx20wz/school_tg_bot/commit/003e9a54)) `Parser` class.
    - [ ] `Schedule` class.
    - [ ] `Grades` class.
    - [ ] "My School" API class.
- [ ] School supplies checklist 📝✅.
- [ ] Grade notifications 🔔.
- [ ] Deployment to a standalone server.
- [ ] Notifications for new homework/grades after lessons.
- [ ] Support for other school diaries.
- [ ] Caching with **Redis**.

#### Assignment Solutions 🔢✅

- [ ] Automatic submission of digital assignment answers.
- [ ] Custom solution system (a dream).
- [ ] Automatic solving of digital assignments.

#### Settings ⚙️

- [x] ([5f43](https://github.com/Lynx20wz/school_tg_bot/commit/5f4301fd)) Homework display
  settings (daily/weekly) 🛠️.
- [x] ([5f43](https://github.com/Lynx20wz/school_tg_bot/commit/5f4301fd)) Notification management
  🔔.

---

### Contributing

1. Fork the repository.
2. Make your changes.
3. Create a Pull Request.

---

### License

The project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

"Thank you for your attention!" — [Lynx20wz](https://github.com/Lynx20wz)
</details>

<details>
<summary>RU</summary>

# Документация для school_tg_bot 🚀

## Описание проекта

`school_tg_bot` — это Telegram-бот, созданный для упрощения доступа школьников к информации о
расписании, домашних заданиях и оценках 📚. Бот позволяет быстро получать актуальные данные о
занятиях, заданиях и успеваемости, делая учебный процесс удобнее.

Проект направлен на оптимизацию учебного процесса, помогая учащимся быть в курсе своих обязанностей
и предоставляя простой доступ к информации, в отличие от школьного портала 😊.

### Основные функции

1. **Домашние задания**:
    - Просмотр домашних заданий на текущий день или на неделю в зависимости от пользовательских
      настроек 🛠️.
    - Данные загружаются с сайта школы, что гарантирует их актуальность 💾.

2. **Расписание**:
    - Запрос расписания на текущий день или на неделю 📆.

3. **Оценки**:
    - Просмотр оценок за текущий день или неделю в зависимости от настроек.

4. **Настройки пользователя**:
    - Настройка отображения домашних заданий (на день или неделю) и уведомлений (
      включены/выключены).
    - Все настройки сохраняются и могут быть изменены в любой момент ⏳.

5. **Логирование**:
    - Все действия пользователей и ошибки записываются с помощью библиотеки `loguru`, что упрощает
      мониторинг и отладку бота 🔍.

### Технические детали

#### Установка

1. Клонируйте репозиторий: `git clone https://github.com/Lynx20wz/school_tg_bot`.
2. Установите зависимости: `pip install -r requirements.txt`.
3. Запустите бота: `python .` или `Start_tg_bot.cmd`.

#### Допустимые аргументы запуска

- `-back` - бэкап базы данных не будет загружаться при запуске бота.
- `-debug` - бот будет запускаться в режиме отладки (дополнительные логи).

#### Используемые библиотеки

- [![
  `Aiogram`](https://img.shields.io/badge/aiogram-3.14.0-blue?style=flat-square)](https://pypi.org/project/aiogram/) —
  асинхронная библиотека для работы с Telegram API 📞.
- [![
  `Aiosqlite`](https://img.shields.io/badge/aiosqlite-0.20.0-green?style=flat-square)](https://pypi.org/project/aiosqlite/) —
  асинхронная работа с базами данных SQLite 🗄️.
- [![
  `Loguru`](https://img.shields.io/badge/loguru-0.7.3-red?style=flat-square)](https://pypi.org/project/loguru/) —
  логирование действий и ошибок 🔍.
- [![
  `Requests`](https://img.shields.io/badge/requests-2.32.2-pink?style=flat-square)](https://pypi.org/project/requests/) —
  HTTP-запросы к школьному порталу для получения расписаний и заданий 🚀.
- ~~[![
  `Selenium`](https://img.shields.io/badge/selenium-4.29.0-orange?style=flat-square)](https://pypi.org/project/selenium/) —
  парсинг токенов авторизации 🔑 (устарело).~~

<details>
<summary>Структура проекта</summary>

##### Корень

- `__main__.py` — точка входа в программу.
- `start_tg_bot.cmd` — скрипт для быстрого запуска бота в терминале.
- `LICENSE` — лицензия проекта.
- `README.md` — описание проекта.
- `pyproject.toml` — конфигурация проекта.
- `requirements.txt` — зависимости бота.

##### bot

> bin
> - `bot.py` — основная логика взаимодействия с Telegram API.

> classes
> - `BaseData.py` — класс для работы с базой данных (SQLite).
> - `UserClass.py` — класс для хранения данных пользователя.
> - `Homework.py` — класс для обработки домашних заданий.
> - `Parser.py` — класс для парсинга данных "Моя школа".

> filters
> - `is_admin.py` — фильтр для администраторов.

> handlers
> - `registration.py` — обработка авторизации и получения токена.
> - `debug.py` — функции для отладки.
> - `unknown.py` — обработка неизвестных сообщений.

> utils
> - ~~`get_token.py` — получение токена (устарело)~~.
> - `Keyboards.py` — функции для создания клавиатур `aiogram`.
> - `Exceptions.py` — пользовательские исключения.

</details>

---

### TODO-лист

#### Основные задачи 🛠️

- [x] ([6d42](https://github.com/Lynx20wz/school_tg_bot/commit/6d4270b)) Авторизация пользователей.
- [x] ([e0ae](https://github.com/Lynx20wz/school_tg_bot/commit/e0aecf3)) База данных (SQLite).
- [x] ([4c95](https://github.com/Lynx20wz/school_tg_bot/commit/4c95aa7b)) Уведомления об отсутствии
  токена для заданий, оценок и расписания.
- [ ] Система API "Моя школа" на основе ООП:
    - [x] ([29e6](https://github.com/Lynx20wz/school_tg_bot/commit/29e6e3fa)) Класс `Homework`.
    - [x] ([003e](https://github.com/Lynx20wz/school_tg_bot/commit/003e9a54)) Класс `Parser`.
    - [ ] Класс `Schedule`.
    - [ ] Класс `Grades`.
    - [ ] Класс API "Моя школа".
- [ ] Чек-лист подготовки школьных принадлежностей 📝✅.
- [ ] Уведомления о новых оценках 🔔.
- [ ] Разворачивание на автономном сервере.
- [ ] Уведомления о новых заданиях и оценках после уроков.
- [ ] Поддержка других школьных дневников.
- [ ] Логирование на уровне middleware.
- [ ] Кеширование с использованием **Redis**.

#### Решения заданий 🔢✅

- [ ] Автоматическая отправка ответов на цифровые задания.
- [ ] Собственная система решений (мечта).
- [ ] Автоматическое решение цифровых заданий.

#### Настройки ⚙️

- [x] ([5f43](https://github.com/Lynx20wz/school_tg_bot/commit/5f4301fd)) Выбор отображения
  заданий (день/неделя) 🛠️.
- [x] ([5f43](https://github.com/Lynx20wz/school_tg_bot/commit/5f4301fd)) Управление уведомлениями
  🔔.

---

### Как внести вклад

1. Сделайте форк репозитория.
2. Внесите изменения.
3. Создайте Pull Request.

---

### Лицензия

Проект распространяется под лицензией MIT. Подробности — в файле [LICENSE](LICENSE).

---

"Спасибо за внимание!" — [Lynx20wz](https://github.com/Lynx20wz)

</details>