from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram_dialog import DialogManager, StartMode
from database.requests import charge_request, new_user

from dialogs import dialogs
from handlers.service_handlers import process_payments_command


router = Router()

class FSMSearching(StatesGroup):   
    searching = State()

# Хендлер для команды /search
@router.message(Command(commands='search'), StateFilter(default_state))
async def process_search_command(message: Message, state: FSMContext, dialog_manager: DialogManager):
    chat_id = str(message.chat.id)
    username = str(message.chat.username)
    new_user(chat_id, username)
    if charge_request(chat_id=chat_id):
        await dialog_manager.start(dialogs.FSMFindPubs.choose_language, mode=StartMode.RESET_STACK)
    else:
        await message.answer("К сожалению, на вашем балансе закончились запросы.\nПриобретите их сейчас👇🏼")
        await process_payments_command(message)
        return

# Хендлер для нажатия кнопки search
@router.callback_query(F.data == "search_button_pressed", StateFilter(default_state))
async def process_search_button(callback: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    chat_id = str(callback.message.chat.id)
    username = str(callback.message.chat.username)
    new_user(chat_id, username)
    if charge_request(chat_id=chat_id):
        await dialog_manager.start(dialogs.FSMFindPubs.choose_language, mode=StartMode.RESET_STACK)
    else:
        await callback.message.answer("К сожалению, на вашем балансе закончились запросы.\nПриобретите их сейчас👇🏼")
        await process_payments_command(callback.message)
        return
