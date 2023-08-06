import requests

from gdz.types.book import Book
from gdz.types.class_ import Class
from gdz.types.structure_entry import StructureEntry
from gdz.types.subject import Subject


class GDZ:
    API_ENDPOINT = "https://gdz-ru.com"

    def __init__(self):
        self.session = requests.Session()
        self.main_info = requests.get(self.API_ENDPOINT).json()

    @property
    def classes(self):
        return [Class(**external_data) for external_data in self.main_info["classes"]]

    @property
    def subjects(self):
        return [
            Subject(**external_data) for external_data in self.main_info["subjects"]
        ]

    @property
    def books(self):
        return [Book(**external_data) for external_data in self.main_info["books"]]

    def book_structure(self, book: Book):
        structure = requests.get(self.API_ENDPOINT + book.url).json()["structure"]
        return [StructureEntry(**external_data) for external_data in structure]
