import telebot
from telebot import types
from config import TOKEN
from user import User
from collections import defaultdict

bot = telebot.TeleBot(TOKEN)
URLS = ["https://cs14.pikabu.ru/post_img/2022/01/23/0/og_og_1642887519238536781.jpg"]

bot_messages = defaultdict(list)


def cleanup_previous_messages(chat_id: str):
    """Удаляет предыдущие сообщения бота в указанном чате"""
    if chat_id in bot_messages:
        for msg_id in bot_messages[chat_id]:
            bot.delete_message(chat_id, msg_id)
        bot_messages[chat_id] = []


def send_message_with_cleanup(chat_id: int, text: str, reply_markup: None):
    """Отправляет сообщение с автоматической очисткой предыдущих"""
    cleanup_previous_messages(chat_id)
    sent_message = bot.send_message(chat_id, text, reply_markup=reply_markup)
    bot_messages[chat_id].append(sent_message.message_id)
    return sent_message


@bot.message_handler(commands=["start"])
def handle_send_welcome(message):
    user_id = message.from_user.id
    user_data = User.get_user(user_id)

    if user_data:
        _, role = (
            user_data  # как я понял, нижнее подчёркивание - игнорирование переменной в списке
        )
        handle_show_main_menu(message, role)
    else:
        show_role_selection(message.chat.id)


def show_role_selection(chat_id):
    """Показывает клавиатуру выбора роли"""
    markup = types.InlineKeyboardMarkup()
    btn_teacher = types.InlineKeyboardButton(
        "Я Преподаватель", callback_data="role_teacher"
    )
    btn_tutor = types.InlineKeyboardButton("Я Куратор", callback_data="role_tutor")
    markup.add(btn_teacher, btn_tutor)

    send_message_with_cleanup(
        chat_id,
        "Добро пожаловать в систему онбординга!\n\nПожалуйста, выберите вашу роль:",
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("role_"))
def process_role_selection(call):
    user_id = call.from_user.id
    existing_user = User.get_user(user_id)

    if existing_user:
        bot.answer_callback_query(
            call.id, f"Ваша роль уже установлена: {existing_user[1]}"
        )
        handle_show_main_menu(call.message, existing_user[1])
        return

    role = call.data.split("_")[1]

    if User.add_user(user_id, role):
        bot.answer_callback_query(call.id, f"Роль '{role}' сохранена!")
    else:
        bot.answer_callback_query(call.id, "Ошибка при сохранении роли!")
        return

    handle_show_main_menu(call.message, role)


