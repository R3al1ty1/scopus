import asyncio

from aiogram import Bot, Dispatcher
from config.config import Config, load_config
from handlers import service_handlers, flow_handlers
from dialogs import dialogs
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from aiogram_dialog import setup_dialogs


def filter_by_stage(stage : int) -> bool :
    a = 1
    return True




# Функция конфигурирования и запуска бота
async def main() -> None:

    # Загружаем конфиг в переменную config
    config: Config = load_config(".env")

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(dialogs.main_menu)
    dp.include_router(service_handlers.router)
    dp.include_router(flow_handlers.router)
    
    setup_dialogs(dp)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
