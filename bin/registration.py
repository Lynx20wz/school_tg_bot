from aiogram import Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from KeyBoards import main_button
from bin import UserClass, db

auth_router = Router()


class Registration(StatesGroup):
    login_entry = State()


@auth_router.message(StateFilter(None), Command('reg'))
async def registration_user(message, state: FSMContext):
    await state.set_state(Registration.login_entry)
    await message.answer(
            text='Для доступа к домашнему заданию нужно зарегистрироваться! Введите пожалуйста свой логин для входа в школьный портал (госуслуги)',
    )


@auth_router.message(Registration.login_entry)
@UserClass.get_user()
async def end_registration(message, user, state: FSMContext, **kwargs):
    await state.update_data(password=message.text)
    data = await state.get_data()
    await db.update_login(user.username, data.get('login'))
    await message.answer(
            f'Спасибо, {user.username}, вы зарегистрированы!',
            reply_markup=main_button(user)
    )
    await state.clear()