def handle_show_main_menu(message: str, role: str):
    markup = types.InlineKeyboardMarkup()

    if role == "teacher":
        buttons = [
            types.InlineKeyboardButton("О компании", url=URLS[0]),
            types.InlineKeyboardButton("Структура", url=URLS[0]),
            types.InlineKeyboardButton("Карта курсов", callback_data="courses_map"),
            types.InlineKeyboardButton("Партнеры", callback_data="partners_teacher"),
            types.InlineKeyboardButton("Мотивация", callback_data="motivation"),
            types.InlineKeyboardButton("Метод работы", url=URLS[0]),
        ]
    else:
        buttons = [
            types.InlineKeyboardButton("О компании", url=URLS[0]),
            types.InlineKeyboardButton(
                " Инструкции и регламенты", callback_data="instructions"
            ),
            types.InlineKeyboardButton("Карта курсов", callback_data="courses_map"),
            types.InlineKeyboardButton("Структура", url=URLS[0]),
            types.InlineKeyboardButton("Партнеры", callback_data="partners_tutor"),
            types.InlineKeyboardButton("Мотивация", callback_data="motivation"),
            types.InlineKeyboardButton("AXO", callback_data="AXO"),
        ]

    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.add(buttons[i], buttons[i + 1])
        else:
            markup.add(buttons[i])

    send_message_with_cleanup(
        message.chat.id, "Главное меню. Выберите раздел:", reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    user = User.get_user(user_id)

    if not user:
        handle_send_welcome(call.message)
        return

    data = call.data

    if data in URLS:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(" Назад", callback_data="main_menu"))
        send_message_with_cleanup(
            call.message.chat.id,
            f"Перейдите по ссылке: {URLS[data]}",
            reply_markup=markup,
        )
        return

    if data == "main_menu":
        handle_show_main_menu(call.message, user[1])
    elif data == "courses_map":
        handle_show_courses_map(call.message)
    elif data == "partners_teacher":
        handle_show_partners_teacher(call.message)
    elif data == "partners_tutor":
        handle_show_partners_tutor(call.message)
    elif data == "growth_teacher":
        handle_show_growth_teacher(call.message)
    elif data == "growth_tutor":
        handle_show_growth_tutor(call.message)
    elif data == "proschool_teacher":
        handle_show_proschool_teacher(call.message)
    elif data == "proschool_tutor":
        handle_show_proschool_tutor(call.message)
    elif data == "school10_teacher":
        handle_show_school10_teacher(call.message)
    elif data == "school10_tutor":
        handle_show_school10_tutor(call.message)
    elif data == "motivation":
        handle_show_motivation(call.message)
    elif data == "instructions":
        handle_show_instructions(call.message)
    elif data == "CMP":
        handle_show_CMP(call.message)
    elif data == "AXO":
        handle_show_AXO(call.message)


"""Общие клавиатуры"""


@bot.message_handler(content_types=["text"])
def handle_show_courses_map(message):
    markup = types.InlineKeyboardMarkup()
    main = types.InlineKeyboardButton("Основные курсы", url=URLS[0])
    summer = types.InlineKeyboardButton("Летняя школы", url=URLS[0])
    short = types.InlineKeyboardButton("Краткосрочные группы", url=URLS[0])
    markup.add(
        main,
        summer,
        short,
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    )

    send_message_with_cleanup(message.chat.id, "Карта курсов", reply_markup=markup)


def handle_show_motivation(message):
    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton("Обратная связь", url=URLS[0]),
        types.InlineKeyboardButton("Мовави бустинструкция/пароли", url=URLS[0]),
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    ]
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.add(buttons[i], buttons[i + 1])
        else:
            markup.add(buttons[i])

    send_message_with_cleanup(message.chat.id, "Мотивация", reply_markup=markup)


"""Клавиатуры преподавателя"""


def handle_show_partners_teacher(message):
    markup = types.InlineKeyboardMarkup()
    growth = types.InlineKeyboardButton("Рост", callback_data="growth_teacher")
    proschool = types.InlineKeyboardButton("Проскул", callback_data="proschool_teacher")
    school10 = types.InlineKeyboardButton(
        "10я гимназия", callback_data="school10_teacher"
    )
    markup.add(
        growth,
        proschool,
        school10,
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    )

    send_message_with_cleanup(message.chat.id, "Партнёры", reply_markup=markup)


def handle_show_growth_teacher(message):
    markup = types.InlineKeyboardMarkup()
    olimp = types.InlineKeyboardButton("Олимпиады", url=URLS[0])
    timetable = types.InlineKeyboardButton("Расписание", url=URLS[0])
    kurs = types.InlineKeyboardButton("Курсы", url=URLS[0])
    markup.add(
        olimp,
        timetable,
        kurs,
        types.InlineKeyboardButton("Назад", callback_data="partners_teacher"),
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    )
    send_message_with_cleanup(message.chat.id, "Рост", reply_markup=markup)


def handle_show_proschool_teacher(message):
    markup = types.InlineKeyboardMarkup()
    timetable = types.InlineKeyboardButton("Расписание", url=URLS[0])
    kurs = types.InlineKeyboardButton("Курсы", url=URLS[0])
    markup.add(
        timetable,
        kurs,
        types.InlineKeyboardButton("Назад", callback_data="partners_teacher"),
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    )
    send_message_with_cleanup(message.chat.id, "Проскул", reply_markup=markup)


