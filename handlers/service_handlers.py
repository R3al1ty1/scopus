from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

router = Router()

# Кнопки и клавиатуры
search_button = InlineKeyboardButton(text='ПОИСК', callback_data='search_button_pressed')
keyboard = InlineKeyboardMarkup(inline_keyboard=[[search_button]])

button_1 = InlineKeyboardButton(text='1', callback_data='button_1')
button_5 = InlineKeyboardButton(text='5', callback_data='button_5')
button_10 = InlineKeyboardButton(text='10', callback_data='button_10')
button_20 = InlineKeyboardButton(text='20', callback_data='button_20')
button_small = InlineKeyboardButton(text='SmallLab', callback_data='small')
button_medium = InlineKeyboardButton(text='MediumLab', callback_data='medium')
button_large = InlineKeyboardButton(text='LargeLab', callback_data='large')

keyboard_payments = InlineKeyboardMarkup(inline_keyboard=[
    [button_1, button_5, button_10, button_20],
    [button_small, button_medium, button_large]
])

# Хендлеры
@router.message(Command(commands='help'), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(text="""
/search   - поиск
/payments - пополнение баланса
/support  - связь с поддержкой
/balance  - баланс"""
    )

@router.message(Command(commands='start'), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text="Привет! Этот бот предоставляет доступ к функционалу Скопуса. Воспользуйтесь кнопкой ниже или введите /search.",
        reply_markup=keyboard
    )

@router.message(Command(commands='payments'), StateFilter(default_state))
async def process_payments_command(message: Message):
    await message.answer(
        text="""Выберите количество запросов для покупки:
1 - 49 руб.
5 - 229 руб.
10 - 419 руб.
20 - 799 руб.
Тарифы SmallLab, MediumLab, LargeLab включают в себя 300, 500 и 800 запросов соответственно.""",
        reply_markup=keyboard_payments
    )

@router.message(Command(commands='support'), StateFilter(default_state))
async def process_support_command(message: Message):
    await message.answer(text="По вопросам пишите: @sirtyler @mikail_kryt. Техподдержка: @ba1xo")

@router.message(Command(commands='balance'), StateFilter(default_state))
async def process_balance_command(message: Message):
    await message.answer("На вашем счету 389 запросов. Чтобы пополнить баланс, используйте команду /payments.")
