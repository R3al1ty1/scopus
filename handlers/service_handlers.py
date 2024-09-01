from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

#from aiogram.types import ChatActions

from filters.filters import general_filter


router = Router()

# Создаем объекты инлайн-кнопок
search_button = InlineKeyboardButton(
    text='ПОИСК',
    callback_data='search_button_pressed'
)

# Создаем объект инлайн-клавиатуры
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[search_button]]
)


# Создаем объекты инлайн-кнопок
button_1 = InlineKeyboardButton(
    text='1',
    callback_data='button_1'
)
button_5 = InlineKeyboardButton(
    text='5',
    callback_data='button_5'
)
button_10 = InlineKeyboardButton(
    text='10',
    callback_data='button_10'
)
button_20 = InlineKeyboardButton(
    text='20',
    callback_data='button_20'
)

button_small = InlineKeyboardButton(
    text='SmallLab',
    callback_data='small'
)
button_medium = InlineKeyboardButton(
    text='MediumLab',
    callback_data='medium'
)
button_large = InlineKeyboardButton(
    text='LargeLab',
    callback_data='large'
)


# Создаем объект инлайн-клавиатуры
keyboard_payments = InlineKeyboardMarkup(
    inline_keyboard=[[button_1, button_5, button_10, button_20],
                      [button_small, button_medium, button_large]  ]
)

# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'), StateFilter(default_state), general_filter)
async def process_start_command(message: Message):
    await message.answer(text = """
/search   - поиск
/payments - пополнение баланса
/support  - связь с поддержкой
/balance  - баланс""")


# Этот хэндлер срабатывает на команду /start
@router.message(Command(commands='start'), StateFilter(default_state), general_filter)
async def process_help_command(message: Message):
    await message.answer(text = "Привет! Этот бот - единственная адекватная альтернатива ушедшему из России Скопусу, он предоставляет недорогой доступ к функционалу, который лаборатории и университеты покупюат за тысячи долларов. При это в России такой возможности в принципе нет.\n\nДля поиска нажмите кнопку ниже, или напишите /search. Если вы у нас впервые, то у вас на счёту есть 1 запрос в качестве подарка. Sapere aude!",
                         reply_markup=keyboard)

# Этот хэндлер срабатывает на команду /payments
@router.message(Command(commands='payments'), StateFilter(default_state), general_filter)
async def process_start_command(message: Message):
    await message.answer(text = """
Выберите количество запросов, которое хотите приобрести.

1 - 49 рублей
5 - 229 рублей
10 - 419 рублей
20 - 799 рублей

Тарифы SmallLab, MediumLab, LargeLab включают в себя 300, 500 и 800 запросов соответсвенно. А также позволяют добавить 1, 2 или 3 людей, которые также смогут использовать эти запросы.""",
                         reply_markup=keyboard_payments)



@router.message(Command(commands='support'), StateFilter(default_state), general_filter)
async def process_start_command(message: Message):
    await message.answer(text = "По всем вопросам, неполадкам и пожеланиям пишите сюда: \nПо вопросам сотрудничества: @sirtyler @mikail_kryt \nПо техническим вопросам: @ba1xo ")


# /balance    
@router.message(Command(commands='balance'), StateFilter(default_state), general_filter)
async def process_search_command(message: Message):
    await message.answer("На текущий момент у вас на балансе 389 запросов.\n\nЧтобы купить запросы восользуйтесь командой /payments")
                         