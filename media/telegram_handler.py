import re
import time
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
import requests
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from backend import settings
from .models import Telegram


class TelegramHandler:
    def __init__(self, offset):
        self.channel = None
        self.messages = []
        self.offset = 0



    async def __aiter__(self):
        self.client = TelegramClient(
            settings.TELETHON_BOT_TOKEN,
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
        )

        if not self.client.is_connected():
            await self.client.start()

    async def get_elements(self, offset=0):

        await self.__aiter__()

        try:
            self.channel = await self.client.get_entity('hweifbwifjbwjvb')
            group_id = 0
            posts = await self.client(GetHistoryRequest(
                peer=self.channel,
                limit=100,
                add_offset=offset,
                offset_id=0,
                min_id=0,
                max_id=0,
                offset_date=None,
                hash=0
            ))

            for message in posts.messages:
                if message.grouped_id:
                    if message.grouped_id == group_id:
                        continue
                    group_id = message.grouped_id
                    await create_telegram_record(message_id=message.id)

            # print(message.id)
            await self.client.disconnect()
            await self.get_elements(offset+100)

            #     page = self.edit_page_source(message.id)
            #
            #     self.messages.append(page)
            #
            # return (
            #     self.messages
            # )

            return ["true"]

        except Exception as error:
            raise error
        finally:
            await self.client.disconnect()




@sync_to_async
def create_telegram_record(message_id):
    print(message_id)
    Telegram.objects.create(id=message_id)

