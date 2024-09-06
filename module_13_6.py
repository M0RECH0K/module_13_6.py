from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Информация')
button2 = KeyboardButton(text='Рассчитать')
kb.add(button)
kb.add(button2)

kb2 = InlineKeyboardMarkup()
button3 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button4 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb2.add(button3)
kb2.add(button4)


@dp.message_handler(text='Рассчитать', state=None)
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию', reply_markup=kb2)


@dp.callback_query_handler(text=['formulas'], state=None)
async def get_formulas(call):
    await call.message.answer(f'Для мужчин: 10 х вес(кг) + 6,25 х рост(см) - 5 х возраст(г) + 5''\n'
                              'Для женщин: 10 х вес(кг) + 6,25 х рост(см) - 5 х возраст(г) + 161')
    await call.answer()


@dp.message_handler(commands=['start'], state=None)
async def start(message: types.Message):
    await message.answer('Нажми на одну из кнопок.', reply_markup=kb)


@dp.message_handler(text=['Информация'], state=None)
async def inform(message: types.Message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.callback_query_handler(text=['calories'], state=None)
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = float(data['weight'])
    calories = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f'Ваша норма калорий: {calories} ккал.')
    await state.finish()


@dp.message_handler()
async def hello(message: types.Message):
    await message.answer('Привет! Хочешь узнать свою норму калорий? Тогда нажми на /start!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
