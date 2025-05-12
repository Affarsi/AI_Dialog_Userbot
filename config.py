from dataclasses import dataclass

@dataclass
class Config:
    api_id = 28303504 # ipred
    api_hash = '6b95c2599a5b310c077262530523dc8b' # ipred
    bot_token = "7617336613:AAEz95VLn0kAoO7vR_9LQbxz4CXfrIpHKrM" #test_kwork
    chad_gpt_token = 'chad-6452d80c08c94cdda633a618ae99973dh9rsdn4y'
    admin_ids = [902966420, 6094120092, 6991273215]
    sqlalchemy_url = 'sqlite+aiosqlite:///bot/database/db.sqlite3' # заменить на root