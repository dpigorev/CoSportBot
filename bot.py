import logging
import time
from collections import OrderedDict
import threading
from aiogram import Bot, Dispatcher, executor, types
from os import getenv
from sys import exit
import requests
import json
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime
import re

class Step(StatesGroup):
    reg_start = State()
    reg_nickname = State()
    reg_name = State()
    reg_surname = State()
    reg_pass = State()
    reg_email = State()
    reg_isSportsman = State()
    reg_gender = State()
    coordinates = State()
    repeat_reg = State()
    create_teams_one = State()
    create_teams_two = State()
    create_teams_three = State()
    create_teams_four = State()

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

regex_nickname = re.compile("^[A-Za-z0-9]+$")
regex_email = re.compile("^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,6}$")
regex_pas = re.compile("(?=.*[0-9])(?=.*[!@#$%^&_*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^_&*]{8,}")
regex_teamName = re.compile("^[a-zA-Z0-9]+$")

registr_arr = []
teams_arr = []

async def check(message):
    url = "http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Nickname=qartz"
    response = requests.get(url)
    response1 = response.text
    response1 = response1.replace("[", "")
    response1 = response1.replace("]", "")
    print(response1 + "пусто")
dp.register_message_handler(check, commands="check")

async def show(message):
    await message.answer(message.from_user.id)
dp.register_message_handler(show, commands="show")

async def add(message):
    a = requests.post('http://167.172.35.241/CSDB/Users/',
                  data={"Phone": "79209217373", "Nickname": "adfsf", "Password": "qwerty",
                        "Name": "Ivan", "Surname": "Ivanov", "Email": "artjom200006@yandex.ru",
                        "Gender": "m", "Profsportman": True})
    print("ADD")
    print(a)
    url = "http://167.172.35.241/CSDB/Users/"

dp.register_message_handler(add, commands="add")


async def cmd_phonenumber(message, state):
    keyboard = types.ReplyKeyboardMarkup()
    button_1 = types.KeyboardButton(text="Авторизоваться по номеру телефона", request_contact=True)
    keyboard.add(button_1)
    await state.finish()
    await message.answer("Нажмите на кнопку, чтобы подтвердить передачу номера телефона", reply_markup=keyboard)
dp.register_message_handler(cmd_phonenumber, commands="start")
dp.register_message_handler(cmd_phonenumber, state=Step.repeat_reg)

async def autorization(message):
    phone_number = str(message.contact.phone_number)
    zapros = 'http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Phone=' + phone_number
    response = requests.get(zapros)
    response1 = response.text
    response1 = response1.replace("[", "")
    response1 = response1.replace("]", "")
    print("test")
    print(response1)
    if response1 != "":
        response2 = json.loads(response1)
        Name = response2["Name"]
        keyboard = types.ReplyKeyboardMarkup()
        button_1 = types.KeyboardButton(text="Передать геопозицию", request_location=True)
        keyboard.add(button_1)
        await message.answer("Здравствуйте, " + Name + "!", reply_markup=keyboard)
        await message.answer("Пожалуйста, передайте вашу геопозицию, чтобы мы могли предлагать вам ближайшие спортплощадки.")
        await message.answer("Вы всегда можете обновить свои координаты в Настройках, чтобы получать наиболее актуальную информацию.")

    else:
        keyboard = types.ReplyKeyboardMarkup()
        button_1 = types.KeyboardButton(text="Зарегистрироваться!")
        keyboard.add(button_1)
        if phone_number[0] == "+":
            phone_number = phone_number[1:100]
        time = datetime.now()

        registr_arr.append([str(message.from_user.id), time, phone_number])
        print(registr_arr)

        await Step.reg_start.set()
        await message.answer("Вы не зарегистрированы на нашем сервисе. Нажмите на кнопку 'Зарегистрироваться!' чтобы пройти регистрацию. ", reply_markup=keyboard)
dp.register_message_handler(autorization, content_types=["contact"])

async def registration(message, state):
    keyboard = types.ReplyKeyboardRemove()
    await state.finish()
    await Step.reg_nickname.set()
    await message.answer("Введите Nickname\nNickname может содержать только цифры и буквы латинского алфавита", reply_markup=keyboard)
