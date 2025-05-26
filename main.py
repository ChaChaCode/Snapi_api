import asyncio
import logging
import aiohttp
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

# Настройки вашего бота
BOT_TOKEN = "ВАШ-ТОКЕН-БОТА"

# SNAPI настройки (ваш выданный API)
SNAPI_URL = "https://snapi.fun/api/api-keys"
API_KEY = "ВАШ-АПИ-SNAPI"

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def check_user_dialog(user_id: int) -> dict:
    """Проверяет диалог пользователя с основным ботом через SNAPI"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{SNAPI_URL}/check-dialog",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={"user_id": user_id},
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"status": "error", "message": "Неверный API ключ"}
                elif response.status == 429:
                    return {"status": "error", "message": "Превышены лимиты API"}
                else:
                    error_text = await response.text()
                    return {"status": "error", "message": f"HTTP {response.status}: {error_text}"}
    except asyncio.TimeoutError:
        return {"status": "error", "message": "Таймаут запроса к API"}
    except Exception as e:
        logger.error(f"Ошибка при запросе к SNAPI: {str(e)}")
        return {"status": "error", "message": f"Ошибка подключения: {str(e)}"}

async def get_api_info() -> dict:
    """Получает информацию об API через endpoint GET /api-info"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{SNAPI_URL}/api-info",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"status": "error", "message": "Неверный API ключ"}
                elif response.status == 429:
                    return {"status": "error", "message": "Превышены лимиты API"}
                else:
                    error_text = await response.text()
                    return {"status": "error", "message": f"HTTP {response.status}: {error_text}"}
    except asyncio.TimeoutError:
        return {"status": "error", "message": "Таймаут запроса к API"}
    except Exception as e:
        logger.error(f"Ошибка при запросе к SNAPI (api-info): {str(e)}")
        return {"status": "error", "message": f"Ошибка подключения: {str(e)}"}

