from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command
from database import Database


router = Router()

@router.message(Command("menu"))
async def menu(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="Мои путешествия✈️", callback_data='mytravel')
    )
    builder.row(types.InlineKeyboardButton(
        text="Мой профиль🆔",
        callback_data='me')
    )
    builder.row(types.InlineKeyboardButton(
        text="Создать путешествие🆕",
        callback_data='addtravel')
    )
    builder.row(types.InlineKeyboardButton(
        text="Самые посещаемые локации🏆",
        callback_data='bestlock')
    )
    builder.row(types.InlineKeyboardButton(
        text="Рейтинг опытных путешественников🧳",
        callback_data='besttraveler')
    )
    await message.answer("Тебя приветствует бот путешествий! Сейчас ты в главном меню. Выбери необходимую вкладку.", reply_markup=builder.as_markup())

@router.callback_query(F.data == 'me')
async def myprofile(callback:  types.CallbackQuery):
    profile = await Database().getuser(callback.from_user.username)
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="Заполнить профиль снова✏️", callback_data='editprofile')
    )
    await callback.message.answer(f'Твой профиль🆔:\nИмя🙋: {profile[0]}\n'
                                  f'Возраст📆: {profile[1]}\n'
                                  f'Местоположение📍: {profile[3]}, {profile[2]}\n'
                                  f'Обо мне📜: {profile[4]}\n',reply_markup=builder.as_markup())

@router.callback_query(F.data == 'bestlock')
async def bestlock(callback:  types.CallbackQuery):
    top = await Database().ratelocks()
    text = 'Топ 5 самых посещаемых локаций:\n'
    for ind, i in enumerate(top[:5]):
        text += f'🎖️#{ind+1} {i[0]}\n'
    await callback.message.answer(text)

@router.callback_query(F.data == 'besttraveler')
async def besttrav(callback:  types.CallbackQuery):
    top = await Database().ratetravelers()
    text = 'Топ 5 самых опытных путешественников:\n'
    for ind, i in enumerate(top[:5]):
        text += f'🎖️#{ind+1} @{i[0]} Путешествий: {i[1]}\n'
    await callback.message.answer(text)