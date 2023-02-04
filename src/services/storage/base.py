import dataclasses
from enum import Enum, unique
from abc import ABC, abstractmethod
from typing import Optional, Union, IO


@dataclasses.dataclass
class File:
    filename: str
    content_type: str
    size: Optional[int]
    bytes: Optional[bytes]
    owner_id: int


class AbstractStorage(ABC):
    """Abstract storage class"""

    @abstractmethod
    async def __aenter__(self, *args, **kwargs):
        pass

    @abstractmethod
    async def __aexit__(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get(self, path: str) -> Optional[File]:
        """
        Получить файл из хранилища
        :param path:
        :return:
        """
        pass

    @abstractmethod
    async def save(self, path: str, file: Union[bytes, IO]) -> str:
        """
        Сохранить файл в хранилище
        :param path:
        :param file:
        """
        pass

    @abstractmethod
    async def delete(self, path: str) -> None:
        """
        Удалить файл из хранилища
        :param path:
        :return:
        """
        pass

    @abstractmethod
    async def get_meta(self, path: str):
        """
        Получить мета-информацию о файле
        :param path:
        """
        pass

    @abstractmethod
    async def rename(self, path: str, new_filename: str):
        """
        Переименовать файл
        :param path:
        :param new_filename:
        """
        pass

    @abstractmethod
    async def copy(self, path: str, new_path: str):
        """
        Копировать файл
        :param path:
        :param new_path:
        """
        pass

    @abstractmethod
    async def move(self, path: str, new_path: str):
        """
        Переместить файл
        :param path:
        :param new_path:
        """
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """
        Проверить существование файла
        :param path:
        :return:
        """
        pass

    @abstractmethod
    async def unzip(self, path: str, destination: str):
        """
        Распаковать архив
        :param path:
        :param destination:
        """
        pass