async def get_usage_stats() -> dict:
    """Получает статистику использования через endpoint GET /usage-stats"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{SNAPI_URL}/usage-stats",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"status": "error", "message": "Неверный API ключ"}
                elif response.status == 429:
                    return {"status": "error", "message": "Превышены лимиты API"}
                else:
                    error_text = await response.text()
                    return {"status": "error", "message": f"HTTP {response.status}: {error_text}"}
    except asyncio.TimeoutError:
        return {"status": "error", "message": "Таймаут запроса к API"}
    except Exception as e:
        logger.error(f"Ошибка при запросе к SNAPI (usage-stats): {str(e)}")
        return {"status": "error", "message": f"Ошибка подключения: {str(e)}"}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Стартовое сообщение"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Проверить мой диалог", callback_data="check_my_dialog")],
        [InlineKeyboardButton(text="📊 Статистика API", callback_data="usage_stats")],
        [InlineKeyboardButton(text="ℹ️ Информация об API", callback_data="api_info")],
        [InlineKeyboardButton(text="ℹ️ О боте", callback_data="info")]
    ])
    text = (
        f"🤖 Тестовый бот SNAPI\n\n"
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"🎯 Этот бот взаимодействует с SNAPI API\n\n"
        f"📱 Ваш ID: {message.from_user.id}"
    )
    await message.answer(text, reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "check_my_dialog")
async def check_my_dialog(callback_query: types.CallbackQuery):
    """Проверяет диалог текущего пользователя"""
    await callback_query.answer("🔍 Проверяем...")
    user_id = callback_query.from_user.id
    await callback_query.message.edit_text(
        f"🔍 Проверка диалога\n\n"
        f"👤 User ID: {user_id}\n"
        f"⏳ Отправляем запрос к SNAPI..."
    )
    result = await check_user_dialog(user_id)
    if result.get("status") == "found":
        status_emoji = "✅"
        status_text = "Диалог найден!"
        description = "У вас есть диалог с основным ботом"
    elif result.get("status") == "not_found":
        status_emoji = "❌"
        status_text = "Диалог не найден"
        description = "Вы ещё не взаимодействовали с основным ботом"
    else:
        status_emoji = "⚠️"
        status_text = "Ошибка"
        description = result.get("message", "Неизвестная ошибка")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Проверить снова", callback_data="check_my_dialog")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_start")]
    ])
    result_text = (
        f"🔍 Результат проверки\n\n"
        f"👤 User ID: {user_id}\n"
        f"{status_emoji} Статус: {status_text}\n"
        f"📝 Описание: {description}\n\n"
        f"🔧 Техническая информация:\n"
        f"<pre>{json.dumps(result, indent=2, ensure_ascii=False)}</pre>"
    )
    await callback_query.message.edit_text(
        result_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(lambda c: c.data == "api_info")
async def show_api_info(callback_query: types.CallbackQuery):
    """Показывает информацию об API"""
    await callback_query.answer("ℹ️ Запрашиваем информацию об API...")
    await callback_query.message.edit_text(
        f"ℹ️ Информация об API\n\n"
        f"⏳ Отправляем запрос к SNAPI..."
    )
    result = await get_api_info()
    status_emoji = "✅" if result.get("status") != "error" else "⚠️"
    status_text = "Информация получена" if result.get("status") != "error" else "Ошибка"
    description = result.get("message", "Данные об API получены") if result.get("status") != "error" else result.get("message", "Неизвестная ошибка")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Запросить снова", callback_data="api_info")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_start")]
    ])
    result_text = (
        f"ℹ️ Информация об API\n\n"
        f"{status_emoji} Статус: {status_text}\n"
        f"📝 Описание: {description}\n\n"
        f"🔧 Техническая информация:\n"
        f"<pre>{json.dumps(result, indent=2, ensure_ascii=False)}</pre>"
    )
    await callback_query.message.edit_text(
        result_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(lambda c: c.data == "usage_stats")
async def show_usage_stats(callback_query: types.CallbackQuery):
    """Показывает статистику использования API"""
    await callback_query.answer("📊 Запрашиваем статистику...")
    await callback_query.message.edit_text(
        f"📊 Статистика API\n\n"
        f"⏳ Отправляем запрос к SNAPI..."
    )
    result = await get_usage_stats()
    status_emoji = "✅" if result.get("status") != "error" else "⚠️"
    status_text = "Статистика получена" if result.get("status") != "error" else "Ошибка"
    description = result.get("message", "Статистика использования API") if result.get("status") != "error" else result.get("message", "Неизвестная ошибка")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Запросить снова", callback_data="usage_stats")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_start")]
    ])
    result_text = (
        f"📊 Статистика API\n\n"
        f"{status_emoji} Статус: {status_text}\n"
        f"📝 Описание: {description}\n\n"
        f"🔧 Техническая информация:\n"
        f"<pre>{json.dumps(result, indent=2, ensure_ascii=False)}</pre>"
    )
    await callback_query.message.edit_text(
        result_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(lambda c: c.data == "info")
async def show_info(callback_query: types.CallbackQuery):
    """Показывает информацию о боте"""
    await callback_query.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_start")]
    ])
    info_text = (
        f"ℹ️ Информация о боте\n\n"
        f"🤖 Назначение: Тестирование SNAPI API\n"
        f"🔗 API URL: {SNAPI_URL}\n"
        f"🔑 API Key: {API_KEY[:20]}...\n\n"
        f"🎯 Что делает бот:\n"
        f"• Подключается к SNAPI API\n"
        f"• Проверяет диалоги пользователей\n"
        f"• Запрашивает информацию об API\n"
        f"• Показывает статистику использования\n\n"
        f"💡 Как использовать:\n"
        f"1. Выберите действие из меню\n"
        f"2. Бот отправит запрос к SNAPI\n"
        f"3. Получите результат"
    )
    await callback_query.message.edit_text(
        info_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(lambda c: c.data == "back_to_start")
async def back_to_start(callback_query: types.CallbackQuery):
    """Возврат в главное меню"""
    await callback_query.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Проверить мой диалог", callback_data="check_my_dialog")],
        [InlineKeyboardButton(text="📊 Статистика API", callback_data="usage_stats")],
        [InlineKeyboardButton(text="ℹ️ Информация об API", callback_data="api_info")],
        [InlineKeyboardButton(text="ℹ️ О боте", callback_data="info")]
    ])
    text = (
        f"🤖 Тестовый бот SNAPI\n\n"
        f"👋 Привет, {callback_query.from_user.first_name}!\n\n"
        f"🎯 Этот бот взаимодействует с SNAPI API\n\n"
        f"📱 Ваш ID: {callback_query.from_user.id}"
    )
    await callback_query.message.edit_text(text, reply_markup=keyboard)

async def main():
    """Запуск бота"""
    logger.info("🚀 Запуск тестового бота SNAPI...")
    logger.info(f"🔗 Подключение к API: {SNAPI_URL}")
    logger.info(f"🔑 API Key: {API_KEY[:20]}...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
