from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.keyboard import main_kb, token_kb
from database import UnitOfWork, User

auth_router = Router()


class GetToken(StatesGroup):
    token: State = State()


@auth_router.message(StateFilter(None), Command('token'))
async def registration_user(message: Message, state: FSMContext):
    await state.set_state(GetToken.token)
    await message.answer(
        'Пожалуйста нажмите на кнопку ниже, скопируйте и отправьте нам токен! (токен начинается с `eyJhb`)\n\nЕсли ты получил другой текст, то сначала перейди по второй кнопке и зарегистрируйся, а потом на первую жми.',
        reply_markup=token_kb,
        parse_mode='Markdown',
    )


@auth_router.message(GetToken.token)
async def end_registration(message: Message, user: User, uow: UnitOfWork, state: FSMContext):
    data = await state.get_data()
    token = data.get('token')
    if token and token.startswith('eyJhb'):
        student_id = user.parser.get_student_id()
        await uow.users.set_reg_data(user.userid, token=token, student_id=student_id)
        await message.answer(
            f'{message.from_user.username}, ваш токен успешно зарегистрирован!',
            reply_markup=main_kb(user),
        )
        await state.clear()
    else:
        await message.answer('Неправильный токен, повторите попытку!')
