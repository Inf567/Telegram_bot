import re

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import CallbackContext
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler
from Key import TOKEN, ADMIN_ID
from Base import write_to_db, get_user_from_db, delete_user_from_db, update_class_in_db, update_name_in_db, update_photo_in_db
import logging

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,encoding='utf-8')
logger = logging.getLogger('dispatcher_logger')
logger.setLevel(logging.INFO)

GRADES = ('8н', '8о', '8п','9н', '9о', '9п', '10н', '11н', '11о',)
WAIT_FOR_CLASS, WAIT_FOR_NAME, WAIT_FOR_PHOTO,  WAIT_FOR_NEW_CLASS, CLASS_CHOICE= range(5)
GRADES_REGEX = '^(' + '|'.join(GRADES) + ')$'
"""    Конфигурирует и запускает бот    """  # Updater - объект, который ловит обновления и Телеграм

# Получение логгера
# logger = logging.getLogger(__name__)
# file_handler = logging.FileHandler('bot.log')
# file_handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

user_states= {}
def handle_all_messages(update: Update, context: CallbackContext):
    """Обработчик всех текстовых сообщений"""
    # user_states[update.message.chat_id] = ''
    state = user_states[update.message.chat_id]
    if state=='get_name':
        get_name(update,context)
    elif state=='change_name':
        change_name(update,context)
    elif state=='change_photo':
        change_photo(update,context)
    elif state=='get_photo':
        get_photo(update,context)
    elif state=='finished':
        user =get_user_from_db(update.message.from_user.id)
        show_registration_info(update, context, user )
    print(state)
    text = update.message.text
    # Здесь можно добавить код для отладки и логирования
    print("Received message:", text)

    # Продолжайте обработку сообщения по вашим потребностям

4

def start_registration(update: Update, context: CallbackContext):
    """Начинает процесс регистрации"""
    user_states[update.message.chat_id] = 'start_registration'
    user_id = update.message.from_user.id
    user=  get_user_from_db(user_id)
    if user:
        return show_registration_info(update,context, user,False)
    else:
        return ask_for_class(update, context)

    # ask_for_class(update, context)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    import re
    if re.match(GRADES_REGEX,  query.data ):
        context.user_data["change_class"] = True
        logger.info("We logged class in our button method")
        update_class(update,context)
        return ConversationHandler.END
    if query.data == "change_name":
        context.user_data["change_name"] = True
        user_states[update.callback_query.message.chat_id] = 'change_name'
        return ask_for_name(update,context, True)
    elif query.data == "change_class":
        user_states[update.callback_query.message.chat_id] = 'change_class'
        context.user_data["change_class"] = True
        return ask_for_class(update, context)
    elif query.data == "change_photo":
        user_states[update.callback_query.message.chat_id] = 'change_photo'
        context.user_data["change_photo"] = True
        return ask_for_photo(update, context,True)
    elif query.data == "delete_register":
        delete_user_from_db(query.from_user.id)
        query.edit_message_text(text="Регистрация удалена.")
        return ConversationHandler.END

def update_class(update, context):
    user_id = update.effective_user.id
    # print('we are in update class')
    if context.user_data.get('change_class'):
        new_class = update.callback_query.data
        context.user_data['class'] = new_class
        print(f'we are changing class to {new_class}')
        update_class_in_db(user_id, new_class)
        update.callback_query.message.reply_text(f"Я запомнил твой класс  {new_class}!")
        user = get_user_from_db(user_id)
        if user_states[update.callback_query.message.chat_id]=='start_registration':
            user_states[update.callback_query.message.chat_id]='get_name'
            return ask_for_name(update,context)
        # show_registration_info(update, context, user)
        # return ask_for_name(update, context)  # Задать вопрос о имени пользователя
    # else:
    #     pass