def handle_show_school10_teacher(message):
    markup = types.InlineKeyboardMarkup()
    timetable = types.InlineKeyboardButton("Расписание", url=URLS[0])
    markup.add(
        timetable,
        types.InlineKeyboardButton("Назад", callback_data="partners_teacher"),
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    )
    send_message_with_cleanup(message.chat.id, "10я гимназия", reply_markup=markup)


"""Клавиатуры куратора"""


def handle_show_instructions(message):
    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton("Документооборот", url=URLS[0]),
        types.InlineKeyboardButton("Касса", url=URLS[0]),
        types.InlineKeyboardButton("Пожарная эвакуация", url=URLS[0]),
        types.InlineKeyboardButton("Работа с котрагентами", url=URLS[0]),
        types.InlineKeyboardButton("Первая помощь", url=URLS[0]),
        types.InlineKeyboardButton("CMP", callback_data="CMP"),
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    ]
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.add(buttons[i], buttons[i + 1])
        else:
            markup.add(buttons[i])
    send_message_with_cleanup(
        message.chat.id, "Инструкции и регламенты", reply_markup=markup
    )


def handle_show_CMP(message):
    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton("Как создать договор", url=URLS[0]),
        types.InlineKeyboardButton("Как провести оплату", url=URLS[0]),
        types.InlineKeyboardButton("Назад", callback_data="instructions"),
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    ]
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.add(buttons[i], buttons[i + 1])
        else:
            markup.add(buttons[i])
    send_message_with_cleanup(message.chat.id, "CMP", reply_markup=markup)


def handle_show_partners_tutor(message):
    markup = types.InlineKeyboardMarkup()
    growth = types.InlineKeyboardButton("Рост", callback_data="growth_tutor")
    proschool = types.InlineKeyboardButton("Проскул", callback_data="proschool_tutor")
    school10 = types.InlineKeyboardButton(
        "10я гимназия", callback_data="school10_tutor"
    )
    markup.add(
        growth,
        proschool,
        school10,
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    )

    send_message_with_cleanup(message.chat.id, "Партнёры", reply_markup=markup)


def handle_show_growth_tutor(message):
    markup = types.InlineKeyboardMarkup()
    olimp = types.InlineKeyboardButton("Олимпиады", url=URLS[0])
    kurs = types.InlineKeyboardButton("Курсы", url=URLS[0])
    markup.add(
        olimp,
        kurs,
        types.InlineKeyboardButton("Назад", callback_data="partners_tutor"),
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    )
    send_message_with_cleanup(message.chat.id, "Рост", reply_markup=markup)


def handle_show_proschool_tutor(message):
    markup = types.InlineKeyboardMarkup()
    kurs = types.InlineKeyboardButton("Курсы", url=URLS[0])
    markup.add(
        kurs,
        types.InlineKeyboardButton("Назад", callback_data="partners_tutor"),
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    )
    send_message_with_cleanup(message.chat.id, "Проскул", reply_markup=markup)


def handle_show_school10_tutor(message):
    markup = types.InlineKeyboardMarkup()
    kurs = types.InlineKeyboardButton("Курсы", url=URLS[0])
    markup.add(
        kurs,
        types.InlineKeyboardButton("Назад", callback_data="partners_tutor"),
        types.InlineKeyboardButton("На главную", callback_data="main_menu"),
    )
    send_message_with_cleanup(message.chat.id, "10я гимназия", reply_markup=markup)


def handle_show_AXO(message):
    markup = types.InlineKeyboardMarkup()
    AXO = types.InlineKeyboardButton("Полезные телефоны", url=URLS[0])
    markup.add(AXO, types.InlineKeyboardButton("На главную", callback_data="main_menu"))
    send_message_with_cleanup(message.chat.id, "AXO", reply_markup=markup)


bot.polling()
