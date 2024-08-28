from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from actions import Action

text = """<b>InstaIdeas</b>

InstaIdeas — это телеграм-бот, предназначенный для помощи в создании уникальных и привлекательных текстов для ваших видео в социальных сетях. 

Прежде чем приступить к созданию захватывающих историй, я хотел бы узнать больше о ваших предпочтениях, стиле и ожиданиях. Это позволит мне точно адаптировать контент под вашу индивидуальность и цели, делая каждое ваше видео не только информативным, но и невероятно интересным!
"""

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('Личная информация', callback_data=Action.EDIT_PROFILE)],
    [InlineKeyboardButton('Создать историю', callback_data=Action.CREATE_STORY)],
])


async def select_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.edit_message_text(text,
                                                  reply_markup=keyboard)
