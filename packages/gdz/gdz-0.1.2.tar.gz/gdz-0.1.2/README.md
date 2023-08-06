<h1 align="center">gdz</h1>
<p align="center">
    Враппер API приложения <a href="https://play.google.com/store/apps/details?id=com.gdz_ru">ГДЗ: мой решебник</a>.
    <br /><br />
    <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
</p>

## Установка
```sh
pip install https://github.com/crinny/gdz/archive/master.zip
``` 

## Пример
```python
from gdz import GDZ

gdz = GDZ()

for book in gdz.books:
    if "Алгебра" in book.title:
        print(book.title)
        for entry in gdz.book_structure(book):
            print(entry.title)
            for task in entry.tasks:
                print(" -> " + task.title, end=", ")
            print()
        print()
```