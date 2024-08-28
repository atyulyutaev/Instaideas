from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from actions import ProfileAction, Action
from adapters.db import Author, speech_styles

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Указать пол", callback_data=ProfileAction.EDIT_GENDER)],
    [InlineKeyboardButton("Указать возраст", callback_data=ProfileAction.EDIT_AGE)],
    [InlineKeyboardButton("Указать стили речи", callback_data=ProfileAction.EDIT_SPEECH_STYLE)],
    [InlineKeyboardButton("Сохранить изменения 🟢", callback_data=ProfileAction.SAVE)],
])


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

    return text


async def get_speech_styles_text(selected_speech_styles: list[int]) -> str:
    preferred_style_text = "\n".join([
        f"{key}. {value['name']}{' (Выбран)' if key in selected_speech_styles else ''}: {value['link']}"
        for key, value
        in speech_styles.items()
    ])

    first_preferred_style_text = """<b>Редактирование личной информации</b>

Выберите какой стиль повествования в данных Reels вам понравился больше всего:

""" + preferred_style_text

    return first_preferred_style_text


async def edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['action'] = Action.EDIT_PROFILE
    author = context.user_data['author']

    if update.callback_query:
        await update.callback_query.edit_message_text(
            await get_text(author),
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            await get_text(author),
            reply_markup=keyboard
        )


async def edit_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['action'] = ProfileAction.EDIT_GENDER

    reply_markup = ReplyKeyboardMarkup([
        ["М", "Ж"],
    ], one_time_keyboard=True, input_field_placeholder="Мужчина или Женщина?")

    await update.callback_query.answer()
    await update.callback_query.message.reply_text("<b>Редактирование личной информации</b>\n\nКакой у вас пол?", reply_markup=reply_markup)


async def edit_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['action'] = ProfileAction.EDIT_AGE
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("<b>Редактирование личной информации</b>\n\nКакой у вас возраст?")


async def edit_speech_styles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['action'] = ProfileAction.EDIT_SPEECH_STYLE

    keyboard = [
        [
            InlineKeyboardButton(
                value['name'] + " ✅" if key in context.user_data['author'].preferred_speech_styles else
                value['name'], callback_data=key)
        ] for key, value in speech_styles.items()
    ]
    keyboard.append([InlineKeyboardButton("Завершить 🟢", callback_data=Action.EDIT_PROFILE)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = await get_speech_styles_text(context.user_data['author'].preferred_speech_styles)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup
    )


async def save_author_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text()

    del context.user_data['action']
