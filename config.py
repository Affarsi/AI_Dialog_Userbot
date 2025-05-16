from dataclasses import dataclass

@dataclass
class Config:
    api_id = 25585008 #
    api_hash = '86d25376e46f2d13ab75be1e0301313f' #
    bot_token = "7617336613:AAEz95VLn0kAoO7vR_9LQbxz4CXfrIpHKrM" #
    chad_gpt_token = 'chad-6452d80c08c94cdda633a618ae99973dh9rsdn4y'
    admin_ids = [902966420, 6094120092, 6991273215]
    sqlalchemy_url = 'sqlite+aiosqlite:///bot/database/db.sqlite3' # заменить на root