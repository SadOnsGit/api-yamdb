# api_yamdb
Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». и жанры (например, «Сказка», «Рок» или «Артхаус»).
Добавлять произведения, категории и жанры может только администратор.
Пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти, из пользовательских оценок формируется усреднённая оценка произведения — рейтинг. Пользователи могут оставлять комментарии к отзывам.

## Стек
- Python 3.12.3
- Django 5.1.1
- djangorestframework 3.15.2

## Как запустить проект(для Windows):

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/SadOnsGit/api-yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать миграции:

```
python3 manage.py makemigrations
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

## Как запустить проект(для Linux):

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/SadOnsGit/api-yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать миграции:

```
python3 manage.py makemigrations
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

## Документация к API:
После запуска проекта полная документация будет доступна по адресу:
```
http://127.0.0.1:8000/redoc/
```

## Авторы
Aidar Iskhakov https://github.com/SadOnsGit

YanaKachalova https://github.com/YanaKachalova

Danila-Py https://github.com/Danila-Py