def delete_registretion(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    delete_user_from_db(user_id)
    update.effective_message.reply_text('Твоя регистрация удалена')


def do_help(update: Update, context: CallbackContext):
    if context.user_data.get('registering') or context.user_data.get('get_class'):
        return
    text = [
        'тестируем следующие функции',
        '/ask_for_class',
        '/ask_for_name',
        '/ask_for_photo',
        '/register_player',
    ]
    text = '\n'.join(text)
    update.message.reply_text(text)
    return ConversationHandler.END

def do_start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = get_user_from_db(user_id)
    if user:
        show_registration_info(update, context, user, False)  # Функция вывода информации о регистрации
    else:
        update.message.reply_text("Введи команду /register чтобы продолжить")
        # return ask_for_class(update, context)

def show_registration_info(update: Update, context: CallbackContext, user: dict, is_first_time= True):
    if is_first_time:
        lines = [
            f'Ты зарегистрирован! :',
            f'Тебя зовут  {user["name"]}',
            f'Ты учишься в {user["class"]} классе',
        ]
    else:
        lines = [
            f'Ты уже зарегистрирован! :',
            f'Тебя зовут  {user["name"]}',
            f'Ты учишься в {user["class"]} классе',
        ]

    text = '\n'.join(lines)

    keyboard = [[InlineKeyboardButton('Изменить имя', callback_data='change_name'),
                 InlineKeyboardButton('Изменить класс', callback_data='change_class')],
                [
                    InlineKeyboardButton('Изменить фото', callback_data='change_photo'),
                    InlineKeyboardButton('Удалить регистрацию', callback_data='delete_register')]]

    keyboard_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=keyboard_markup)
def ask_for_class(update: Update, context: CallbackContext):
    """Запрашивает у пользователя выбор класса"""
    keyboard = [
        [
            InlineKeyboardButton("8н", callback_data='8н'),
            InlineKeyboardButton("8о", callback_data='8о'),
            InlineKeyboardButton("8п", callback_data='8п')
        ],
        [
            InlineKeyboardButton("9н", callback_data='9н'),
            InlineKeyboardButton("9о", callback_data='9о'),
            InlineKeyboardButton("9п", callback_data='9п')
        ],
        [
            InlineKeyboardButton("10н", callback_data='10н'),
            InlineKeyboardButton("11н", callback_data='11н'),
            InlineKeyboardButton("11о", callback_data='11о')
        ]
    ]
    keyboard_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        grade = update.callback_query.data
        update.callback_query.answer()
        update.callback_query.message.reply_text(f'Выбери свой классс:',reply_markup=keyboard_markup)
    else:
        grade = update.message.text
        update.message.reply_text(f'Я Выбери свой классс:',reply_markup=keyboard_markup)
    return WAIT_FOR_CLASS



def get_class(update: Update, context: CallbackContext):
        if update.callback_query:
            grade = update.callback_query.data
            update.callback_query.answer()
            update.callback_query.message.reply_text(f'Я запомнил твой класс: {grade}')
        else:
            grade = update.message.text
            update.message.reply_text(f'Я запомнил твой класс: {grade}')

        context.user_data['class'] = grade
        user_id = update.effective_user.id
        update_class_in_db(user_id, grade)

        user = get_user_from_db(user_id)
        if user:
            return show_registration_info(update, context, user)  # Показать информацию о регистрации
        else:
            return ask_for_name(update, context)  # Задать вопрос о имени пользователя



def ask_for_name(update: Update, context: CallbackContext, for_update = False):

    text = [
        'Введи своё имя',
    ]
    text = '\n'.join(text)

    if update.callback_query:
        chat_id = update.callback_query.message.chat_id
        update.callback_query.message.reply_text(text)
        update.callback_query.answer()

    else:
        chat_id = update.message.chat_id
        update.message.reply_text(text)

    if for_update:
        user_states[chat_id] = 'change_name'
    else:
        user_states[chat_id] = 'get_name'

def change_photo(update: Update, context: CallbackContext):
    if update.callback_query:
        new_photo = update.callback_query.message.text
        user_states[update.callback_query.message.chat_id] = 'changed_photo'
        update.callback_query.answer()
        update.callback_query.message.reply_text(f"Я запомнил твое фото {new_photo}")
        update_name_in_db(update.callback_query.message.from_user.id, name)
    else:
        user_states[update.message.chat_id] = 'changed_photo'
        new_photo =update.message.text
        update.message.reply_text(f"Я запомнил твое фото {new_photo}")
        update_photo_in_db(update.message.from_user.id, new_photo)
    return ConversationHandler.END

def change_name(update: Update, context: CallbackContext):
    if update.callback_query:
        name = update.callback_query.message.text
        user_states[update.callback_query.message.chat_id] = 'change_name'
        update.callback_query.answer()
        update_name_in_db(update.callback_query.message.from_user.id, name)
    else:
        user_states[update.message.chat_id] = 'change_name'
        name =update.message.text
        update_name_in_db(update.message.from_user.id, name)
    return get_name(update,context,True)





