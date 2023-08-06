import requests

from gdz.types.book import Book
from gdz.types.class_ import Class
from gdz.types.subject import Subject
from gdz.types.structure_entry import StructureEntry


class GDZ:
    API_ENDPOINT = "https://gdz-ru.com"

    def __init__(self):
        self.main_info = requests.get(self.API_ENDPOINT).json()

        self.classes = [
            Class(**external_data) for external_data in self.main_info["classes"]
        ]
        self.subjects = [
            Subject(**external_data) for external_data in self.main_info["subjects"]
        ]
        self.books = [
            Book(**external_data) for external_data in self.main_info["books"]
        ]

    def book_structure(self, book: Book):
        structure = requests.get(self.API_ENDPOINT + book.url).json()["structure"]
        return [StructureEntry(**external_data) for external_data in structure]
