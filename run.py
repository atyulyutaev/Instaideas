import telegram
import config
from telegram import Update
from telegram.ext import Defaults, Application, CommandHandler, CallbackQueryHandler, ContextTypes, filters, \
    MessageHandler
from actions import ProfileAction, Action, StoryAction
from adapters.db import author_repository, Author
from menu import select_action_menu
from menu.create_story_menu import create_story, set_story_type, set_story_line, generate, edit_story_line, \
    cancel_story_generation, end_story_generation, set_story_line_part, show_story_line, show_edit_story_line
from menu.edit_profile_menu import edit_profile, edit_gender, \
    edit_age, edit_speech_styles
from menu.set_profile_menu import set_gender, set_age, set_speech_styles, set_speech_styles_reply, \
    save

defaults = Defaults(
    parse_mode=telegram.constants.ParseMode.HTML
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await author_repository.connect()
    try:
        author = await author_repository.get_by_id(update.message.from_user.id)

        if author:
            context.user_data['author'] = author
            await create_story(update, context)
        else:
            context.user_data['author'] = Author(update.message.from_user.id)
            await update.message.reply_text(select_action_menu.text)
            await set_gender(update, context)
    finally:
        await author_repository.close()


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'action' not in context.user_data:
        await update.message.reply_text("Для генерации истории можете воспользоваться командой /start")
        return

    author = context.user_data['author']
    action = context.user_data['action']
    message = update.message.text

    if action == ProfileAction.EDIT_GENDER:
        error_message = author.set_gender(message)
        if error_message:
            await update.message.reply_text(error_message)
            return

        await edit_profile(update, context)

    elif action == ProfileAction.SET_GENDER:
        error_message = author.set_gender(message)
        if error_message:
            await update.message.reply_text(error_message)
            return

        await set_age(update, context)

    elif action == ProfileAction.EDIT_AGE:
        error_message = author.set_age(message)
        if error_message:
            await update.message.reply_text(error_message)
            return

        await edit_profile(update, context)

    elif action == ProfileAction.SET_AGE:
        error_message = author.set_age(message)
        if error_message:
            await update.message.reply_text(error_message)
            return

        await set_speech_styles(update, context)

    elif action == Action.CREATE_STORY:
        await set_story_type(update, context)
    elif action == StoryAction.SET_STORY_LINE:
        await set_story_line_part(update, context)
    elif action == StoryAction.EDIT_STORY_LINE:
        await set_story_line(update, context)

    elif action == StoryAction.SHOW_STORY_LINE or action == StoryAction.REGEN:
        await update.message.reply_text(
            'Пожалуйста, выберите одно из действий используя кнопки или начните создание новой истории с командой /start.')
        return
    else:
        await update.message.reply_text("Для генерации новой истории можете воспользоваться командой /start")
        return


async def query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    author = context.user_data['author']
    action = context.user_data['action']
    data = update.callback_query.data

    if not action:
        return

    elif action == ProfileAction.EDIT_SPEECH_STYLE:
        author.toggle_speech_style(int(data))
        await edit_speech_styles(update, context)

    elif action == ProfileAction.SET_SPEECH_STYLE:
        author.toggle_speech_style(int(data))
        await set_speech_styles_reply(update, context)


def main() -> None:
    application = Application.builder().defaults(defaults).token(config.BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('cancel', cancel_story_generation))
    application.add_handler(CommandHandler('edit_profile', edit_profile))

    application.add_handler(CallbackQueryHandler(edit_profile, pattern="^" + Action.EDIT_PROFILE + "$"))
    application.add_handler(CallbackQueryHandler(edit_gender, pattern="^" + ProfileAction.EDIT_GENDER + "$"))
    application.add_handler(CallbackQueryHandler(edit_age, pattern="^" + ProfileAction.EDIT_AGE + "$"))
    application.add_handler(
        CallbackQueryHandler(edit_speech_styles, pattern="^" + ProfileAction.EDIT_SPEECH_STYLE + "$"))
    application.add_handler(
        CallbackQueryHandler(save, pattern="^" + ProfileAction.SAVE + "$"))

    application.add_handler(
        CallbackQueryHandler(generate, pattern="^" + StoryAction.REGEN + "$"))
    application.add_handler(
        CallbackQueryHandler(edit_story_line, pattern="^" + StoryAction.EDIT_STORY_LINE + "$"))
    application.add_handler(
        CallbackQueryHandler(show_edit_story_line, pattern="^" + StoryAction.SHOW_EDIT_STORY_LINE + "$"))
    application.add_handler(
        CallbackQueryHandler(end_story_generation, pattern="^" + StoryAction.END + "$"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(CallbackQueryHandler(query_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
