import os
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram import Bot, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.input_file import FSInputFile
from database import Database
from datetime import datetime
from parsing import Parsing


router = Router()
bot = Bot(token="secret")

#travel_{travel[0]}
@router.callback_query(F.data[:6] == 'travel')
async def watchtravel(callback:  types.CallbackQuery, state: FSMContext):
    uid = callback.data.split('_')[1]
    travel = await Database().get_travel(uid)
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text='Заметки📜', callback_data=f'data_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Опции путешествия📑', callback_data=f'options_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Добавить заметку➕', callback_data=f'addz_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Добавить приватную заметку🔒', callback_data=f'addpz_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Добавить участника➕', callback_data=f'addfr_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Добавить локацию📍', callback_data=f'addlock_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Изменить описание✏️', callback_data=f'editbio_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Удалить путешествие🗑️', callback_data=f'delete_{uid}')
    )
    text = (f'Данные о путешествии🗃️:\n'
            f'id🎫: {travel["about"][0]}\n'
            f'Название✍: {travel["about"][1]}\n'
            f'О путешествии📕: {travel["about"][2]}\n'
            f'Локации посещения🗺️:\n')
    locs = ''
    locations = sorted(travel['locations'],key = lambda x: datetime.strptime(x[-1], "%Y-%m-%d"))
    for i in locations:
        txt = f'📍{i[1]}|{i[2]} - {i[3]}\n'
        locs += txt
    text += locs
    users = ''
    for i in travel['members']:
        users += f'@{i[0]}\n'
    text += 'Участники путешествия👨‍👨‍👦‍👦:\n'
    text += users
    await callback.message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data[:4] == 'data')
async def checknotes(callback:  types.CallbackQuery, state: FSMContext):
    uid = callback.data.split('_')[1]
    notes = await Database().getnotes(uid, callback.from_user.username)
    if len(notes) == 0:
        await callback.message.answer('Нет доступных заметок по данному путешествию:(')
        return
    for ind, note in enumerate(notes):
        document = FSInputFile(os.getcwd() + '/writes' + note[3])
        await bot.send_document(callback.from_user.id, document, caption=f'Заметка #{ind+1}\nТекст: ' + note[2])

@router.callback_query(F.data[:7] == 'options')
async def traveloptions(callback:  types.CallbackQuery, state: FSMContext):
    uid = callback.data.split('_')[1]
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text='Карта путешествия🗺️', callback_data=f'map_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Погода🌦️', callback_data=f'weather_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Больницы🚑', callback_data=f'hosp_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Отели🛏️', callback_data=f'hotels_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Рестораны🌮🍕🥪', callback_data=f'rests_{uid}')
    )
    builder.row(types.InlineKeyboardButton(
        text='Интересные места🗽', callback_data=f'attr_{uid}')
    )
    await callback.message.answer('Выбери необходимую опцию:', reply_markup=builder.as_markup())

@router.callback_query(F.data[:7] == 'weather')
async def getweather(callback:  types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Собираю информацию.....')
    uid = callback.data.split('_')[1]
    travel = await Database().get_travel(uid)
    await callback.message.answer(await Parsing().getweather([i for i in sorted(travel['locations'], key=lambda x: datetime.strptime(x[-1], "%Y-%m-%d"))]))

@router.callback_query(F.data[:6] == 'hotels')
async def gethotels(callback:  types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Собираю информацию.....')
    uid = callback.data.split('_')[1]
    travel = await Database().get_travel(uid)
    travels = []
    for loc in sorted(travel['locations'], key=lambda x: datetime.strptime(x[-1], "%Y-%m-%d")):
        travels.append(await Parsing().gethotels(loc[1].split(',')[1], loc[2], loc[3]))
    await callback.message.answer('----------------------------------------------------\n'.join(travels))

@router.callback_query(F.data[:3] == 'map')
async def getmap(callback:  types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Создаю карту....')
    uid = callback.data.split('_')[1]
    travel = await Database().get_travel(uid)
    file = await Parsing().getmap([i[1] for i in sorted(travel['locations'], key=lambda x: datetime.strptime(x[-1], "%Y-%m-%d"))])
    document = FSInputFile(os.getcwd() + '/' + file)
    await bot.send_photo(callback.from_user.id, document)

@router.callback_query(F.data[:5] == 'rests')
async def getfood(callback:  types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Собираю информацию.....')
    uid = callback.data.split('_')[1]
    travel = await Database().get_travel(uid)
    await callback.message.answer(await Parsing().getrestoraunce([i[1] for i in sorted(travel['locations'], key=lambda x: datetime.strptime(x[-1], "%Y-%m-%d"))]))

@router.callback_query(F.data[:4] == 'hosp')
async def gethosp(callback:  types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Собираю информацию.....')
    uid = callback.data.split('_')[1]
    travel = await Database().get_travel(uid)
    await callback.message.answer(await Parsing().gethospitals([i[1] for i in sorted(travel['locations'], key=lambda x: datetime.strptime(x[-1], "%Y-%m-%d"))]))

@router.callback_query(F.data[:4] == 'attr')
async def getattrs(callback:  types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Собираю информацию.....')
    uid = callback.data.split('_')[1]
    travel = await Database().get_travel(uid)
    await callback.message.answer(await Parsing().getinterestig([i[1] for i in sorted(travel['locations'], key=lambda x: datetime.strptime(x[-1], "%Y-%m-%d"))]))