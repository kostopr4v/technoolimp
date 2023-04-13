import logging
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3
import random
import nest_asyncio

nest_asyncio.apply()
bot = Bot(token="5698793612:AAF4EbhCPIxzRw7Zh0tvoSYhHas6FS35KtQ")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
con = sqlite3.connect("techno.db")
cur = con.cursor()


class Name(StatesGroup):
    name = State()


class ID(StatesGroup):
    pr_id = State()


class exterminate(StatesGroup):
    ex = State()


class problem(StatesGroup):
    pr = State()


class razdel(StatesGroup):
    pr = State()


class info(StatesGroup):
    pr = State()


class pod_z(StatesGroup):
    amongus = State()


class problem_state(StatesGroup):
    problem = State()

class vipol(StatesGroup):
    vip = State()

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    query = f"SELECT ФИО FROM users WHERE UserID = {message.from_user.id}"
    cur.execute(query)
    tmp = cur.fetchall()
    if tmp == []:
        buttons = ["Пройти регистрацию"]
        keyboard.add(*buttons)
        await message.answer(
            'Добро пожаловать, я — бот-менеджер проблем компании. Похоже, Вы тут впервые. Чтобы приступить к работе, пройдите процедуру регистрации.',
            reply_markup=keyboard)
    else:
        buttons = ["Начать работу"]
        keyboard.add(*buttons)
        await message.answer(f'Здравствуйте, {tmp[0][0]}', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Пройти регистрацию")
async def reg(message: types.Message):
    await Name.name.set()
    await message.answer(f"Введите свое ФИО:")


@dp.message_handler(state=Name.name)
async def wr(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        query = f"SELECT COUNT(*) FROM users"
        cur.execute(query)
        ident = cur.fetchone()[0]
        query = f"INSERT INTO users (UserID, ID, ФИО) VALUES ('{message.from_user.id}', '{ident}', '{user_message}')"
        cur.execute(query)
        con.commit()
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Директор", "Заместитель директора", "Подчиненный директора", "Сотрудник"]
    keyboard.add(*buttons)
    await message.answer("Теперь выберите свою роль:", reply_markup=keyboard)


@dp.message_handler(
    lambda message: message.text in ["Директор", "Заместитель директора", "Подчиненный директора", "Сотрудник"])
async def wr(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Начать работу"]
    keyboard.add(*buttons)
    query = f"UPDATE users SET Роль = '{message.text}' WHERE (UserID) = ({message.from_user.id})"
    cur.execute(query)
    con.commit()
    await message.answer("Вы зарегистрированы!", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text in ["Начать работу", "Назад"])
async def wrap(message: types.Message, state: FSMContext):
    query = f"SELECT Роль FROM users WHERE UserID = ({message.from_user.id})"
    cur.execute(query)
    tmp = cur.fetchone()[0]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Мои заявки", "Сообщить о проблеме", "Поданные заявки"] if tmp != "Сотрудник" else ["Мои заявки",
                                                                                                   "Сообщить о проблеме",
                                                                                                   "Групповые заявки"]
    keyboard.add(*buttons)
    await message.answer("Выберите действие: ", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text in ["Поданные заявки", "Групповые заявки"])
async def wr(message: types.Message, state: FSMContext):
    query = f"SELECT Роль FROM users WHERE UserID = ({message.from_user.id})"
    cur.execute(query)
    role = cur.fetchone()[0]
    query = f"SELECT * FROM problems_list"
    cur.execute(query)
    tmp = cur.fetchall()

    need = []
    if tmp:
        if role == "Сотрудник":
            for i in tmp:
                i = list(i)
                if (i[-3] != "Индивидуальная" and i[2] != message.from_user.id):
                    need.append(i)
            proc = str(
                "В процессе:\n" + "".join(
                    [i[1] + f"- {i[-1]}" + f" (Добавил - {i[4]})" + "\n" for i in need if i[3] == 1]))
            nfulf = str(
                "Не выполнены:\n" + "".join(
                    [i[1] + f" {i[-1]}" + f" (Добавил - {i[4]})" + "\n" for i in need if i[3] == 0]))
            await message.answer(f"{proc}\n{nfulf}")

        elif role in ["Подчиненный директора", "Заместитель директора", "Директор"]:
            for i in tmp:
                i = list(i)
                if (i[2] != message.from_user.id):
                    need.append(i)

            vipo = str(
                "Выполнено:\n" + "".join(
                    [str(i[0]) + ") " + i[1] + f"- {i[-1]}" + f" (Добавил - {i[4]})" + "\n" for i in need if
                     i[3] == 2]))
            bezpotv = str(
                "Ожидает подтверждения:\n" + "".join(
                    [str(i[0]) + ") " + i[1] + f"- {i[-1]}" + f" (Добавил - {i[4]})" + "\n" for i in need if
                     i[3] == 3]))
            proc = str(
                "В процессе:\n" + "".join(
                    [str(i[0]) + ") " + i[1] + f"- {i[-1]}" + f" (Добавил - {i[4]})" + "\n" for i in need if
                     i[3] == 1]))
            nfulf = str(
                "Не выполнены:\n" + "".join(
                    [str(i[0]) + ") " + i[1] + f" {i[-1]}" + f" (Добавил - {i[4]})" + "\n" for i in need if i[3] == 0]))
            if role =='Подчиненный директора':
                await ID.pr_id.set()
                await message.answer(
                    f"{vipo}\n{bezpotv}\n{proc}\n{nfulf}\n\nЧтобы поменять статус проблемы, напишите ее номер:")
            else:
                await vipol.vip.set()
                await message.answer(f"{vipo}\n{bezpotv}\n{proc}\n{nfulf}\n\nЧтобы подтвердить выполнение проблемы, "
                                     f"напишите ее номер")

    else:
        fulf = "В данный момент проблем нет!"
        await message.answer(f"{fulf}")

@dp.message_handler(state=vipol.vip)
async def wr(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        global vip
        vip = data['text']
    await state.finish()
    print(vip)
    query = f"SELECT ID, Статус FROM problems_list WHERE ID ={vip}"
    cur.execute(query)
    tmp = list(cur.fetchone())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    buttons = ["Назад"]
    keyboard.add(*buttons)
    if int(vip) == tmp[0]:
        if tmp[1] == 3:
            query = f"UPDATE problems_list SET Статус = {2} WHERE ID = {vip}"
            cur.execute(query)
            con.commit()
            await message.answer("Вы подтвердили проблему", reply_markup=keyboard)
        else:
            await message.answer("Вы можете подтверждать только проблемы, ожидающие подтверждения", reply_markup=keyboard)

@dp.message_handler(state=ID.pr_id)
async def wr(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['text'] = message.text
            global pr_ident
            pr_ident = data['text']

        query = f"SELECT ID, Статус FROM problems_list WHERE ID ={pr_ident}"
        cur.execute(query)
        tmp = list(cur.fetchone())
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if tmp[1] != 2:
            if int(pr_ident) != tmp[0]:
                buttons = ["Назад"]
                keyboard.add(*buttons)
                await message.answer("Не очень Вас понял.", reply_markup=keyboard)
            else:
                buttons = ["Ожидает подтверждения", "В процессе", "Не выполнена"]
                keyboard.add(*buttons)
                await problem_state.problem.set()
                await message.answer("Теперь выберите статус проблемы:", reply_markup=keyboard)
        else:
            buttons = ["Назад"]
            keyboard.add(*buttons)
            await message.answer("Вы не можете менять статус выполненых проблем", reply_markup=keyboard)

    except:
        await wrap(message, state)


@dp.message_handler(state=problem_state.problem)
async def wr(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        global pr_id, pr_ident
        pr_id = data['text']
        amongus = pr_ident
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Назад"]
    keyboard.add(*buttons)
    if pr_id == "Ожидает подтверждения":
        tmp = 3
    elif pr_id == "В процессе":
        tmp = 1
    elif pr_id == "Не выполнена":
        tmp = 0
    query = f"UPDATE problems_list SET Статус = {tmp} WHERE ID = {amongus}"
    cur.execute(query)
    con.commit()

    query = f"SELECT UserID, Роль from users"
    users = [list(i) for i in cur.execute(query).fetchall()]
    con.commit()
    query = f"SELECT Проблема from problems_list WHERE ID={amongus}"
    problem = cur.execute(query).fetchone()

    for i in users:
        if message.from_user.id not in i:
            if "Заместитель директора" in i:
                await bot.send_message(i[0], f"Изменен статус проблемы:\n{list(problem)[0]}->{pr_id}")

    await message.answer(f"Выполнено!", reply_markup=keyboard)



@dp.message_handler(lambda message: message.text == "Сообщить о проблеме")
async def wr(message: types.Message, state: FSMContext):
    await razdel.pr.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Технические проблемы", "Хозяйственные проблемы и нужды", "Поддержка файловых ресурсов", "Иное"]
    keyboard.add(*buttons)
    await message.answer(f"Выберите подходящий сервис:", reply_markup=keyboard)


@dp.message_handler(state=razdel.pr)
async def wr(message: types.Message, state: FSMContext):
    await problem.pr.set()
    query = f"SELECT MAX(ID) FROM problems_list"
    cur.execute(query)
    ident = cur.fetchone()[0]

    query = f"INSERT INTO problems_list (ID, ID_автора, Razdel) VALUES " \
            f"('{ident + 1}', '{message.from_user.id}', '{message.text}')"
    cur.execute(query)
    con.commit()
    await message.answer(f"Опишите свою проблему:", reply_markup=None)


@dp.message_handler(state=problem.pr)
async def wr(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        import datetime
        data['text'] = message.text
        today = f"{datetime.date.today()}"
        time2 = f"{datetime.datetime.now():%H:%M}"
        print(time2)
        time = today + " " + time2

        message_text = data['text']
        query = f"SELECT (ФИО) FROM users WHERE UserID = {message.from_user.id}"
        cur.execute(query)
        fio = cur.fetchone()[0]
        query = f"UPDATE problems_list SET (Проблема, ID_автора, Статус, ФИО_автора, Time) = ('{message_text}', '{message.from_user.id}',  '{0}', '{fio}', '{time}') " \
                f"WHERE (ID_автора) = ({message.from_user.id}) AND " \
                f"(ID) = (SELECT MAX(ID) FROM problems_list)"

        cur.execute(query)
        con.commit()
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Индивидуальная", "Групповая"]
    keyboard.add(*buttons)
    await message.answer("Укажите тип заявки:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text in ["Индивидуальная", "Групповая"])
async def wr(message: types.Message, state: FSMContext):
    query = f"UPDATE problems_list SET Тип = '{message.text}' WHERE (ID_автора) = ({message.from_user.id}) AND " \
            f"(ID)= (SELECT MAX(ID) FROM problems_list)"
    cur.execute(query)
    con.commit()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Назад"]
    keyboard.add(*buttons)
    await message.answer("Проблема принята!", reply_markup=keyboard)

    query = f"SELECT UserID, Роль from users"
    users = [list(i) for i in cur.execute(query).fetchall()]
    con.commit()
    query = f"SELECT Razdel, Проблема from problems_list WHERE (ID_автора) = ({message.from_user.id}) AND " \
            f"(ID)= (SELECT MAX(ID) FROM problems_list)"
    problem = cur.execute(query).fetchone()
    con.commit()
    print(problem, users)
    for i in users:
        if message.from_user.id not in i:
            if "Подчиненный директора" in i:
                await bot.send_message(i[0], f"Добавлена новая проблема:\n{' - '.join(problem)} ({message.text})")
            else:
                if message.text == "Групповая":
                    await bot.send_message(i[0], f"Добавлена новая проблема:\n{' -'.join(problem)}")


@dp.message_handler(lambda message: message.text in ["Мои заявки", "Вернуться к выбору проблемы"])
async def wr(message: types.Message, state: FSMContext):
    query = f"SELECT Проблема, Статус, Тип, Time, ID, Razdel FROM problems_list WHERE ID_автора={message.from_user.id}"
    cur.execute(query)
    tmp = cur.fetchall()

    query = f"SELECT Роль FROM users WHERE UserID = ({message.from_user.id})"
    cur.execute(query)
    role = cur.fetchone()[0]

    need = []
    if len(tmp) > 0:
        if role == "Сотрудник":
            for i in range(len(tmp)):
                tmp[i] = list(tmp[i])
                k = tmp[i][1]
                tmp[i][1] = k
            tmp.sort(key=lambda row: row[1])
            fulf = str("Выполнены:\n" + "".join(
                [f"{str(i[-2])}) " + i[0] + f" - {i[-1]}" + " " + str(i[3]) + "\n" for i in tmp if i[1] == 2]))
            proc = str("В процессе:\n" + "".join(
                [f"{str(i[-2])}) " + i[0] + f" - {i[-1]}" + " " + str(i[3]) + "\n" for i in tmp if
                 (i[1] == 1 or i[1] == 3)]))
            nfulf = str("Не выполнены:\n" + "".join(
                [f"{str(i[-2])}) " + i[0] + f" - {i[-1]}" + " " + str(i[3]) + "\n" for i in tmp if i[1] == 0]))
            await info.pr.set()
            await message.answer(
                f"Количество ваших заявок: {len(tmp)}\n\n{fulf}\n{proc}\n{nfulf}\n\nЧтобы узнать подробнее о проблеме, введите ее номер:",
                reply_markup=types.ReplyKeyboardRemove())
        else:
            for i in range(len(tmp)):
                tmp[i] = list(tmp[i])
                k = tmp[i][1]
                tmp[i][1] = k
            tmp.sort(key=lambda row: row[1])
            fulf = str("Выполнены:\n" + "".join(
                [f"{str(i[-2])}) " + i[0] + f" - {i[-1]}" + " " + str(i[3]) + "\n" for i in tmp if i[1] == 3]))
            bezpotrv = str("Выполнены (без потверждения):\n" + "".join(
                [f"{str(i[-2])}) " + i[0] + f" - {i[-1]}" + " " + str(i[3]) + "\n" for i in tmp if i[1] == 2]))
            proc = str("В процессе:\n" + "".join(
                [f"{str(i[-2])}) " + i[0] + f" - {i[-1]}" + " " + str(i[3]) + "\n" for i in tmp if i[1] == 1]))
            nfulf = str("Не выполнены:\n" + "".join(
                [f"{str(i[-2])}) " + i[0] + f" - {i[-1]}" + " " + str(i[3]) + "\n" for i in tmp if i[1] == 0]))
            await info.pr.set()
            await message.answer(
                f"Количество ваших заявок: {len(tmp)}\n\n{fulf}\n{bezpotrv}\n{proc}\n{nfulf}\n\nЧтобы узнать подробнее о проблеме, введите ее номер:",
                reply_markup=types.ReplyKeyboardRemove())

    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Назад"]
        keyboard.add(*buttons)
        await message.answer(f"Количество ваших заявок: 0", reply_markup=keyboard)


@dp.message_handler(state=info.pr)
async def wr(message: types.Message, state: FSMContext):
    try:
        global amongus
        async with state.proxy() as data:
            data['text'] = message.text
            message_text = data['text']
            query = f"SELECT * FROM problems_list WHERE ID_автора = {message.from_user.id}"
            inform = [list(i) for i in cur.execute(query).fetchall()]
            inform.sort(key=lambda row: row[3])
            con.commit()
            await state.finish()
        for x in inform:
            if x[0] == int(message.text):
                inform = x
        query = f"SELECT Роль FROM users WHERE UserID = ({message.from_user.id})"
        cur.execute(query)
        role = cur.fetchone()[0]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Назад", "Вернуться к выбору проблемы", "Удалить проблему"]
        keyboard.add(*buttons)
        if role == "Сотрудник":
            stat = ["Не выполнена", "В процессе", "Выполнена", "В процессе"][inform[3]]
        else:
            stat = ["Не выполнена", "В процессе", "Выполнена", "Выполнена (без подтверждения)"][inform[3]]

        amongus = inform[0]
        await message.answer(
            f"Номер проблемы: {inform[0]}\n\nРаздел: {inform[7]}\nПроблема: {inform[1]}\n\nТип проблемы: {inform[5]}\nАвтор: {inform[4]}\nВремя создания: {inform[6]}\n\nСтатус: {stat}",
            reply_markup=keyboard)
    except:
        await wrap(message, state)


@dp.message_handler(lambda message: message.text == "Удалить проблему")
async def wr(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Назад"]
    keyboard.add(*buttons)
    query = f"DELETE FROM problems_list WHERE (ID) = ({amongus})"
    cur.execute(query)
    con.commit()
    a = cur.execute(f"SELECT ID FROM problems_list").fetchall()
    m_ind = cur.execute('SELECT MAX(ID) FROM problems_list').fetchone()
    await message.answer(f"Выполнено!", reply_markup=keyboard)


# @dp.message_handler(state=pod_z.amongus)
# async def wr(message: types.Message, state: FSMContext):
#     global amongus
#     async with state.proxy() as data:
#         data['text'] = message.text
#         message_text = data['text']
#         query = f"SELECT * FROM problems_list WHERE ID_автора = {message.from_user.id}"
#         inform = [list(i) for i in cur.execute(query).fetchall()]
#         inform.sort(key=lambda row: row[3])
#         print(inform)
#         con.commit()
#         await state.finish()
#     for x in inform:
#         if x[0] == int(message.text):
#             inform = x
#     print(inform)
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     query = f"SELECT Роль FROM users WHERE UserID = {message.from_user.id}"
#     tmp = cur.execute(query).fetchone()
#     buttons = ["Назад", "Вернуться к выбору проблемы", "Изменить статус проблемы", "Удалить проблему"]
#     if tmp == "Директор":
#         buttons = ["Назад", "Вернуться к выбору проблемы", "Изменить статус проблемы"]
#     keyboard.add(*buttons)
#     stat = ["Не выполнена", "В процессе", "Выполнена", "Ожидает подтверждения"][inform[3]]
#     amongus = inform[-1]
#     await message.answer(
#         f"Номер проблемы: {inform[0]}\n\nРаздел: {inform[7]}\nПроблема: {inform[1]}\n\nТип проблемы: {inform[5]}\nАвтор: {inform[4]}\nВремя создания: {inform[6]}\n\nСтатус: {stat}",
#         reply_markup=keyboard)


# @dp.message_handler(lambda message: message.text == "Изменить статус проблемы")
# async def wr(message: types.Message, state: FSMContext):
#     query = f"SELECT * FROM problems_list WHERE ID = {amongus}"
#     cur.execute(query)
#     tmp = cur.fetchall()
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     query = f"SELECT Роль FROM users WHERE UserID = {message.from_user.id}"
#     tmp = cur.execute(query).fetchone()
#     buttons = ["Выполнено", "В процессе", "Назад"]
#     if tmp[0] == "Подчиненный директора":
#         buttons = ["Выполнено (ожидает подтверждения)", "В процессе", "Назад"]
#     keyboard.add(*buttons)
#     await message.answer(f"Выберите статус:", reply_markup=keyboard)


if __name__ == "__main__":
    executor.start_polling(dp)
