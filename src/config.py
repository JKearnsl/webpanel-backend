import os
from functools import lru_cache
from typing import Optional
from dataclasses import dataclass
import configparser

from src.version import __version__
from dotenv import find_dotenv, load_dotenv


@dataclass
class RedisConfig:
    HOST: Optional[str]
    PASSWORD: Optional[str]
    USERNAME: Optional[str]
    PORT: Optional[int] = 6379


@dataclass
class DbConfig:
    REDIS: Optional[RedisConfig]


@dataclass
class Contact:
    NAME: Optional[str]
    URL: Optional[str]
    EMAIL: Optional[str]


@dataclass
class JWT:
    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str


@dataclass
class Base:
    TITLE: Optional[str]
    DESCRIPTION: Optional[str]
    VERSION: Optional[str]
    JWT: JWT
    CONTACT: Contact


@dataclass
class Config:
    DEBUG: bool
    IS_SECURE_COOKIE: bool
    BASE: Base
    DB: DbConfig


@lru_cache()
def load_ini_config(path: str | os.PathLike, encoding="utf-8") -> Config:
    """
    Loads config from file

    :param path: *.ini
    :param encoding:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(filenames=path, encoding=encoding)

    return Config(
        DEBUG=bool(int(os.getenv('DEBUG', 1))),
        IS_SECURE_COOKIE=bool(config["BASE"]["IS_SECURE_COOKIE"]),
        BASE=Base(
            TITLE=config["BASE"]["TITLE"],
            DESCRIPTION=config["BASE"]["DESCRIPTION"],
            VERSION=__version__,
            CONTACT=Contact(
                NAME=config["CONTACT"]["NAME"],
                URL=config["CONTACT"]["URL"],
                EMAIL=config["CONTACT"]["EMAIL"]
            ),
            JWT=JWT(
                ACCESS_SECRET_KEY=config["JWT"]["ACCESS_SECRET_KEY"],
                REFRESH_SECRET_KEY=config["JWT"]["REFRESH_SECRET_KEY"]
            )
        ),
        DB=DbConfig(
            REDIS=RedisConfig(
                HOST=config["REDIS"]["HOST"],
                USERNAME=config["REDIS"]["USERNAME"],
                PASSWORD=config["REDIS"]["PASSWORD"],
                PORT=int(config["REDIS"]["PORT"])
            )
        )
    )


@lru_cache()
def load_env_config(file_name: str = None) -> Config:
    """
    Loads config from .env file

    """
    if not file_name:
        env_file = find_dotenv()
    else:
        env_file = find_dotenv(file_name)

    if env_file:
        load_dotenv(env_file)
    else:
        raise EnvironmentError("No .env file found. Using Environment Variables.")

    return Config(
        DEBUG=bool(int(os.getenv('DEBUG', 1))),
        IS_SECURE_COOKIE=bool(os.getenv('BASE_IS_SECURE_COOKIE')),
        BASE=Base(
            TITLE=os.getenv('BASE_TITLE'),
            DESCRIPTION=os.getenv('BASE_DESCRIPTION'),
            VERSION=__version__,
            CONTACT=Contact(
                NAME=os.getenv('CONTACT_NAME'),
                URL=os.getenv('CONTACT_URL'),
                EMAIL=os.getenv('CONTACT_EMAIL')
            ),
            JWT=JWT(
                ACCESS_SECRET_KEY=os.getenv('JWT_ACCESS_SECRET_KEY'),
                REFRESH_SECRET_KEY=os.getenv('JWT_REFRESH_SECRET_KEY')
            )
        ),
        DB=DbConfig(
            REDIS=RedisConfig(
                HOST=os.getenv('REDIS_HOST'),
                USERNAME=os.getenv('REDIS_USERNAME'),
                PASSWORD=os.getenv('REDIS_PASSWORD'),
                PORT=int(os.getenv('REDIS_PORT'))
            )
        )
    )
