import logging
import asyncio
import random
from datetime import datetime, timezone
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.client.default import DefaultBotProperties

# 🔹 Конфиг
BOT_TOKEN = "8287116966:AAFNKvumWLiqiTclBjGUFlaVX2CG3GzLtiA"
CRYPTO_BOT_URL = "t.me/send?start=IVAKoNCjFdAM"
CARD_DETAILS = "2200700437767535 (Т-Банк)"
PRICE_RUB = "3000 ₽"
PRICE_USD = "37$"
PRODUCT_NAME_RU = "🌀 СБОРКА 87,000 СЛУЧАЙНЫХ ВИДЕО"
PRODUCT_NAME_EN = "🌀 COLLECTION OF 87,000 RANDOM VIDEOS"
PREVIEW_URL = "https://t.me/Agarthavipp_bot?start=BQADAQAD8AkAAv5DUEbUvW6_RS1lJhYE"
CHANNEL_URL = "https://t.me/+ccDKfWUgVKc3NTA0"

# 🔹 Память пользователей
USERS = {}
INVOICES = {}

# 🔹 Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 Инициализация бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# --- Клавиатуры ---
def main_menu_kb(lang="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Наши товары" if lang == "ru" else "📦 Our products", callback_data="products")],
        [InlineKeyboardButton(text="👤 Профиль" if lang == "ru" else "👤 Profile", callback_data="profile")],
        [InlineKeyboardButton(text="📞 Поддержка" if lang == "ru" else "📞 Support", callback_data="support")],
        [InlineKeyboardButton(text="🌐 Сменить язык" if lang == "ru" else "🌐 Change language", callback_data="change_lang")],
        [InlineKeyboardButton(text="📡 Наши каналы" if lang == "ru" else "📡 Our channels", url=CHANNEL_URL)]
    ])

def products_kb(lang="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить через карту" if lang == "ru" else "💳 Buy with card", callback_data="pay_card")],
        [InlineKeyboardButton(text="💰 Купить через Crypto Bot" if lang == "ru" else "💰 Buy with Crypto Bot", callback_data="pay_crypto")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

def profile_kb(lang="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

def pay_card_kb(lang="ru", invoice_id=0):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил" if lang == "ru" else "✅ I paid", callback_data=f"paid_card:{invoice_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

def pay_crypto_kb(lang="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Оплатить" if lang == "ru" else "💰 Pay", url=f"https://{CRYPTO_BOT_URL}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

def back_to_main_kb(lang="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

# --- Хэндлеры ---
@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])
    await message.answer("🌍 Выберите язык | Choose language:", reply_markup=kb)

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = "ru" if callback.data == "lang_ru" else "en"
    USERS[user_id] = {"lang": lang, "start": datetime.now(timezone.utc).isoformat()}
    await show_main_menu(callback.message, lang, delete_old=True)

async def show_main_menu(message, lang="ru", delete_old=False):
    text = "🏴 PIRAT SHOP\n\n📍 Главное меню:" if lang == "ru" else "🏴 PIRAT SHOP\n\n📍 Main menu:"
    if delete_old:
        try:
            await message.delete()
        except Exception:
            pass
    await message.answer(text, reply_markup=main_menu_kb(lang))

@dp.callback_query(F.data == "change_lang")
async def change_language(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])
    lang = USERS.get(callback.from_user.id, {}).get("lang", "ru")
    await callback.message.answer(
        "🌍 Выберите язык:" if lang == "ru" else "🌍 Choose language:",
        reply_markup=kb
    )

@dp.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    lang = USERS.get(callback.from_user.id, {}).get("lang", "ru")
    text = "📞 Поддержка @piratadmin_bot" if lang == "ru" else "📞 Support @piratadmin_bot"
    await callback.message.answer(text, reply_markup=back_to_main_kb(lang))

@dp.callback_query(F.data == "products")
async def show_products(callback: CallbackQuery):
    lang = USERS.get(callback.from_user.id, {}).get("lang", "ru")
    if lang == "ru":
        text = f"{PRODUCT_NAME_RU}\n💰 Цена: {PRICE_USD}\n👁 Предосмотр: {PREVIEW_URL}"
    else:
        text = f"{PRODUCT_NAME_EN}\n💰 Price: {PRICE_USD}\n👁 Preview: {PREVIEW_URL}"
    await callback.message.answer(text, reply_markup=products_kb(lang))

@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    lang = USERS.get(callback.from_user.id, {}).get("lang", "ru")
    if lang == "ru":
        text = f"👤 Ваш профиль\n\n🆔 ID: {callback.from_user.id}\n📅 Дата входа: {USERS[callback.from_user.id]['start']}"
    else:
        text = f"👤 Your profile\n\n🆔 ID: {callback.from_user.id}\n📅 Joined: {USERS[callback.from_user.id]['start']}"
    await callback.message.answer(text, reply_markup=back_to_main_kb(lang))

@dp.callback_query(F.data == "pay_card")
async def pay_card(callback: CallbackQuery):
    lang = USERS.get(callback.from_user.id, {}).get("lang", "ru")
    invoice_id = random.randint(1000, 9999)
    INVOICES[invoice_id] = {"method": "card", "user": callback.from_user.id}
    text = (
        f"✔️ Ваш счет №{invoice_id} создан и ожидает оплаты\n\n"
        f"Детали оплаты:\n\n• Карта: {CARD_DETAILS}\n• Сумма: {PRICE_RUB}"
        if lang == "ru" else
        f"✔️ Your invoice №{invoice_id} is created and waiting for payment\n\n"
        f"Payment details:\n\n• Card: {CARD_DETAILS}\n• Amount: {PRICE_RUB}"
    )
    await callback.message.answer(text, reply_markup=pay_card_kb(lang, invoice_id))

@dp.callback_query(F.data == "pay_crypto")
async def pay_crypto(callback: CallbackQuery):
    lang = USERS.get(callback.from_user.id, {}).get("lang", "ru")
    invoice_id = random.randint(1000, 9999)
    INVOICES[invoice_id] = {"method": "crypto", "user": callback.from_user.id}
    text = (
        f"✔️ Ваш счет №{invoice_id} создан и ожидает оплаты\n\n"
        f"Детали оплаты:\n\n• Сумма: {PRICE_USD}"
        if lang == "ru" else
        f"✔️ Your crypto invoice №{invoice_id} is created and waiting for payment\n\n"
        f"Payment details:\n\n• Amount: {PRICE_USD}"
    )
    await callback.message.answer(text, reply_markup=pay_crypto_kb(lang))

@dp.callback_query(F.data.startswith("paid_card:"))
async def confirm_paid(callback: CallbackQuery):
    lang = USERS.get(callback.from_user.id, {}).get("lang", "ru")
    text = (
        "💰 Вы произвели оплату?\nПожалуйста, предоставьте скриншот для быстрой обработки вашего заказа:"
        if lang == "ru" else
        "💰 Did you make a payment?\nPlease provide a screenshot for faster order processing:"
    )
    await callback.message.answer(text, reply_markup=back_to_main_kb(lang))

@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    lang = USERS.get(callback.from_user.id, {}).get("lang", "ru")
    await show_main_menu(callback.message, lang, delete_old=True)

# --- Запуск ---
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("🚀 Запуск бота...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")

if __name__ == "__main__":
    asyncio.run(main())
