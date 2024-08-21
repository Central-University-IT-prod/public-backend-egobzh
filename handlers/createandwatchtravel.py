from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from datetime import datetime
from statemachine import *
import uuid

router = Router()

@router.callback_query(F.data == 'addtravel')
async def myprofile(callback:  types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Воу! Ты решил отправиться в путешествие? Тогда придумай ему уникальное имя!')
    await state.set_state(CreateTravel.name)

@router.message(CreateTravel.name)
async def input_name(message: types.Message, state: FSMContext):
    if await Database().isuniquetravelname(message.text.title()):
        await state.update_data(name=message.text)
        await state.update_data(uid=uuid.uuid1())
        await message.answer('Отлично! Теперь отправь мне краткое описание путешествия(до 45 символов)')
        await state.set_state(CreateTravel.bio)
    else:
        await message.answer('Путешествие с таким именем уже существует:( Отправь новое имя путешествия')


@router.message(CreateTravel.bio)
async def input_bio(message: types.Message, state: FSMContext):
        if len(message.text) > 45:
            await message.answer("Вы написали слишком много( Сократи текст и пришли его еще раз!.")
        else:
            await state.update_data(bio=message.text)
        await message.answer("Отлично! Теперь указывай локации, которые планируешь посетить в"
                             "в формате: Страна, Город$Датаприбытия$Датаотбытия\nНапример: Россия, Москва$2024-04-18$2024-04-20") #datetime.strptime(time, "%Y-%m-%d")
        await state.set_state(CreateTravel.locations)

@router.message(CreateTravel.locations)
async def input_locations(message: types.Message, state: FSMContext):
        if message.text.lower().strip() == '.':
            data = await state.get_data()
            await Database().create_travel(id=data['uid'],name=data['name'].title(),bio=data['bio'],username=message.from_user.username)
            await message.answer(
                "Путешествие создано! Теперь ты можешь посмотреть его во вкладке Мои путешествия /menu .")
            await state.clear()
            return
        try:
            data = message.text.split('$')
            datetime.strptime(data[1], "%Y-%m-%d")
            datetime.strptime(data[2], "%Y-%m-%d")
            data[0].split(',')[1]
            uid = await state.get_data()
            await Database().create_location(id=uid['uid'], locate=data[0], fromtime=data[1], totime=data[2])
            await message.answer("Локация добавлена! Отправьте . в чат, если хотите завершить ввод локаций или же продолжайте ввод")
        except Exception as E:
            #print(E)
            await message.answer("Данные о локации введены в неверном формате. Измените формат или отправьте . для выхода из ввода локаций")

@router.callback_query(F.data == 'mytravel')
async def mytravels(callback:  types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    travels = sorted(await Database().watch_my_travels(callback.from_user.username))
    for travel in travels:
        builder.row(types.InlineKeyboardButton(
            text=travel[1], callback_data=f'travel_{travel[0]}')
        )
    if len(travels) != 0:
        await callback.message.answer('Выбери путешествия, информацию о котором ты хочешь увидеть:',reply_markup=builder.as_markup())
    else:
        await callback.message.answer('Пока у тебя нет путешествий:( Но ты всегда можешь создать их в /menu')