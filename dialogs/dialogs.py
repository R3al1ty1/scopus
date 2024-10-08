from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

from aiogram.types import Message
from aiogram import Router, F

from aiogram.filters import Command, StateFilter

from aiogram.types import FSInputFile, CallbackQuery, ContentType


from aiogram_dialog import Dialog, Window, setup_dialogs, DialogManager, StartMode, BaseDialogManager, ShowMode
from aiogram_dialog.widgets.text import Format, Multi, Const, Progress
from aiogram_dialog.widgets.kbd import Checkbox, Button, Row, Cancel, Start, Next, ScrollingGroup

from aiogram_dialog.widgets.input import TextInput, MessageInput

from aiogram_dialog.widgets.text import Jinja

from database.requests import new_user

import uuid
import time

import asyncio

from utils.utils import download_scopus_file

class FSMFindPubs(StatesGroup):
    choose_language = State()         # Состояние ожидания выбора языка
    choose_years = State()            # Состояние ожидания ввода годов
    choose_document_type = State()    # Состояние ожидания выбора типов документа
    filling_query = State()           # Состояние написания запроса
    validate = State()                # Валидация введенных данных
    #search = State()                 # Состояние поиска
    check_pubs = State()              # Просмотр 50 статей

async def dialog_get_data(dialog_manager: DialogManager, **kwargs):
    return {
        "ru": dialog_manager.find("ru").is_checked(),
        "eng": dialog_manager.find("eng").is_checked(),
        "years": dialog_manager.find("years").get_value(),
        "art": dialog_manager.find("art").is_checked(),
        "rev": dialog_manager.find("rev").is_checked(),
        "conf": dialog_manager.find("conf").is_checked(),
        "query": dialog_manager.find("query").get_value(),
        "pressed": dialog_manager.dialog_data['pressed'],
    }

async def pubs_found(dialog_manager: DialogManager, **kwargs):
    return {
        "pubs_found": dialog_manager.dialog_data['pubs_found'],
        "pressed_new": dialog_manager.dialog_data['pressed_new'],
    }


async def next_and_set_not_pressed(callback: CallbackQuery, button: Button, manager: DialogManager):
    manager.dialog_data['pressed'] = False
    manager.dialog_data['pressed_new'] = False
    await manager.next() 

    
async def error(
        message: Message,
        dialog_: Any,
        manager: DialogManager,
        error_: ValueError
):
    await message.answer("Необходимо ввести ровно 2 упорядоченных неотрицательных числа через пробел, оба не больше 9999")


def check_years(text):
    
    num_words=len(text.split())
    if (num_words != 2):
        raise ValueError
    words = text.split()  
    print(words)
    if (not (words[0].isnumeric() and words[1].isnumeric() and int(words[1]) >= int(words[0]) >= 0 and int(words[1]) < 10000)):
        raise ValueError
    return text


async def go_to_beginning(callback: CallbackQuery, button: Button, manager: DialogManager):
    #manager.dialog_data['pressed'] = True
    await manager.switch_to(FSMFindPubs.choose_language)  



async def start_search(callback: CallbackQuery, button: Button,
                     manager: DialogManager):
    
    chat_id = str(callback.message.chat.id)
    new_user(chat_id)

    #await manager.switch_to(state=FSMFindPubs.search)
    manager.dialog_data['folder_id'] = uuid.uuid4()
    manager.dialog_data['pressed'] = True
    await callback.message.answer("Отлично! Теперь, пожалуйста, подождите. Наш бот уже выполняет ваш запрос.")
    loop = asyncio.get_event_loop()

    flag = asyncio.Event()
    future = asyncio.Future()
    manager.dialog_data['future'] = future
    asyncio.create_task(download_scopus_file(await dialog_get_data(manager), manager.dialog_data['folder_id'], flag, future))
    await flag.wait()
    flag.clear()
    manager.dialog_data['flag'] = flag
    result = future.result()


    #result = await loop.run_in_executor(None, download_scopus_file, await dialog_get_data(manager), manager.dialog_data['folder_id'])
    ##result = await download_scopus_file(query= await dialog_get_data(manager), folder_id=manager.dialog_data['folder_id'])
    if (result[0]):

        manager.dialog_data['pubs_found'] = result[1]
        manager.dialog_data['newest'] = result[2]
        manager.dialog_data['oldest'] = result[3]
        manager.dialog_data['most_cited'] = result[4]
        manager.dialog_data['active_array'] = result[2]

        for i in range(len(result[2])):
            manager.find(str(i)).text = Const(str(i + 1) + ". " + str(result[2][i]["Title"]))
        await manager.switch_to(state=FSMFindPubs.check_pubs, show_mode=ShowMode.SEND)

    else:
        await callback.message.answer(text="По Вашему запросу не было найдено ни одной статьи.\n\nСпасибо, что воспользовались нашим ботом! \n\nЧтобы искать снова напишите команду /search")
        await manager.done()
  
