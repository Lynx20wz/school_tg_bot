from aiogram import Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.bin import UserClass, db, token_button, main_button
from bot.bin.parser import get_student_id

auth_router = Router()


class GetToken(StatesGroup):
    token = State()


@auth_router.message(StateFilter(None), Command('token'))
async def registration_user(message, state: FSMContext):
    await state.set_state(GetToken.token)
    await message.answer(
            'Пожалуйста нажмите на кнопку ниже, скопируйте и отправьте нам токен! (токен начинается с `eyJhb`)\n\nЕсли ты получил другой текст, то сначала перейди по второй кнопке и зарегистрируйся, а потом на первую жми.',
            reply_markup=token_button(),
            parse_mode='Markdown',
    )


@auth_router.message(GetToken.token)
@UserClass.get_user()
async def end_registration(message, user, state: FSMContext):
    if message.text.strip().startswith('eyJhb'):
        await state.update_data(token=message.text)
        data = await state.get_data()
        user.token = data.get('token')
        user.student_id = get_student_id(token=user.token)
        await db.update_user(user)
        await message.answer(
                f'{user.username}, ваш токен успешно зарегистрирован!',
                reply_markup=main_button(user),
        )
        await state.clear()
    else:
        await message.answer('Неправильный токен, повторите попытку!')
