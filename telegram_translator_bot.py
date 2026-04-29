import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from deep_translator import GoogleTranslator

API_TOKEN = "8624162973:AAHQHGF3v3MLAzeh24wPV1gIUHNkGG4S-zk"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

LANGUAGES = {
    "en": "🇬🇧 Английский",
    "ru": "🇷🇺 Русский",
    "de": "🇩🇪 Немецкий",
    "fr": "🇫🇷 Французский",
    "zh-CN": "🇨🇳 Китайский",
    "ar": "🇸🇦 Арабский",
    "es": "🇪🇸 Испанский",
    "kk": "🇰🇿 Казахский",
}

# Хранилище
user_texts = {}


def is_russian(text: str) -> bool:
    return any('а' <= ch.lower() <= 'я' or ch.lower() == 'ё' for ch in text)


def get_lang_keyboard(exclude_lang: str = None) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for code, name in LANGUAGES.items():
        if code == exclude_lang:
            continue
        row.append(InlineKeyboardButton(text=name, callback_data=f"lang:{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Привет! Отправь мне любой текст, и я спрошу, на какой язык перевести. 🌍"
    )


@dp.message()
async def handle_text(message: types.Message):
    text = message.text
    user_texts[message.from_user.id] = text

    # Определяем язык источника для исключения из кнопок
    source_lang = "ru" if is_russian(text) else "en"

    await message.answer(
        "На какой язык перевести?",
        reply_markup=get_lang_keyboard(exclude_lang=source_lang)
    )


@dp.callback_query(F.data.startswith("lang:"))
async def handle_lang_choice(callback: types.CallbackQuery):
    target_lang = callback.data.split(":")[1]
    user_id = callback.from_user.id
    text = user_texts.get(user_id)

    if not text:
        await callback.message.answer("❌ Текст не найден. Отправь его заново.")
        await callback.answer()
        return

    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        lang_name = LANGUAGES.get(target_lang, target_lang)
        await callback.message.answer(f"{lang_name}:\n{translated}")
    except Exception as e:
        logging.error(f"Translation error: {e}")
        await callback.message.answer("❌ Ошибка перевода. Попробуй ещё раз.")

    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