def get_name(update: Update, context: CallbackContext, for_update=False):
    # if for_update:
    if update.callback_query:
            name = update.callback_query.message.text
            chat_id = update.callback_query.message.chat_id
            context.user_data["name"] = name
            # user_states[chat_id] = 'get_name'
            update.callback_query.answer()
            update.callback_query.message.reply_text(f"Я запомнил как тебя зовут: {name}")
            update_name_in_db(update.callback_query.message.from_user.id, name)
    else:
            chat_id = update.message.chat_id
            # user_states[chat_id] = 'get_name'
            name = update.message.text
            context.user_data["name"] = name
            update_name_in_db(update.message.from_user.id, name)
            update.message.reply_text(f"Я запомнил как тебя зовут: {name}")
    # name = update.message.text

    print(f"state in ask_name {user_states[chat_id]}")
    if for_update:
        print('we have passed if for_update: condition')

        return ConversationHandler.END
        # return ask_for_photo(update, context)
    elif for_update and user_states[chat_id]=='get_name' or user_states[chat_id]=='change_name':
        print('we have passed the second condition')
        return ConversationHandler.END
    elif not for_update and user_states[chat_id]!='get_name':
        print(f"we are in pre else user_state is {user_states}")
        return ask_for_photo(update,context)
    elif not for_update and user_states[chat_id]=='get_name':
        print('we are in elif : ')
        return ask_for_photo(update,context)
    else:
        print(f'we are in else condition and user_state is {user_states}')
        return ask_for_photo(update,context)


def ask_for_photo(update: Update, context: CallbackContext, for_update =False):

    text = 'Прикрепи своё фото'

    if update.callback_query:
        chat_id = update.callback_query.message.chat_id
        user_states[chat_id] = 'get_photo'
        update.callback_query.message.reply_text(text)
        update.callback_query.answer()
    else:
        chat_id = update.message.chat_id
        user_states[chat_id] = 'get_photo'
        update.message.reply_text(text)
    if for_update:
        user_states[chat_id] = 'change_photo'
    else:
        user_states[chat_id] = 'get_photo'
    return WAIT_FOR_PHOTO


def get_photo(update: Update, context: CallbackContext, for_update = False):
    photo = update.message.text
    print(photo)
    context.user_data['photo'] = photo
    print(context.user_data)
    text = f'Я запомнил твоё фото: {photo}'
    update.message.reply_text(text)
    if not for_update:
        return register_player(update, context)
    else:
        return ConversationHandler.END
def register_player(update: Update, context: CallbackContext):
    grade = context.user_data["class"]
    name = context.user_data["name"]
    photo = update.message.text
    user_id = update.message.from_user.id
    print(grade, name, photo, user_id)
    user_states[update.message.chat_id]='finished_registration'
    write_to_db(user_id, grade, name, photo)

    user = get_user_from_db(user_id)

    # show the menu
    return show_registration_info(update, context, user)


if __name__ == '__main__':
    updater = Updater(token=TOKEN)
    # Диспетчер будет распределять события по обработчикам
    dispatcher = updater.dispatcher
    logger = dispatcher.logger
    dispatcher.add_handler(
        ConversationHandler(
            per_message=True,
            entry_points=[CommandHandler('register', ask_for_class)],

            states={},
            #     WAIT_FOR_CLASS: [MessageHandler(Filters.text, get_class)],
            #     WAIT_FOR_NAME: [MessageHandler(Filters.text, get_name)],
            #     WAIT_FOR_PHOTO: [MessageHandler(Filters.text, get_photo)],
            #
            #     # WAIT_FOR_NEW_CLASS: [CallbackQueryHandler(update_class, pattern=GRADES_REGEX)],
            #
            # },  # состояние
            fallbacks=[MessageHandler(Filters.text, do_help)]  # отлов ошибок

        )
    )
    dispatcher.add_handler(CommandHandler('start', do_start))
    dispatcher.add_handler(CommandHandler('register', start_registration, pass_args=True))

    dispatcher.add_handler(CallbackQueryHandler(button))
    # Добавляем обработчик событий из Телеграма

    dispatcher.add_handler(MessageHandler(Filters.text, handle_all_messages))

# Начать бесконечный опрос телеграма на предмет обновлений
    updater.start_polling()
    print(updater.bot.getMe())
    print('Бот запущен')
    updater.idle()

