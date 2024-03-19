from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str


@dataclass
class Database:
    base_name: str
    collection_name: str


@dataclass
class Config:
    tg_bot: TgBot
    database: Database


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN')
        ),
        database=Database(
            base_name=env('BASE_NAME'),
            collection_name=env('COLLECTION_NAME'),
        )
    )


config: Config = load_config()