dp.register_message_handler(registration, state=Step.reg_start)

async def registr_first_step(message: types.Message, state):
    global registr_arr
    cont = False
    circle = True
    nickname = message.text
    nickname = nickname.lower()
    if regex_nickname.findall(nickname) != []:
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
                nickname = message.text + str(i)
                nickname = nickname.lower()
                zapros = 'http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Nickname=' + nickname
                response = requests.get(zapros)
                response1 = response.text
                response1 = response1.replace("[", "")
                response1 = response1.replace("]", "")
                if response1 == "":
                    cont = True
                    break
                if i == 9:
                    await message.answer("Такой Nickname уже занят. Пожалуйста, выберите другой.")
                    await message.answer("Введите Nickname\nNickname может содержать только цифры и буквы латинского алфавита")
                    await state.finish()
                    await Step.reg_nickname.set()
                    break
        if cont:
            next = False
            for i in range(0, len(registr_arr)):
                if registr_arr[i][0] == str(message.from_user.id):
                    registr_arr[i].append(nickname)
                    registr_arr[i][1] = datetime.now()
                    next = True
                    print(registr_arr)
                    break
            if next:
                await message.answer("Ваш Nickname - " + nickname)
                await message.answer("Введите пароль\nВнимание! Пароль должен содержать не менее 8 символов, при этом не менее одного строчного и прописного символа, одной цифры и одного спецсимвола!")
                await state.finish()
                await Step.reg_pass.set()
            else:
                await state.finish()
                keyboard = types.ReplyKeyboardMarkup()
                button_1 = types.KeyboardButton(text="Повторить регистрацию или авторизоваться")
                keyboard.add(button_1)
                await message.answer("С момента начала регистрации прошло более 1 дня. Пожалуйста, повторите регистрацию или авторизуйтесь в сервисе, если вы уже зарегистрированы.", reply_markup=keyboard)
                await Step.repeat_reg.set()
    else:
        await state.finish()
        await Step.reg_nickname.set()
        await message.answer("Введён некорректный Nickname. Повторите попытку ввода.")
dp.register_message_handler(registr_first_step, state=Step.reg_nickname)

async def registr_second_step(message: types.Message, state):
    global registr_arr
    pas = message.text
    repeat = False
    if regex_pas.findall(pas) == []:
        await state.finish()
        await Step.reg_pass.set()
        repeat = True
        await message.answer('Введенный пароль не соответствует требованиям. Пожалуйста, повторите попытку.')
    else:
        next = False
        for i in range(0, len(registr_arr)):
            if registr_arr[i][0] == str(message.from_user.id):
                registr_arr[i].append(message.text)
                registr_arr[i][1] = datetime.now()
                next = True
                print(registr_arr)
                break
        if next:
            await message.answer("Введите имя")
            await state.finish()
            await Step.reg_name.set()
        else:
            await state.finish()
            keyboard = types.ReplyKeyboardMarkup()
            button_1 = types.KeyboardButton(text="Повторить регистрацию или авторизоваться")
            keyboard.add(button_1)
            await message.answer("С момента начала регистрации прошло более 1 дня. Пожалуйста, повторите регистрацию или авторизуйтесь в сервисе, если вы уже зарегистрированы.", reply_markup=keyboard)
            await Step.repeat_reg.set()
dp.register_message_handler(registr_second_step, state=Step.reg_pass)

async def registr_third_step(message: types.Message, state):
    global registr_arr
    next = False
    for i in range(0, len(registr_arr)):
        if registr_arr[i][0] == str(message.from_user.id):
            registr_arr[i].append(message.text)
            registr_arr[i][1] = datetime.now()
            next = True
            print(registr_arr)
            break
    if next:
        await message.answer("Введите фамилию")
        await state.finish()
        await Step.reg_surname.set()
    else:
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup()
        button_1 = types.KeyboardButton(text="Повторить регистрацию или авторизоваться")
        keyboard.add(button_1)
        await message.answer(
            "С момента начала регистрации прошло более 1 дня. Пожалуйста, повторите регистрацию или авторизуйтесь в сервисе, если вы уже зарегистрированы.",
            reply_markup=keyboard)
        await Step.repeat_reg.set()
