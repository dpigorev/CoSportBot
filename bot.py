import logging
from aiogram import Bot, Dispatcher, executor, types
from os import getenv
from sys import exit
import random
import psycopg2
import requests
import json
from validate_email import validate_email
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

class Step(StatesGroup):
    reg_start = State()
    reg_nickname = State()
    reg_name = State()
    reg_surname = State()
    reg_pass = State()
    reg_email = State()
    reg_isSportsman = State()
    reg_gender = State()
    #reg_notValid_email = State()

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


registr_arr = []
phone_number = ""
hasBeenRepeated = False

async def check(message):
    url = "http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Nickname=qartz"
    response = requests.get(url)
    response1 = response.text
    response1 = response1.replace("[", "")
    response1 = response1.replace("]", "")
    print(response1 + "пусто")
dp.register_message_handler(check, commands="check")


async def add(message):
    requests.post('http://167.172.35.241/CSDB/Users/?Content-Type=application/json',
                  data={'Phone': '79209217373', 'Nickname': 'aboba', 'Password': 'qwerty',
                        'Name': 'Ivan', 'Surname': 'Ivanov', 'Email': 'artjom200006@yandex.ru',
                        'Gender': 'M', 'Profsportman': 'True'})
dp.register_message_handler(add, commands="add")


async def cmd_phonenumber(message):
    global phone_number
    global registr_arr
    global hasBeenRepeated
    phone_number = ""
    registr_arr = []
    hasBeenRepeated = False
    keyboard = types.ReplyKeyboardMarkup()
    button_1 = types.KeyboardButton(text="Авторизоваться по номеру телефона", request_contact=True)
    keyboard.add(button_1)
    await message.answer("Нажмите на кнопку, чтобы подтвердить передачу номера телефона", reply_markup=keyboard)
dp.register_message_handler(cmd_phonenumber, commands="start")

async def autorization(message):
    global phone_number
    phone_number = str(message.contact.phone_number)
    zapros = 'http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Phone=' + phone_number
    response = requests.get(zapros)
    response1 = response.text
    response1 = response1.replace("[", "")
    response1 = response1.replace("]", "")
    #response2 = json.loads(response1)
    if response1 != "":
        response2 = json.loads(response1)
        Name = response2["Name"]
        keyboard = types.ReplyKeyboardMarkup()
        button_1 = types.KeyboardButton(text="Создать команду")
        keyboard.add(button_1)
        button_2 = types.KeyboardButton(text="Мои команды")
        keyboard.add(button_2)
        button_3 = types.KeyboardButton(text="Создать мероприятие")
        keyboard.add(button_3)
        button_4 = types.KeyboardButton(text="Мои мероприятия")
        keyboard.add(button_4)
        button_5 = types.KeyboardButton(text="Найти мероприятие")
        keyboard.add(button_5)
        button_6 = types.KeyboardButton(text="Настройки")
        keyboard.add(button_6)
        await message.answer("Здравствуйте, " + Name + "!", reply_markup=keyboard)

    else:
        keyboard = types.ReplyKeyboardMarkup()
        button_1 = types.KeyboardButton(text="Зарегистрироваться!")
        keyboard.add(button_1)
        await Step.reg_start.set()
        await message.answer("Вы не зарагистрированны на нашем сервисе. Нажмите на кнопку 'Зарегистрироваться!' чтобы пройти регистрацию. ", reply_markup=keyboard)
dp.register_message_handler(autorization, content_types=["contact"])

async def registration(message, state):
    keyboard = types.ReplyKeyboardRemove()
    #global phone_number
    registr_arr.append(phone_number)
    await state.finish()
    await Step.reg_nickname.set()
    await message.answer("Введите Nickname", reply_markup=keyboard)
dp.register_message_handler(registration, state=Step.reg_start)

async def registr_first_step(message: types.Message, state):
    global registr_arr
    nickname = ""
    cont = False
    circle = True
    nickname = message.text
    nickname = nickname.lower()
    zapros = 'http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Nickname=' + nickname
    response = requests.get(zapros)
    response1 = response.text
    response1 = response1.replace("[", "")
    response1 = response1.replace("]", "")
    if response1 == "":
        cont = True
        circle = False
    if circle:
        for i in range(1, 10):
            #nickname = message.text + '#' + str(i)
            nickname = message.text + str(i)
            nickname = nickname.lower()
            zapros = 'http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Nickname=' + nickname
            #print(zapros)
            response = requests.get(zapros)
            response1 = response.text
            response1 = response1.replace("[", "")
            response1 = response1.replace("]", "")
            #print(response1 + "         aboba")
            if response1 == "":
                cont = True
                break
            if i == 9:
                await message.answer("Такой Nickname уже занят. Пожалуйста, выберите другой.")
                await message.answer("Введите Nickname.")
                await state.finish()
                await Step.reg_nickname.set()
                break
    if cont:
        registr_arr.append(nickname)
        await message.answer("Ваш Nickname - " + nickname)
        await message.answer("Введите пароль\nВнимание! Пароль должен содержать не менее 6 символов!")
        await state.finish()
        await Step.reg_pass.set()
dp.register_message_handler(registr_first_step, state=Step.reg_nickname)

