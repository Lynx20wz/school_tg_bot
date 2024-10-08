# Документация для school_tg_bot 🚀

## Описание проекта

Этот проект представляет собой Telegram-бота, созданного для упрощения взаимодействия учеников с информацией о
расписании и домашних заданиях 📚. Бот предоставляет пользователям возможность быстро и удобно получать актуальную
информацию о занятиях, домашних заданиях и настройках уведомлений.

### Основные функции:

1. **Получение расписания**:
  - Пользователи могут запрашивать расписание на текущий день или на неделю 📆.

2. **Домашнее задание**:
  - Бот позволяет пользователям видеть свои домашние задания на текущий день или на всю неделю в зависимости от настроек
    🛠️.
  - Домашние задания также загружаются с сайта школы, что обеспечивает актуальность данных 💾.

3. **Настройки пользователя**:
  - Пользователи могут настраивать предпочтения получения информации о домашних заданиях (на день или на неделю) и
    уведомлениях (включенные или выключенные).
  - Все настройки удобно сохраняются и при необходимости могут быть изменены в любое время ⏳.

4. **Логирование**:
  - Все действия пользователей и ошибки логируются с помощью библиотеки `loguru`, что позволяет отслеживать работу бота
    и быстро находить возможные проблемы 🔍.

### Технические детали:

- **Основные библиотеки**:
  - `telebot`: библиотека для работы с API Telegram.
  - `dotenv`: для загрузки переменных окружения 🔄.
  - `loguru`: для логирования 🔍.
  - `requests`: для выполнения HTTP-запросов к школьному порталу для получения расписаний и домашних заданий 🚀.
  - `json`: для работы с форматом данных JSON 📃.

- **Структура кода**:
  - Основная логика взаимодействия с пользователем реализована в файле `main.py`.
  - Функции для парсинга данных с сайта школы сгруппированы в файле `Parser_school.py`.
  - Информация об расписании и нужных вещах для уроков храниться в `schedule.json`.
  - Для быстрого запуска бота в терминале используется файл `Start tg bot.cmd`.

### TODO-лист:

Основная работа 🛠️:

- [x] Реализовать систему кэша
- [ ] Чек-лсит сборки портфеля 📝✅
- [ ] Уведомления о новом дз сразу после соответствующего урока
- [ ] Выложить код на автономный сервер
- [ ] Авторизация других пользователей
  - [ ] Уведомления о полученных оценках 🔔

ГДЗ 🔢✅:

- [ ] Автоматическая отправка ответов на цдз
- [ ] Написать свою систему (мечта)

Настройки ⚙️:

- [x] Настройка дз день/неделя 🛠️
- [x] Настройка уведомлений 🔔

Проект нацелен на оптимизацию учебного процесса, позволяя учащимся быть в курсе своих обязанностей и обеспечивая легкий
доступ к необходимой информации (в отличие от школьного портала 😁).

# Техническая документация

## Классы

### `user_class`

Символизирует пользователя.

### Атрибуты:

- **`username`**: Имя пользователя.
- **`userid`**: ID пользователя.
- **`debug`**: Флаг отладки.
- **`setting_dw`**: Флаг настройки уведомлений.
- **`setting_notification`**: Флаг уведомлений.
- **`data`**: Кортеж, содержащий все вышеперечисленные данные пользователя.

### Методы:

- **`__init__`**: Инициализирует объект пользователя, проверяет наличие пользователя в массиве и обновляет его
  настройки, если он уже существует.
  - **Аргументы**: `username` (str), `userid` (int), `debug` (bool), `setting_dw` (bool), `setting_notification` (bool)
  - **Возвращает**: `cache_class`
- **`get_user_from_massive`**: Получает пользователя из списка пользователей по имени.
  - **Аргументы**: `username` (str)
  - **Возвращает**: `user_class`, или индекс user в массиве users, или Tuple с user.data
- **`get_user`**: Декоратор, который возвращает объект `user_class` по username из кэша.
  - **Аргументы**: `func`, `message` (Message), `userid` (int)
  - **Возвращает**: `user_class`
- **`save_settings`**: Сохраняет настройки пользователя и обновляет файл кэша.
  - **Аргументы**: `setting_dw` (bool), `setting_notification` (bool), `debug` (bool), `save_cache` (bool)
  - **Возвращает**: None

