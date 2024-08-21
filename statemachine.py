from aiogram.fsm.state import StatesGroup, State

class Register(StatesGroup):
    age = State()
    city = State()
    country = State()
    bio = State()

class CreateTravel(StatesGroup):
    name = State()
    bio = State()
    locations = State()

class EditAd(StatesGroup):
    addz = State()
    addpz = State()
    addfr = State()
    addlock = State()
    editbio = State()

