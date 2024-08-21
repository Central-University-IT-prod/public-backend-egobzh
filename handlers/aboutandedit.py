from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.filters.command import Command
from database import Database
from statemachine import *

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Тебя приветствует бот путешествий! Немного расскажи о себе. Сколько тебе лет?")
    await state.set_state(Register.age)

@router.message(Register.age)
async def input_age(message: types.Message, state: FSMContext):
    try:
        if int(message.text.lower()) > 150 or int(message.text.lower()) <= 0:
            await message.answer("Некорректный возраст!!")
        else:
            await state.update_data(age=int(message.text.lower()))
            await message.answer("Отлично! Теперь укажи свой город c большой буквы.")
            await state.set_state(Register.city)
    except:
        await message.answer("Некорректный возраст!!")

@router.message(Register.city)
async def input_city(message: types.Message, state: FSMContext):
        await state.update_data(city=message.text)
        await message.answer("Отлично! Теперь укажи свою страну с большой буквы.")
        await state.set_state(Register.country)

@router.message(Register.country)
async def input_country(message: types.Message, state: FSMContext):
        await state.update_data(country=message.text)
        await message.answer("Отлично! Теперь кратко расскажи о себе(до 45 символов).")
        await state.set_state(Register.bio)

@router.message(Register.bio)
async def input_bio(message: types.Message, state: FSMContext):
        if len(message.text) > 45:
            await message.answer("Вы написали о себе больше 45 символов! Сократи текст и пришли его еще раз!.")
        else:
            await state.update_data(bio=message.text)
            data = await state.get_data()
            await Database().create_user(username=message.from_user.username, **data)
            await message.answer("Записал данные о тебе! Теперь ты можешь пользоваться ботом, вызови главное меню командой /menu .")
            await state.clear()

@router.callback_query(F.data == 'editprofile')
async def editprofile(callback:  types.CallbackQuery, state:FSMContext):
    await callback.message.answer("Давай перезаполним твою анкетку. Сколько тебе лет?")
    await state.set_state(Register.age)

