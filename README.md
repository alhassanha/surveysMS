#SurveysMS API
API для системы опросов пользователей

##### Функционал для администратора системы:
- авторизация в системе (регистрация не нужна)
- добавление/изменение/удаление опросов. Атрибуты опроса: название, дата старта, дата окончания, описание. После создания поле "дата старта" у опроса менять нельзя
- добавление/изменение/удаление вопросов в опросе. Атрибуты вопросов: текст вопроса, тип вопроса (ответ текстом, ответ с выбором одного варианта, ответ с выбором нескольких вариантов)

##### Функционал для пользователей системы:
- получение списка активных опросов
- прохождение опроса: опросы можно проходить анонимно, в качестве идентификатора пользователя в API передаётся числовой ID, по которому сохраняются ответы пользователя на вопросы; один пользователь может участвовать в любом количестве опросов
- получение пройденных пользователем опросов с детализацией по ответам (что выбрано) по ID уникальному пользователя

##### Использовать следующие технологии: 
Django 2.2.10, Django REST framework.

## Установка:
1. Клонировать репозиторий
2. Создать и настроить контейнкров Docker:
    - 'docker-compose build'
    - 'docker-compose up -d'
3. Проводить миграции:
    - 'docker-compose run backend python manage.py makemigrations'
    - 'docker-compose run backend python manage.py migrate'
4. Создать суперпользователя:
    - 'docker-compose run backend python manage.py createsuperuser'
5. Добавить surveysms.local в файл 'hosts' (в linux: /etc/hosts), чтобы получить доступ к проекту на http://surveysms.local:8080, или использовать домашний домен http://localhost:8080.
## Документация по API
### Функционал для администратора системы:
##### 1- Алгоритм авторизации пользователей:
- Пользователь отправляет POST запрос с параметрами `username` и `password` на `/api/auth/`, в ответе на запрос ему приходит `token` (JWT-токен) в поле access.
- При отправке запроса передавайте токен в заголовке Authorization: token <токен>
##### 2- Добавление опросов (POST):
- Права доступа: `Администратор`
- URL: `/api/survey/`
- Тело запроса (за обязательными полями следуют \*): `name`*, `start_date`, `end_date`, `description`
##### 3- Изменение опросов (Patch/PUT):
- Права доступа: `Администратор`
- URL: `/api/survey/<survey_id>/`
- Тело запроса: `name`, `end_date`, `description`
#### 4- Удаление опросов (DELETE):
- Права доступа: `Администратор`
- URL: `/api/survey/<survey_id>/`
#### 5- Добавление вопросов к опросу (POST)
- Права доступа: `Администратор`
- URL: `/api/question/`
- Тело запроса: `text`*, `type`(TEXT or SINGLE or MULTIPLE), `survey`*, `options`(Список текстов для добавления опций к вопросу)
##### 6- Изменение вопросов (PATCH/PUT)
- Права доступа: `Администратор`
- URL: `/api/question/<question_id>/`
- Тело запроса: `text`, `type`, `survey`, `options`
##### 7- Удаление вопросов (DELETE):
- Права доступа: `Администратор`
- URL: `/api/question/<question_id>/`

### Функционал для пользователей системы:
##### 1- Получение списка активных опросов (GET):
Этот API показывает администраторам все опросы, а неаутентифицированным пользователям показывает только активные опросы.
- Права доступа: `Любой пользователь`
- URL: `/api/survey/`
##### 2- Прохождение опроса (POST):
- Права доступа: `Любой пользователь`
- URL: `/api/survey/<poll_id>/submit/`
- Тело запроса:
   - `participant` (int): Не требуется в случае аутентифицированного пользователя
   - `answers` (list): Ответы пользователя на все вопросы. Каждый ответ представляет собой объект JSON, который содержит 2 из следующих 3 ключей:
        - `question`*: id вопроса
        - `options`: список выбранных вариантов
        - `text`: текст ответа
   - пример:
    ```{
    "participant": 1,
    "answers": [
        {
            "question": 14,
            "options": [39,40]
        },
        {
            "question": 16,
            "text": "some answer text for question in survey 7"
        },
        {
            "question": 15,
            "options": [43]
        }
    ]}
  ```
##### 3- Получение пройденных пользователем опросов (GET):
- Права доступа: `Любой пользователь`
- URL: `/api/answers/?user=<participant_id>`

##### 4- Получение детализации о пройденном опросе (GET):
- Права доступа: `Любой пользователь`
- URL: `/api/answers/<survey_id>/?user=<participant_id>`