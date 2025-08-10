from dataclasses import dataclass

@dataclass
class Config:
    bot_token = "" #test_kwork
    admin_ids = [902966420, 6094120092, 6991273215]
    sqlalchemy_url = 'sqlite+aiosqlite:///bot/database/db.sqlite3'
