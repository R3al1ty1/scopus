from typing import Any

from aiogram.types import Message
from aiogram import Router, F
from aiogram.filters import Command, StateFilter

from aiogram.types import FSInputFile, CallbackQuery, ContentType


from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

from aiogram_dialog import DialogManager, StartMode

#from aiogram.types import ChatActions

from filters.filters import general_filter

from dialogs import dialogs


router = Router()



class FSMSearching(StatesGroup):   
    searching = State()               # Мы ищем


    


# Этот хэндлер срабатывает на команду /search
@router.message(Command(commands='search'), StateFilter(default_state), general_filter)
async def process_search_command(message: Message, state: FSMContext, dialog_manager: DialogManager):
    # await state.set_state(FSMSearching.searching)
    await dialog_manager.start(dialogs.FSMFindPubs.choose_language, mode=StartMode.RESET_STACK)

# А этот на нажатие на кнопку search
@router.callback_query(F.data == "search_button_pressed", lambda x : x.from_user.username == "Parckes" or x.from_user.username == "mikail_kryt" or x.chat.username == 'iamk8' or x.chat.username == "uvwxxz" or x.chat.username == "OGLuckySaPer" or x.chat.username == "serhio_vsh")
async def process_search_button(callback: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    # await state.set_state(FSMSearching.searching)
    await dialog_manager.start(dialogs.FSMFindPubs.choose_language, mode=StartMode.RESET_STACK)    

# Этот хэндлер срабатывает на команду /cancel
# @router.message(Command(commands='cancel'), StateFilter(FSMSearching.searching), general_filter)
# async def process_search_command(message: Message, state: FSMContext, dialog_manager: DialogManager):
#     await state.clear()
#     await dialog_manager.done()
