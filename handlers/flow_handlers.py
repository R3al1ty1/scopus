from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram_dialog import DialogManager, StartMode

from dialogs import dialogs


router = Router()

class FSMSearching(StatesGroup):   
    searching = State()

# Хендлер для команды /search
@router.message(Command(commands='search'), StateFilter(default_state))
async def process_search_command(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.start(dialogs.FSMFindPubs.choose_language, mode=StartMode.RESET_STACK)

# Хендлер для нажатия кнопки search
@router.callback_query(F.data == "search_button_pressed", lambda x: x.from_user.username in ["Parckes", "mikail_kryt", "iamk8", "uvwxxz", "OGLuckySaPer", "serhio_vsh"])
async def process_search_button(callback: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.start(dialogs.FSMFindPubs.choose_language, mode=StartMode.RESET_STACK)
