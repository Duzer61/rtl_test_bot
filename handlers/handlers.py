from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from services.service import process_message

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        'Привет! Это бот написан в качестве тестового задания для RTL.'
    )


@router.message()
async def handle_message(message: Message):
    reply_message: str = await process_message(message)
    await message.answer(reply_message, parse_mode='HTML')