def chunkstring(string, length):
    return ([string[0+i:length+i] for i in range(0, len(string), length)])


async def process_pub_click(callback: CallbackQuery, button: Button,
                     manager: DialogManager):
    if (int(callback.data) < len(manager.dialog_data['active_array'])):

        list_to_print = chunkstring(f"""
        {int(callback.data) + 1}
*Название*    
        {manager.dialog_data['active_array'][int(callback.data)]['Title'].replace('_', '-').replace('*', '✵')}

*Абстракт*
        {manager.dialog_data['active_array'][int(callback.data)]['Abstract'].replace('_', '-').replace('*', '✵')}

*Авторы*
        {manager.dialog_data['active_array'][int(callback.data)]['Authors'].replace('_', '-').replace('*', '✵')}

*Источник*
        {manager.dialog_data['active_array'][int(callback.data)]['Source'].replace('_', '-').replace('*', '✵')}

*Год*
        {manager.dialog_data['active_array'][int(callback.data)]['Year'].replace('_', '-').replace('*', '✵')}

*Кол-во цитированиий*
        {manager.dialog_data['active_array'][int(callback.data)]['Citations'].replace('_', '-').replace('*', '✵')  }


Чтобы виджет с выбором статей опустила вниз диалога, отправьте любое сообщение.

        """, 4096)
        for j in range(len(list_to_print)):
            await callback.message.answer(list_to_print[j], parse_mode = 'Markdown')
        await manager.switch_to(state=FSMFindPubs.check_pubs)


def pub_buttons_create():
    buttons = []
    for i in range(0, 50):
        i = str(i)
        buttons.append(Button(Const('-'), id=i, on_click=process_pub_click, when=~F["pressed_new"]))
    return buttons


async def download_file(callback: CallbackQuery, button: Button, manager: DialogManager):
    #manager.dialog_data['pressed'] = True
    manager.dialog_data['pressed_new'] = True
    try:
        await callback.message.answer("Отлично! Подождите пока мы скачиваем файл - это может занять некоторое время")
        flag = manager.dialog_data['flag']
        flag.set()
        await asyncio.sleep(1)
        print("flag was set in handler and now we are waiting")
        await flag.wait()
        await callback.message.answer_document(document=FSInputFile(f"/Users/user/Documents/scopus_files/{manager.dialog_data['folder_id']}/scopus.ris"))
        await callback.message.answer("Спасибо, что воспользовались нашим ботом! \n\nЧтобы искать снова напишите команду /search")
        await manager.done() 
        return
    except:
        await callback.message.answer("Произошла непредвиденная ошибка, скорее всего Scopus начудил. Мы не спишем вам запрос. Попробуйте позже или переформулируйте запрос.")
        await manager.done() 

# async def do_not_download_file(callback: CallbackQuery, button: Button, manager: DialogManager):
#     #manager.dialog_data['pressed'] = True
#     manager.dialog_data['pressed_new'] = True
#     manager.dialog_data['future'].set_result(False)
#     flag.set()
#     await asyncio.sleep(1)
#     await callback.message.answer("Спасибо, что воспользовались нашим ботом! \n\nЧтобы искать снова напишите команду /search")
#     await state.set_state(FSMFindPubs.choose_language)
#     await manager.done()        

#test_buttons = test_buttons_creator(range(0, 100))

async def sort_by_newest(callback: CallbackQuery, button: Button, manager: DialogManager):
    manager.find("cit").text = Const("⚪️ Cited")
    manager.find("date_new").text = Const("🔘 Newest")
    manager.find("date_old").text = Const("⚪️ Oldest")
    for i in range(len(manager.dialog_data['newest'])):
        manager.find(str(i)).text = Const(str(i + 1) + ". " + str(manager.dialog_data['newest'][i]["Title"]))
    manager.dialog_data['active_array'] = manager.dialog_data['newest']   

async def sort_by_oldest(callback: CallbackQuery, button: Button, manager: DialogManager):
    manager.find("cit").text = Const("⚪️ Cited")
    manager.find("date_new").text = Const("⚪️ Newest")
    manager.find("date_old").text = Const("🔘 Oldest")
    for i in range(len(manager.dialog_data['oldest'])):
        manager.find(str(i)).text = Const(str(i + 1) + ". " + str(manager.dialog_data['oldest'][i]["Title"])) 
    manager.dialog_data['active_array'] = manager.dialog_data['oldest']  

