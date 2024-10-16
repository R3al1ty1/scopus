from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from utils.payments import buy_requests, check_payment_status, get_requests_amount
from utils.const import AMOUNTS_DCT
from database.requests import get_requests, add_requests


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
    """Обработчик команды /help."""
    await message.answer(text="""
/search   - поиск
/payments - пополнение баланса
/support  - связь с поддержкой
/balance  - баланс"""
    )


@router.message(Command(commands='start'), StateFilter(default_state))
async def process_start_command(message: Message):
    """Обработчик команды /start."""
    await message.answer(
        text="Привет! Этот бот предоставляет доступ к функционалу Скопуса. Воспользуйтесь кнопкой ниже или введите /search.",
        reply_markup=keyboard
    )


@router.message(Command(commands='payments'), StateFilter(default_state))
async def process_payments_command(message: Message):
    """Обработчик команды /payments."""
    await message.answer(
        text="""Выберите количество запросов для покупки:
1 - 49 руб.
5 - 229 руб.
10 - 419 руб.
20 - 799 руб.
Тарифы SmallLab, MediumLab, LargeLab включают в себя 300, 500 и 800 запросов соответственно.""",
        reply_markup=keyboard_payments
    )


@router.callback_query(F.data.in_(['button_1', 'button_5', 'button_10', 'button_20', 'small', 'medium', 'large']))
async def generate_payment(callback: CallbackQuery):
    """Формирование платежа и его проверки."""
    amount = AMOUNTS_DCT[callback.data]
    payment_url, payment_id = buy_requests(amount, callback.message.chat.id)
    url = InlineKeyboardButton(text="Оплата", url=payment_url)
    check = InlineKeyboardButton(text="Проверить оплату", callback_data=f'check_{payment_id}')
    keyboard_buy = InlineKeyboardMarkup(inline_keyboard=[[url, check]])

    await callback.message.answer(text="Ваша ссылка на оплату готова!\nПосле оплаты необходимо нажать на кнопку проверки платежа.",
                         reply_markup=keyboard_buy)


@router.callback_query(lambda x: "check" in x.data)
async def check_payment(callback: CallbackQuery):
    """Кнопка проверки платежа."""
    res = check_payment_status(callback.data.split('_')[-1])
    reqs = get_requests_amount(callback.data.split('_')[-1])
    if res:
        add_requests(callback.message.chat.id, reqs)
        if reqs == 1:
            await callback.message.answer(f"Оплата прошла успешно, на баланс зачислен 1 запрос.")
        else:
            await callback.message.answer(f"Оплата прошла успешно, на баланс зачислено {reqs} запросов.")
    else:
        await callback.message.answer("На данный момент оплата еще не прошла.")


@router.message(Command(commands='support'), StateFilter(default_state))
async def process_support_command(message: Message):
    """Обработчик команды /support."""
    await message.answer(text="По вопросам пишите: @sirtyler @mikail_kryt. Техподдержка: @ba1xo")


@router.message(Command(commands='balance'), StateFilter(default_state))
async def process_balance_command(message: Message):
    """Обработчик команды /balance."""
    requests = get_requests(message.chat.id)
    await message.answer(f"Количество запросов на Вашем счету: {requests}.\nЧтобы пополнить баланс, используйте команду /payments.")