dp.register_message_handler(registr_third_step, state=Step.reg_name)

async def registr_fourth_step(message: types.Message, state):
    global registr_arr
    next = False
    for i in range(0, len(registr_arr)):
        if registr_arr[i][0] == str(message.from_user.id):
            registr_arr[i].append(message.text)
            registr_arr[i][1] = datetime.now()
            next = True
            print(registr_arr)
            break
    if next:
        await message.answer("Введите E-mail")
        await state.finish()
        await Step.reg_email.set()
    else:
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup()
        button_1 = types.KeyboardButton(text="Повторить регистрацию или авторизоваться")
        keyboard.add(button_1)
        await message.answer(
            "С момента начала регистрации прошло более 1 дня. Пожалуйста, повторите регистрацию или авторизуйтесь в сервисе, если вы уже зарегистрированы.",
            reply_markup=keyboard)
        await Step.repeat_reg.set()
dp.register_message_handler(registr_fourth_step, state=Step.reg_surname)

async def registr_fifth_step(message: types.Message, state):
    global registr_arr
    email = message.text
    email = email.lower()
    if regex_email.findall(email) == []:
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
            next = False
            for i in range(0, len(registr_arr)):
                if registr_arr[i][0] == str(message.from_user.id):
                    registr_arr[i].append(email)
                    registr_arr[i][1] = datetime.now()
                    next = True
                    print(registr_arr)
                    break
            if next:
                keyboard = types.ReplyKeyboardMarkup()
                button_1 = types.KeyboardButton(text="Мужской")
                keyboard.add(button_1)
                button_2 = types.KeyboardButton(text="Женский")
                keyboard.add(button_2)
                await message.answer("При помощи кнопок укажите ваш пол", reply_markup=keyboard)
                await state.finish()
                await Step.reg_gender.set()
            else:
                await state.finish()
                keyboard = types.ReplyKeyboardMarkup()
                button_1 = types.KeyboardButton(text="Повторить регистрацию или авторизоваться")
                keyboard.add(button_1)
                await message.answer(
                    "С момента начала регистрации прошло более 1 дня. Пожалуйста, повторите регистрацию или авторизуйтесь в сервисе, если вы уже зарегистрированы.",
                    reply_markup=keyboard)
                await Step.repeat_reg.set()
dp.register_message_handler(registr_fifth_step, state=Step.reg_email)