async def registr_second_step(message: types.Message, state):
    global registr_arr
    global hasBeenRepeated
    pas = message.text
    #print(pas)
    repeat = False
    if len(pas) < 6:
        await state.finish()
        await Step.reg_pass.set()
        repeat = True
        hasBeenRepeated = True
    if repeat == False:
        registr_arr.append(message.text)
        await message.answer("Введите имя")
        await state.finish()
        await Step.reg_name.set()
        hasBeenRepeated = False
    if hasBeenRepeated:
        await message.answer('Введенный пароль не соответствует требованиям. Пожалуйста, повторите попытку.')
dp.register_message_handler(registr_second_step, state=Step.reg_pass)

async def registr_third_step(message: types.Message, state):
    global registr_arr
    registr_arr.append(message.text)
    await message.answer("Введите фамилию")
    await state.finish()
    await Step.reg_surname.set()
dp.register_message_handler(registr_third_step, state=Step.reg_name)

async def registr_fourth_step(message: types.Message, state):
    global registr_arr
    registr_arr.append(message.text)
    await message.answer("Введите E-mail")
    await state.finish()
    await Step.reg_email.set()
dp.register_message_handler(registr_fourth_step, state=Step.reg_surname)

async def registr_fifth_step(message: types.Message, state):
    global registr_arr
    email = message.text
    email = email.lower()
    if validate_email(email) == False:
        await message.answer("Некорректно введен E-mail. Пожалуйста, повторите попытку ввода.")
        await state.finish()
        await Step.reg_email.set()
    else:
        zapros = 'http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Email=' + email
        response = requests.get(zapros)
        response1 = response.text
        response1 = response1.replace("[", "")
        response1 = response1.replace("]", "")
        if response1 != "":
            await message.answer("Пользователь с таким E-mail уже зарегистрирован. Пожалуйста, укажите другой E-mail.")
            await state.finish()
            await Step.reg_email.set()
        else:
            registr_arr.append(email)
            keyboard = types.ReplyKeyboardMarkup()
            button_1 = types.KeyboardButton(text="Мужской")
            keyboard.add(button_1)
            button_2 = types.KeyboardButton(text="Женский")
            keyboard.add(button_2)
            await message.answer("При помощи кнопок укажите ваш пол", reply_markup=keyboard)
            await state.finish()
            await Step.reg_gender.set()
dp.register_message_handler(registr_fifth_step, state=Step.reg_email)

async def registr_sixth_step(message: types.Message, state):
    global registr_arr
    cont = False
    if message.text == "Мужской":
        registr_arr.append("Мужчина")
        cont = True
    elif message.text == "Женский":
        registr_arr.append("Женщина")
        cont = True
    else:
        await state.finish()
        await Step.reg_isSportsman.set()
        keyboard = types.ReplyKeyboardMarkup()
        button_1 = types.KeyboardButton(text="Мужской")
        keyboard.add(button_1)
        button_2 = types.KeyboardButton(text="Женский")
        keyboard.add(button_2)
        await message.answer("Введены некорректные данные. Пожалуйста, используйте кнопки.", reply_markup=keyboard)
    if cont:
        keyboard = types.ReplyKeyboardMarkup()
        button_1 = types.KeyboardButton(text="Да")
        keyboard.add(button_1)
        button_2 = types.KeyboardButton(text="Нет")
        keyboard.add(button_2)
        await message.answer("Являетесь ли вы профессианальным спортсменом?\nПри помощи кнопок укажите ответ.", reply_markup=keyboard)
        await state.finish()
        await Step.reg_isSportsman.set()
dp.register_message_handler(registr_sixth_step, state=Step.reg_gender)

async def registr_seventh_step(message: types.Message, state):
    global registr_arr
    cont = False
    if message.text == "Да":
        registr_arr.append(True)
        cont = True
    elif message.text == "Нет":
        registr_arr.append(False)
        cont = True
    else:
        await state.finish()
        await Step.reg_isSportsman.set()
        keyboard = types.ReplyKeyboardMarkup()
        button_1 = types.KeyboardButton(text="Да")
        keyboard.add(button_1)
        button_2 = types.KeyboardButton(text="Нет")
        keyboard.add(button_2)
        await message.answer("Введены некорректные данные. Пожалуйста, используйте кнопки.", reply_markup=keyboard)
    if cont:
        keyboard = types.ReplyKeyboardRemove()
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup()
        button_1 = types.KeyboardButton(text="Создать команду")
        keyboard.add(button_1)
        button_2 = types.KeyboardButton(text="Мои команды")
        keyboard.add(button_2)
        button_3 = types.KeyboardButton(text="Создать мероприятие")
        keyboard.add(button_3)
        button_4 = types.KeyboardButton(text="Мои мероприятия")
        keyboard.add(button_4)
        button_5 = types.KeyboardButton(text="Найти мероприятие")
        keyboard.add(button_5)
        button_6 = types.KeyboardButton(text="Настройки")
        keyboard.add(button_6)
        await message.answer(registr_arr, reply_markup=keyboard)
        #print(registr_arr[0])
        requests.post('http://167.172.35.241/CSDB/Users/?Content-Type=application/json', data={'Phone':registr_arr[0], 'Nickname':registr_arr[1], 'Password':registr_arr[2], 'Name':registr_arr[3], 'Surname':registr_arr[4], 'Email':registr_arr[5], 'Gender':registr_arr[6], 'Profsportman':registr_arr[7]})
        await message.answer("Вы успешно зарегистрировались на сервисе CoSport!", reply_markup=keyboard)
dp.register_message_handler(registr_seventh_step, state=Step.reg_isSportsman)










if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)