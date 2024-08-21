import os
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram import Bot, types
from database import Database
from datetime import datetime
from statemachine import *


router = Router()
bot = Bot(token="secret")

@router.callback_query()
async def setstate(callback:  types.CallbackQuery, state: FSMContext):
    namecall = callback.data
    if namecall[:4] == 'addz':
        await state.set_state(EditAd.addz)
        await state.update_data(uid=callback.data.split('_')[1])
        await callback.message.answer('Отправь мне фото(файлом) или любой другой файл с подписью и я создам заметку!')
    elif namecall[:5] == 'addpz':
        await state.set_state(EditAd.addpz)
        await state.update_data(uid=callback.data.split('_')[1])
        await callback.message.answer('Отправь мне фото(файлом) или любой другой файл с подписью и я создам приватную заметку!')
    elif namecall[:5] == 'addfr':
        await state.set_state(EditAd.addfr)
        await state.update_data(uid=callback.data.split('_')[1])
        await callback.message.answer('Введите username(без собачки) друга, которого вы хотите добавить в путешествие. Например: iwdbliss. Этот пользователь должен быть зарегистрирова в боте!')
    elif namecall[:7] == 'addlock':
        await state.set_state(EditAd.addlock)
        await state.update_data(uid=callback.data.split('_')[1])
        await callback.message.answer("Укажи локацию, которую нужно добавить в"
                             "в формате: Страна, Город$Датаприбытия$Датаотбытия\nНапример: Россия, Москва$2024-04-18$2024-04-20")
    elif namecall[:7] == 'editbio':
        await state.set_state(EditAd.editbio)
        await state.update_data(uid=callback.data.split('_')[1])
        await callback.message.answer('Введите новое описание путешествия(до 45 символов)')
    elif namecall[:6] == 'delete':
        await Database().deletetravel(callback.data.split('_')[1])
        await callback.message.answer('Путешествие удалено!')
        await callback.message.delete()

@router.message(EditAd.editbio)
async def edit_bio(message: types.Message, state: FSMContext):
        if len(message.text) > 45:
            await message.answer("Вы написали слишком много( Сократи текст и пришли его еще раз!.")
        else:
            uid = await state.get_data()
            await Database().updatetravelbio(uid['uid'], message.text)
        await message.answer('Обновил описание!')
        await state.clear()

@router.message(EditAd.addfr)
async def add_friend(message: types.Message, state: FSMContext):
        if not await Database().getuser(message.text):
            await message.answer("Такой пользователь не зарегистрирован в боте, проверьте правильность юзернейма или попросите пользователя зарегистрироваться в боте")
        else:
            uid = await state.get_data()
            await Database().addfriendintravel(uid['uid'], message.text)
            await message.answer('Добавил участника в путешествие!')
            await state.clear()

@router.message(EditAd.addlock)
async def add_locations(message: types.Message, state: FSMContext):
    try:
        data = message.text.split('$')
        datetime.strptime(data[1], "%Y-%m-%d")
        datetime.strptime(data[2], "%Y-%m-%d")
        data[0].split(',')[1]
        uid = await state.get_data()
        await Database().create_location(id=uid['uid'], locate=data[0], fromtime=data[1], totime=data[2])
        await message.answer("Локация добавлена!")
        await state.clear()
    except Exception as E:
            #print(E)
        await message.answer("Данные о локации введены в неверном формате.")

@router.message(EditAd.addz)
async def download_note(message: types.Message, state: FSMContext):
    uid = await state.get_data()
    if message.photo:
        file_name = f"{os.getcwd()}/writes/{message.photo[-1].file_id}.jpg"
        await bot.download(message.photo[-1], destination=file_name)
        await Database().addnote(uid['uid'], 'All', message.caption, f'/{message.photo[-1].file_id}.jpg')
        await message.answer('Заметка добавлена!')
    elif message.document:
        mime_type = message.document.mime_type
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path

        file_obj = await bot.download_file(file_path)

        file_extension = mime_type.split("/")[-1]
        with open(f"{os.getcwd()}/writes/{message.document.file_name}.{file_extension}", 'wb') as f:
            f.write(file_obj.read())

        await Database().addnote(uid['uid'], 'All', message.caption, f'/{message.document.file_name}.{file_extension}')
        await message.answer('Заметка добавлена!')
    else:
        await message.answer('Файл для заметки не приложен! Зайдите в раздел еще раз и попрбуйте снова')

@router.message(EditAd.addpz)
async def download_note_private(message: types.Message, state: FSMContext):
    uid = await state.get_data()
    if message.photo:
        file_name = f"{os.getcwd()}/writes/{message.photo[-1].file_id}.jpg"
        await bot.download(message.photo[-1], destination=file_name)
        await Database().addnote(uid['uid'], message.from_user.username, message.caption, f'/{message.photo[-1].file_id}.jpg')
        await message.answer('Заметка добавлена!')
    elif message.document:
        mime_type = message.document.mime_type
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path

        file_obj = await bot.download_file(file_path)

        file_extension = mime_type.split("/")[-1]
        with open(f"{os.getcwd()}/writes/{message.document.file_name}.{file_extension}", 'wb') as f:
            f.write(file_obj.read())

        await Database().addnote(uid['uid'], message.from_user.username, message.caption, f'/{message.document.file_name}.{file_extension}')
        await message.answer('Заметка добавлена!')
    else:
        await message.answer('Файл для заметки не приложен! Зайдите в раздел еще раз и попрбуйте снова')