async def registr_sixth_step(message: types.Message, state):
    global registr_arr
    cont = False
    if message.text == "Мужской":
        next = False
        for i in range(0, len(registr_arr)):
            if registr_arr[i][0] == str(message.from_user.id):
                registr_arr[i].append("Male")
                registr_arr[i][1] = datetime.now()
                next = True
                print(registr_arr)
                break
        if next:
            cont = True
        else:
            await state.finish()
            keyboard = types.ReplyKeyboardMarkup()
            button_1 = types.KeyboardButton(text="Повторить регистрацию или авторизоваться")
            keyboard.add(button_1)
            await message.answer(
                "С момента начала регистрации прошло более 1 дня. Пожалуйста, повторите регистрацию или авторизуйтесь в сервисе, если вы уже зарегистрированы.",
                reply_markup=keyboard)
            await Step.repeat_reg.set()
    elif message.text == "Женский":
        next = False
        for i in range(0, len(registr_arr)):
            if registr_arr[i][0] == str(message.from_user.id):
                registr_arr[i].append("Female")
                registr_arr[i][1] = datetime.now()
                next = True
                print(registr_arr)
                break
        if next:
            cont = True
        else:
            await state.finish()
            keyboard = types.ReplyKeyboardMarkup()
            button_1 = types.KeyboardButton(text="Повторить регистрацию или авторизоваться")
            keyboard.add(button_1)
            await message.answer(
                "С момента начала регистрации прошло более 1 дня. Пожалуйста, повторите регистрацию или авторизуйтесь в сервисе, если вы уже зарегистрированы.",
                reply_markup=keyboard)
            await Step.repeat_reg.set()
    else:
        await state.finish()
        await Step.reg_gender.set()
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
    pos = None
    if message.text == "Да":
        for i in range(0, len(registr_arr)):
            if registr_arr[i][0] == str(message.from_user.id):
                registr_arr[i].append(True)
                registr_arr[i][1] = datetime.now()
                cont = True
                pos = i
                print(registr_arr)
                break
        if not cont:
            await state.finish()
            keyboard = types.ReplyKeyboardMarkup()
            button_1 = types.KeyboardButton(text="Повторить регистрацию или авторизоваться")
            keyboard.add(button_1)
            await message.answer(
                "С момента начала регистрации прошло более 1 дня. Пожалуйста, повторите регистрацию или авторизуйтесь в сервисе, если вы уже зарегистрированы.",
                reply_markup=keyboard)
            await Step.repeat_reg.set()
    elif message.text == "Нет":
        for i in range(0, len(registr_arr)):
            if registr_arr[i][0] == str(message.from_user.id):
                registr_arr[i].append(False)
                registr_arr[i][1] = datetime.now()
                cont = True
                pos = i
                print(registr_arr)
                break
        if not cont:
            await state.finish()
            keyboard = types.ReplyKeyboardMarkup()
            button_1 = types.KeyboardButton(text="Повторить регистрацию или авторизоваться")
            keyboard.add(button_1)
            await message.answer(
                "С момента начала регистрации прошло более 1 дня. Пожалуйста, повторите регистрацию или авторизуйтесь в сервисе, если вы уже зарегистрированы.",
                reply_markup=keyboard)
            await Step.repeat_reg.set()
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
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup()
        button_1 = types.KeyboardButton(text="Передать геопозицию", request_location=True)
        keyboard.add(button_1)
        await message.answer("Вы успешно зарегистрировались на сервисе CoSport!", reply_markup=keyboard)
        await message.answer("Пожалуйста, передайте вашу геопозицию, чтобы мы могли предлагать вам ближайшие спортплощадки.")
        await message.answer("Вы всегда можете обновить свои координаты в Настройках, чтобы получать наиболее актуальную информацию.")
        zapros1 = 'http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Phone=' + registr_arr[pos][2]
        zapros2 = 'http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Nickname=' + registr_arr[pos][3]
        zapros3 = 'http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Email=' + registr_arr[pos][7]
        response1 = requests.get(zapros1)
        response2 = requests.get(zapros2)
        response3 = requests.get(zapros3)
        response11 = response1.text
        response11 = response11.replace("[", "")
        response11 = response11.replace("]", "")
        response21 = response2.text
        response21 = response21.replace("[", "")
        response21 = response21.replace("]", "")
        response31 = response3.text
        response31 = response31.replace("[", "")
        response31 = response31.replace("]", "")

        if response11 == "" and response21 == "" and response31 == "":
            print("Переданный массив")
            print(registr_arr)
            dt = {'Tg_id': registr_arr[pos][0], 'Phone': registr_arr[pos][2],
                                'Nickname': registr_arr[pos][3], 'Password': registr_arr[pos][4],
                                'Name': registr_arr[pos][5], 'Surname': registr_arr[pos][6],
                                'Email': registr_arr[pos][7], 'Gender': registr_arr[pos][8],
                                'Profsportman': registr_arr[pos][9], 'City': 'Москва'}
            dtt = json.dumps(dt)
            url = 'http://167.172.35.241/CSDB/Users/'
            #requests.post('http://167.172.35.241/CSDB/Users/',
             #             data={'Tg_id': registr_arr[pos][0], 'Phone': registr_arr[pos][2],
              #                  'Nickname': registr_arr[pos][3], 'Password': registr_arr[pos][4],
               #                 'Name': registr_arr[pos][5], 'Surname': registr_arr[pos][6],
                #                'Email': registr_arr[pos][7], 'Gender': registr_arr[pos][8],
                 #               'Profsportman': registr_arr[pos][9]})
            a = requests.post(url, data=dtt)
            print(a)
            registr_arr.pop(pos)
            print("Массив после чистки")
            print(registr_arr)
        else:
            await Step.repeat_reg.set()
            keyboard = types.ReplyKeyboardMarkup()
            button_1 = types.KeyboardButton(text="Повторить регистрацию")
            keyboard.add(button_1)
            await message.answer("Пользователь с таким номером телефона/Nickname/Email уже зарегистрирован.\nПожалуйста, повторите попытку регистрации",reply_markup=keyboard)
