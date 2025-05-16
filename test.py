from pyrogram import Client

from config import Config

client = Client(
    name='79003564078',
    workdir="bot/pyrogram/sessions",
    api_id=Config.api_id,
    api_hash=Config.api_hash,
)

client.start()
print(client.get_me())