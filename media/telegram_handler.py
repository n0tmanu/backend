from asgiref.sync import sync_to_async
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from backend import settings
from .models import Telegram

class TelegramHandler:
    def __init__(self):
        self.channel = None
        self.client = None
        self.offset = 0

    async def __aiter__(self):
        """
        Asynchronous iterator to initialize the TelegramClient.
        """
        self.client = TelegramClient(
            settings.TELETHON_BOT_TOKEN,
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
        )
        if not self.client.is_connected():
            await self.client.start()

    async def get_messages(self, offset=0):
        """
        Asynchronously fetches messages from Telegram and creates records in the database.
        """
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
                    status = await create_telegram_record(message_id=message.id)
                    if not status:
                        break

            await self.client.disconnect()
            await self.get_messages(offset+100)

        except Exception as error:
            raise error
        finally:
            await self.client.disconnect()

        return Telegram.objects.all().count()

@sync_to_async
def create_telegram_record(message_id):
    """
    Asynchronously creates a Telegram record in the database.
    Returns False if the object already exists, otherwise returns the object.
    """
    try:
        telegram_object, created = Telegram.objects.get_or_create(id=message_id)
        return telegram_object if created else False
    except Exception as e:
        print(f"Error creating Telegram record: {e}")
        return False