dp.register_message_handler(registr_seventh_step, state=Step.reg_isSportsman)


async def settings(message):
    keyboard = types.ReplyKeyboardMarkup()
    button_1 = types.KeyboardButton(text="Обновить геопозицию", request_location=True)
    keyboard.add(button_1)
    await message.answer("При помощи кнопок выберите интересующий вас пункт меню", reply_markup=keyboard)
dp.register_message_handler(settings, Text(equals="⚙ Настройки ⚙"))


async def get_coordinates(message: types.location, state):
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
    button_6 = types.KeyboardButton(text="⚙ Настройки ⚙")
    keyboard.add(button_6)
    lat =  message.location.latitude
    long = message.location.longitude
    zapros = 'http://167.172.35.241/CSDB/Users/?Content-Type=application/json&Tg_id=' + str(message.from_user.id)
    response = requests.get(zapros)
    response1 = response.text
    response1 = response1.replace("[", "")
    response1 = response1.replace("]", "")
    print(response1)
    response2 = json.loads(response1)
    pk = response2["pk"]
    print(pk)
    url = 'http://167.172.35.241/CSDB/Users/'+str(pk)
    response2['GeoCoords_Longitude'] = long
    response2['GeoCoords_Latitude'] = lat
    dtt = json.dumps(response2)
    print(dtt)
    a = requests.put(url, data=dtt)
    await message.answer("Широта: " + str(message.location.latitude) + "\nДолгота: " + str(message.location.longitude), reply_markup=keyboard)
dp.register_message_handler(get_coordinates, content_types=["location"])

#Создание команд

async def create_teams_start(message):
    await Step.create_teams_one.set()
    keyboard = types.ReplyKeyboardMarkup()
    button_6 = types.KeyboardButton(text="Назад")
    keyboard.add(button_6)
    await message.answer("Введите название команды", reply_markup=keyboard)
dp.register_message_handler(create_teams_start, Text(equals="Создать команду"))

async def create_teams_1(message, state):
    if regex_teamName.findall(message.text) != []:
        if message.text == "Назад":
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
            button_6 = types.KeyboardButton(text="⚙ Настройки ⚙")
            keyboard.add(button_6)
        else:
            team_name = message.text
            time = datetime.now()
            teams_arr.append([str(message.from_user.id), time, team_name, "Москва"])
            print(teams_arr)
            await Step.create_teams_one.set()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_1 = types.KeyboardButton(text="Баскетбол")
            button_2 = types.KeyboardButton(text="Бег")
            button_3 = types.KeyboardButton(text="Хоккей")
            button_4 = types.KeyboardButton(text="Теннис")
            button_5 = types.KeyboardButton(text="Бейсбол")
            button_6 = types.KeyboardButton(text="Волейбол")
            button_7 = types.KeyboardButton(text="Регби")
            button_8 = types.KeyboardButton(text="Бокс")
            button_9 = types.KeyboardButton(text="Т.Атлетика")
            button_10 = types.KeyboardButton(text="Велоспорт")
            button_11 = types.KeyboardButton(text="Воркаут")
            button_12 = types.KeyboardButton(text="Настольный теннис")
            button_13 = types.KeyboardButton(text="Фитнес")
            button_14 = types.KeyboardButton(text="Н.Игры")
            button_15 = types.KeyboardButton(text="Скейтборд")
            button_16 = types.KeyboardButton(text="Футбол")
            keyboard.insert(button_1)
            keyboard.insert(button_2)
            keyboard.insert(button_3)
            keyboard.insert(button_4)
            keyboard.insert(button_5)
            keyboard.insert(button_6)
            keyboard.insert(button_7)
            keyboard.insert(button_8)
            keyboard.insert(button_9)
            keyboard.insert(button_10)
            keyboard.insert(button_11)
            keyboard.insert(button_12)
            keyboard.insert(button_13)
            keyboard.insert(button_14)
            keyboard.insert(button_15)
            keyboard.insert(button_16)
            button_prev = types.KeyboardButton(text="Главное меню")
            keyboard.add(button_prev)
            await message.answer("Выберите виды спорта, нажимая на соответствующие кнопки", reply_markup=keyboard)
            await state.finish()
            await Step.create_teams_two.set()
    else:
        await state.finish()
        await Step.create_teams_one.set()
        keyboard = types.ReplyKeyboardMarkup()
        button_6 = types.KeyboardButton(text="Назад")
        keyboard.add(button_6)
        await message.answer("Некорректно введено название команды. Пожалуйста, повторите попытку ввода.", reply_markup=keyboard)