async def sort_by_most_cited(callback: CallbackQuery, button: Button, manager: DialogManager):
    manager.find("cit").text = Const("🔘 Cited")
    manager.find("date_new").text = Const("⚪️ Newest")
    manager.find("date_old").text = Const("⚪️ Oldest")
    for i in range(len(manager.dialog_data['most_cited'])):
        manager.find(str(i)).text = Const(str(i + 1) + ". " + str(manager.dialog_data['most_cited'][i]["Title"]))  
    manager.dialog_data['active_array'] = manager.dialog_data['most_cited']    

main_menu = Dialog(
    Window(
        Const(
            "Выберите, если нужно, языки для фильтрации публикаций."
        ),
        Row(
            Checkbox(
                Const("☑️ Русский🇷🇺"),
                Const("⬜ Русский🇷🇺"),
                id="ru",
                default=False,  # so it will be checked by default,
            ),
            Checkbox(
                Const("☑️ Английский🇬🇧"),
                Const("⬜ Английский🇬🇧"),
                id="eng",
                default=False,  # so it will be checked by default,
            ),
        ),
        Button(text=Const("Дальше"), id="save", on_click=next_and_set_not_pressed),
        state=FSMFindPubs.choose_language,
    ),
    Window(
        Const(
            "Напишите в каком временном диапазоне Вы хотите искать статьи, укажите года через пробел.\n\nНапример:\n'0 2028' или '1989 2001' или '2023 2023'."
        ),
        TextInput(
            id="years",
            on_error=error,
            on_success=Next(),
            type_factory=check_years,
        ),
        state=FSMFindPubs.choose_years,
    ),
    Window(
        Const(
            "Выберите, если нужно, типы документов для фильтрации."
        ),
        Row(
            Checkbox(
                Const("☑️ Article📝"),
                Const("⬜ Article📝"),
                id="art",
                default=False,  # so it will be checked by default,
            ),
            Checkbox(
                Const("☑️ Review📣"),
                Const("⬜ Review📣"),
                id="rev",
                default=False,  # so it will be checked by default,
            ),
        ),
        Row(
            Checkbox(
                Const("☑️ Conference\npaper👥"),
                Const("⬜ Conference\npaper👥"),
                id="conf",
                default=False,  # so it will be checked by default,
            ),
        ),
        Button(text=Const("Дальше"), id="save", on_click=Next()),
        state=FSMFindPubs.choose_document_type,
    ),
    Window(
        Const("Теперь введите сам поисковый запрос."),
        TextInput(
            id="query",
            on_success=Next(),
        ),
        state=FSMFindPubs.filling_query,
    ),
    Window(
        Format("""Проверьте корректность введеных данных.\n\nУбедитесь, что в запросе нет опечаток - скопус может ничего не найти, но мы всё равно спишем запрос с вашего счёта.  

    Русский язык: {ru}
    Английский язык: {eng}
    Года: {years}
    Article: {art}
    Review: {rev}
    Conference paper: {conf}
    ----------------
    Текст запроса: "{query}"                  
"""),
        Button(text=Const("🔁 Заново"), id="again", on_click=go_to_beginning, when=~F["pressed"]),
        Button(text=Const("▶️ Поиск"), id="search", on_click=start_search, when=~F["pressed"]),
        state=FSMFindPubs.validate,
        getter=dialog_get_data  # here we specify data getter for dialog
    ),
    Window(
        Row (
            Button(text=Const("⚪️ Cited"), id="cit", on_click=sort_by_most_cited),
            Button(text=Const("🔘 Newest"), id="date_new", on_click=sort_by_newest),
            Button(text=Const("⚪️ Oldest"), id="date_old", on_click=sort_by_oldest)
        ),
        Format("По вашему запросу найдено {pubs_found} статей.\n\n Ниже представлен топ соответствующих."),
        ScrollingGroup(
            *pub_buttons_create(),
            id="numbers",
            width=1,
            height=8,
        ),
        Button(text=Const("Скачать файл со всеми статьями 👑"), id="download", on_click=download_file, when=~F["pressed_new"]),
        #Button(text=Const("Не скачивать файл"), id="do_not_download", on_click=do_not_download_file, when=~F["pressed_new"]),
        state=FSMFindPubs.check_pubs,
        getter=pubs_found
    ),
    
)
