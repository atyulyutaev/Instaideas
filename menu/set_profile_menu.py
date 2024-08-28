from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from actions import ProfileAction
from adapters.db import speech_styles, Author, author_repository

gender_keyboard = ReplyKeyboardMarkup([
    ["М", "Ж"],
], one_time_keyboard=True, input_field_placeholder="Мужчина или Женщина?")


async def get_text(author: Author):
    if not author.has_info():
        return "<b>Личная информация</b>\n\nВ этом месте будет представлена ваша информация."

    text = "<b>Личная информация</b>\n\n"
    if author.gender:
        text += f"Пол: {author.gender}\n"
    else:
        text += "Пол: не указано\n"

    if author.age:
        text += f"Возраст: {author.age}\n"
    else:
        text += "Возраст: не указано\n"

    if author.preferred_speech_styles:
        text += f"Стили речи: {', '.join([speech_styles[i]['name'] for i in author.preferred_speech_styles])}\n"
    else:
        text += "Стили речи: не указано\n"

    text += "\nТеперь можете создать историю используя команду /start"
    return text


async def get_speech_styles_text(selected_speech_styles: list[int]) -> str:
    preferred_style_text = "\n".join([
        f"{key}. {value['name']}{' (Выбран)' if key in selected_speech_styles else ''}: {value['link']}"
        for key, value
        in speech_styles.items()
    ])

    first_preferred_style_text = """<b>Заполнение личной информации</b>

Выберите какой стиль повествования в данных Reels вам понравился больше всего:

""" + preferred_style_text

    return first_preferred_style_text


async def set_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['action'] = ProfileAction.SET_GENDER

    await update.message.reply_text(
        "<b>Заполнение личной информации</b>\n\nКакой у вас пол?",
        reply_markup=gender_keyboard
    )


async def set_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['action'] = ProfileAction.SET_AGE

    await update.message.reply_text(
        "<b>Заполнение личной информации</b>\n\nКакой у вас возраст?",
        reply_markup=ReplyKeyboardRemove()
    )


async def set_speech_styles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['action'] = ProfileAction.SET_SPEECH_STYLE

    keyboard = [
        [
            InlineKeyboardButton(
                value['name'] + " ✔️" if key in context.user_data['author'].preferred_speech_styles else
                value['name'], callback_data=key)
        ] for key, value in speech_styles.items()
    ]
    if context.user_data['author'].preferred_speech_styles:
        keyboard.append([InlineKeyboardButton("Завершить 🟢", callback_data=ProfileAction.SAVE)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = await get_speech_styles_text(context.user_data['author'].preferred_speech_styles)

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )


async def set_speech_styles_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['action'] = ProfileAction.SET_SPEECH_STYLE

    keyboard = [
        [
            InlineKeyboardButton(
                value['name'] + " ✅" if key in context.user_data['author'].preferred_speech_styles else
                value['name'], callback_data=key)
        ] for key, value in speech_styles.items()
    ]
    if context.user_data['author'].preferred_speech_styles:
        keyboard.append([InlineKeyboardButton("Завершить 🟢", callback_data=ProfileAction.SAVE)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = await get_speech_styles_text(context.user_data['author'].preferred_speech_styles)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup
    )


async def save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await author_repository.connect()
    try:
        await author_repository.update_or_create(context.user_data['author'])
        text = await get_text(context.user_data['author'])

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text
        )
    finally:
        await author_repository.close()
        del context.user_data['action']