dp.register_message_handler(create_teams_1, state=Step.create_teams_one)

async def create_teams_2(message, state):
    sport = message.text
    if sport == "Главное меню" or sport == "Далее" or sport == "Баскетбол" or sport == "Бег" or sport == "Хоккей" or sport == "Теннис" or sport == "Бейсбол" or sport == "Волейбол" or sport == "Хоккей" or sport == "Регби" or sport == "Бокс" or sport == "Т.Атлетика" or sport == "Велоспорт" or sport == "Воркаут" or sport == "Настольный теннис" or sport == "Фитнес"or sport == "Н.Игры"or sport == "Скейтборд" or sport == "Футбол":
        if sport == "Главное меню":
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
            button_6 = types.KeyboardButton(text="⚙ Настройки ⚙")
            keyboard.add(button_6)
            await message.answer("Главное меню", reply_markup=keyboard)
            for i in range(0, len(teams_arr)):
                if teams_arr[i][0] == str(message.from_user.id):
                    teams_arr.pop(i)
                    print(teams_arr)
                    break
        elif sport == "Далее":
            next = False
            pos = -1
            for i in range(0, len(teams_arr)):
                if teams_arr[i][0] == str(message.from_user.id):
                    teams_arr[i][1] = datetime.now()
                    next = True
                    pos = i
                    print(teams_arr)
                    print(type(teams_arr))
                    break
            if next:
                teams_arr[pos] = list(OrderedDict.fromkeys(teams_arr[pos]))
                print(teams_arr)
                print(type(teams_arr))
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
                button_6 = types.KeyboardButton(text="⚙ Настройки ⚙")
                keyboard.add(button_6)
                await state.finish()
                await Step.create_teams_three.set()
                await message.answer("Выберите спортплощадку по умолчанию", reply_markup=keyboard)
            else:
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
                button_6 = types.KeyboardButton(text="⚙ Настройки ⚙")
                keyboard.add(button_6)
                await message.answer("С момента начала создания команды прошло более 24 часов. Повторите создание команды заново.", reply_markup=keyboard)
        else:
            next = False
            for i in range(0, len(teams_arr)):
                if teams_arr[i][0] == str(message.from_user.id):
                    teams_arr[i].append(sport)
                    teams_arr[i][1] = datetime.now()
                    next = True
                    print(teams_arr)
                    break
            if next:
                await state.finish()
                await Step.create_teams_two.set()
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button_1 = types.KeyboardButton(text="Баскетбол")
                button_2 = types.KeyboardButton(text="Бег")
                button_3 = types.KeyboardButton(text="Хоккей")
                button_4 = types.KeyboardButton(text="Теннис")
                button_5 = types.KeyboardButton(text="Бейсбол")
                button_6 = types.KeyboardButton(text="Волейбол")
                button_7 = types.KeyboardButton(text="Регби")
                button_8 = types.KeyboardButton(text="Бокс")
                button_9 = types.KeyboardButton(text="Т.Атлетика")
                button_10 = types.KeyboardButton(text="Велоспорт")
                button_11 = types.KeyboardButton(text="Воркаут")
                button_12 = types.KeyboardButton(text="Настольный теннис")
                button_13 = types.KeyboardButton(text="Фитнес")
                button_14 = types.KeyboardButton(text="Н.Игры")
                button_15 = types.KeyboardButton(text="Скейтборд")
                button_16 = types.KeyboardButton(text="Футбол")
                keyboard.insert(button_1)
                keyboard.insert(button_2)
                keyboard.insert(button_3)
                keyboard.insert(button_4)
                keyboard.insert(button_5)
                keyboard.insert(button_6)
                keyboard.insert(button_7)
                keyboard.insert(button_8)
                keyboard.insert(button_9)
                keyboard.insert(button_10)
                keyboard.insert(button_11)
                keyboard.insert(button_12)
                keyboard.insert(button_13)
                keyboard.insert(button_14)
                keyboard.insert(button_15)
                keyboard.insert(button_16)
                button_next = types.KeyboardButton(text="Далее")
                keyboard.add(button_next)
                button_prev = types.KeyboardButton(text="Главное меню")
                keyboard.add(button_prev)
                await message.answer("Выбранный вид спорта сохранён", reply_markup=keyboard)

            else:
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
                button_6 = types.KeyboardButton(text="⚙ Настройки ⚙")
                keyboard.add(button_6)
                await message.answer(
                    "С момента начала создания команды прошло более 24 часов. Повторите создание команды заново.",
                    reply_markup=keyboard)
    else:
        next = False
        length = -1
        for i in range(0, len(teams_arr)):
            if teams_arr[i][0] == str(message.from_user.id):
                next = True
                length = len(teams_arr[i])
                print(teams_arr)
                break
        if next:
            await state.finish()
            await Step.create_teams_two.set()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_1 = types.KeyboardButton(text="Баскетбол")
            button_2 = types.KeyboardButton(text="Бег")
            button_3 = types.KeyboardButton(text="Хоккей")
            button_4 = types.KeyboardButton(text="Теннис")
            button_5 = types.KeyboardButton(text="Бейсбол")
            button_6 = types.KeyboardButton(text="Волейбол")
            button_7 = types.KeyboardButton(text="Регби")
            button_8 = types.KeyboardButton(text="Бокс")
            button_9 = types.KeyboardButton(text="Т.Атлетика")
            button_10 = types.KeyboardButton(text="Велоспорт")
            button_11 = types.KeyboardButton(text="Воркаут")
            button_12 = types.KeyboardButton(text="Настольный теннис")
            button_13 = types.KeyboardButton(text="Фитнес")
            button_14 = types.KeyboardButton(text="Н.Игры")
            button_15 = types.KeyboardButton(text="Скейтборд")
            button_16 = types.KeyboardButton(text="Футбол")
            keyboard.insert(button_1)
            keyboard.insert(button_2)
            keyboard.insert(button_3)
            keyboard.insert(button_4)
            keyboard.insert(button_5)
            keyboard.insert(button_6)
            keyboard.insert(button_7)
            keyboard.insert(button_8)
            keyboard.insert(button_9)
            keyboard.insert(button_10)
            keyboard.insert(button_11)
            keyboard.insert(button_12)
            keyboard.insert(button_13)
            keyboard.insert(button_14)
            keyboard.insert(button_15)
            keyboard.insert(button_16)
            if length == 4:
                button_prev = types.KeyboardButton(text="Главное меню")
                keyboard.add(button_prev)
            else:
                button_next = types.KeyboardButton(text="Далее")
                keyboard.add(button_next)
                button_prev = types.KeyboardButton(text="Главное меню")
                keyboard.add(button_prev)
            await message.answer("Вид спорта введен некорректно. Пожалуйста, используйте кнопки для выбора вида спорта.", reply_markup=keyboard)
        else:
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
            button_6 = types.KeyboardButton(text="⚙ Настройки ⚙")
            keyboard.add(button_6)
            await message.answer(
                "С момента начала создания команды прошло более 24 часов. Повторите создание команды заново.",
                reply_markup=keyboard)
dp.register_message_handler(create_teams_2, state=Step.create_teams_two)

check_time = datetime.strptime('2021-07-14 04:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
def clear_reg_array():
    global check_time
    global registr_arr
    while True:
        time.sleep(3)
        secs = check_time - datetime.now()
        secs = secs.seconds
        #print(secs)
        if secs < 3:
            length = len(registr_arr)
            print("До изменений")
            print(registr_arr)
            a = False
            for i in range(0, length):
                if a:
                    i = i - 1
                    length = length - 1
                a = False
                if (datetime.now() - registr_arr[i][1]).days > 1:
                    print((datetime.now() - registr_arr[i][1]).days)
                    registr_arr.pop(i)
                    a = True
                    print(registr_arr)


if __name__ == "__main__":
    # Запуск бота
    x = threading.Thread(target=clear_reg_array)
    x.start()
    executor.start_polling(dp, skip_updates=True)
