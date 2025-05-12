import time

from telethon import TelegramClient

# Remember to use your own values from my.telegram.org!
api_id = 2040
api_hash = 'b18441a1ff607e10a989891a5462e627'
proxy = ('socks5', "190.2.137.56", 9999, "rq7re0vcg1-res-country-GB-hold-query", "QLdSi1IVMFupLYiv")
client = TelegramClient('38641372174', api_id, api_hash, proxy=proxy)

async def main():
    me = await client.get_me()

    print(me.stringify())

    username = me.username
    print(username)
    print(me.phone)

with client:
    client.loop.run_until_complete(main())