---

### `cache_class`

Хранит в себе словарь, созданный из файла кэша.

### Атрибуты:

- **`cache`**: Словарь, хранящий данные кэша.
- **`cache_file`**: Путь к файлу кэша.
- **`start_number`**: Номер запуска бота.

### Методы:

- **`__init__`**: Инициализирует кэш, читает данные из файла кэша и обновляет номер запуска, если это необходимо.
  - **Аргументы**: `cache_file` (str)
  - **Возвращает**: None
- **`cache_read`**: Читает файл кэша или создает новый с базовым содержанием, если файл отсутствует.
  - **Аргументы**: None
  - **Возвращает**: dict
- **`user_record`**: Записывает пользователя в файл кэша, если он не существует.
  - **Аргументы**: `user` (user_class)
  - **Возвращает**: None
- **`homework_record`**: Записывает домашнее задание в файл кэша.
  - **Аргументы**: `homework` (dict)
  - **Возвращает**: None

---

## Функции

#### `main_button`

Создает и возвращает клавиатуру с кнопками главного меню для взаимодействия с ботом.

- **Аргументы**: None
- **Возвращает**: `ReplyKeyboardMarkup`

---

#### `restart`

Перезапускает бота и отправляет уведомление каждому пользователю из кэша.

- **Аргументы**: None
- **Возвращает**: None

---

#### `start`

Обрабатывает команду `/start`, приветствует пользователя и отправляет ему информацию о боте.

- **Аргументы**: `message` (Message)
- **Возвращает**: None

---

#### `timetable`

Обрабатывает запрос на расписание и отправляет фотографию расписания с текстовой подписью, в которой указан текстовый
вариант расписания и предметы для соответствующего урока.

- **Аргументы**: `message` (Message)
- **Возвращает**: None

---

#### `homework`

Обрабатывает запрос на домашнее задание и отправляет его в зависимости от настроек пользователя. Домашнее задание
получает из метода `full_parse` модуля `Parser_school`.

- **Аргументы**: `message` (Message), `user` (user_class)
- **Возвращает**: None

---

#### `social_networks`

Отправляет пользователю ссылки на социальные сети.

- **Аргументы**: `message` (Message)
- **Возвращает**: None

---

#### `developer`

Выдает роль Developer, если ID совпадает с ID разработчика, который хранится в виртуальной среде (venv).

- **Аргументы**: `userid` (int)
- **Возвращает**: bool

---

#### `make_setting_button`

Создает клавиатуру настроек для пользователя.

- **Аргументы**: None
- **Возвращает**: `ReplyKeyboardMarkup`

---

#### `settings`

Отправляет пользователю информацию о текущих настройках и клавиатуру для изменения настроек.

- **Аргументы**: `message` (Message), `user` (user_class)
- **Возвращает**: None

---

#### `change_delivery`

Обрабатывает изменения настроек выдачи домашнего задания (на день или на неделю).

- **Аргументы**: `message` (Message), `user` (user_class)
- **Возвращает**: None

---

#### `change_notification`

Обрабатывает изменения настроек уведомлений (включить или выключ��ть).

- **Аргументы**: `message` (Message), `user` (user_class)
- **Возвращает**: None

---

#### `exit_settings`

Обрабатывает выход из меню настроек, сохраняет настройки в кэш и возвращает пользователя в главное меню.

- **Аргументы**: `message` (Message), `user` (user_class)
- **Возвращает**: None

---

#### `unknown_command`

Обрабатывает несуществующие команды и отправляет сообщение об ошибке.

- **Аргументы**: `message` (Message)
- **Возвращает**: None

---

### Если вы хотите внести свой вклад в проект, вы можете сделать это следующим образом:

1. **Форкните репозиторий**
2. Создайте новую ветку (`git checkout -b feature-name`).
3. Внесите свои изменения! 🛠️👍
4. Отправьте их на свой форк (`git push origin feature-name`).
5. Создайте Pull Request! ✅

---

### Лицензия:

Этот проект лицензирован под лицензией MIT. Подробности можно найти в файле [LICENSE](LICENSE).

---
"Спасибо за внимание!" - [Lynx20wz](https://github.com/Lynx20wz)
