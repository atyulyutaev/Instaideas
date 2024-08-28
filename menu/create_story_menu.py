import re

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from actions import Action, StoryAction
from adapters.db import speech_styles
from adapters.story_generator import Story, StoryPersonal, StoryExpert, story_generator

personal_story_line = {
    1: "🎯Вопрос 1/7: В чем суть твоей истории? Опиши самую главную суть, одним предложением.\nНапример: блогер кинул меня на бабки.",
    2: "⏳Вопрос 2/7: Как давно это произошло или как давно ты об этом думал, мечтал?\nНапример: еще с самого детства я хотел.., пару недель назад произошло.., буквально на днях я...",
    3: "🔍Вопрос 3/7: Опиши развитие событий которые подводят к основной истории, что сподвигло тебя к истории, почему история произошла.\nНапример: я долго мучался или долго к этому шел, но в один из дней, и в один из дней я понял...",
    4: "📖Вопрос 4/7: Расскажи основную историю, основную часть и подробно, старайся описывать все эмоции и детали которые были в твоей истории. Что было, как, что произошло.\nНапример: я пошел в это помещение, посмотрел что там есть, понял, что оно мне не подходит, там нет: (перечисление), и я понял, что меня просто развели на бабки.",
    5: "🔄Вопрос 5/7: Расскажи про события, которые были после истории, постарайся подробно описать\nНапример: я выхожу из помещения, звоню другу, рассказываю про то что меня обманули, меня поддержали и я поехал домой.",
    6: "🔚Вопрос 6/7: Опиши, что произошло по итогу, тезисно подытожить историю.\nНапример: по итогу: я понял, что блогер меня кинул, помещение я не наше, но друзья меня поддержали.",
    7: "💡Вопрос 7/7: Напиши вывод какой ты вынес или какой бы хотел сказать людям, чтобы они сочли твою историю полезной\nНапример: Вывод - как говорится скупой платит дважды, не стоит экономить на себе и доверять блогерам.",
}
personal_story_line_text = """<b>Создание личной истории</b>

Для того чтобы создать увлекательную и целостную сюжетную линию для твоего видео, тебе необходимо ответить на 7 вопросов. Каждый вопрос поможет тебе детально раскрыть все аспекты твоей истории, от главной идеи до заключительных выводов. Не пропускай ни один вопрос, чтобы твоя история была полной и интересной для зрителей.
""" + f"\n\n{personal_story_line[1]}"

expert_story_line = {
    1: "🎯Вопрос 1/5: Напиши о чем твоя тема, самая главная мысль/тема, что ты хочешь донести.\nНапример: я расскажу как похудеть за месяц.  ",
    2: "👀Вопрос 2/5: Напиши почему человеку стоит смотреть этот ролик.\nНапример: я даю пользу или лайфхак, расскажу секрет.",
    3: "🌟Вопрос 3/5: Расскажи основную информацию, пользу, лайфхак, секрет, историю.\nНапример: всего одна чашка чая в день, поможет вам худеть на 2кг в неделю",
    4: "⏳Вопрос 4/5: Расскажи про промежкточный результат, что получил или что получит человек.\nНапрмер: применив этот секрет, всего за 2 дня я похудел. ",
    5: "📢Вопрос 5/5: Расскажи про пользу или напиши свой призыв к действию, с которым людь будут взаимодействовать.\nНапример: подпишись, чтобы не пропустить... поставь + в коментария если солгласен",
}
expert_story_line_text = """<b>Cоздание эксперной истории</b>

Для того чтобы разработать информативную и убедительную сюжетную линию для твоего экспертного видео, ответь, пожалуйста, на 5 ключевых вопросов. Эти вопросы помогут тебе структурированно и ясно представить основные идеи, лайфхаки и пользу, которую ты хочешь донести до зрителей. Ответы на эти вопросы сформируют основу твоего видео, делая его не только информативным, но и привлекательным для аудитории.
""" + f"\n\n{expert_story_line[1]}"


# keyboard = InlineKeyboardMarkup([
#     [InlineKeyboardButton("Личная информация", callback_data=Action.EDIT_PROFILE)],
#     [InlineKeyboardButton("Вернуться к выбору действия", callback_data=Action.SELECT_ACTION)],
# ])


async def get_story_dictionary_from_text(story_text: str, story_line: dict) -> dict:
    # Split the text by number and dot
    split_text = re.split(r'(\d+\.)', story_text)

    # Remove empty strings and dots
    split_text = [item.strip() for item in split_text if item.strip() and item.strip() != '.']

    # Create dictionary
    d = {}
    for i in range(0, len(split_text), 2):
        key = int(split_text[i][:-1])  # remove the dot from the key
        value = split_text[i + 1]

        if key not in story_line:
            continue

        d[key] = value

    return d


async def create_story(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await dispatch_story_data(context)
    context.user_data['action'] = Action.CREATE_STORY

    reply_markup = ReplyKeyboardMarkup([
        ["Личная"],
        ["Экспертная"],
    ], one_time_keyboard=True, input_field_placeholder="Личная или Экспертная?")

    await update.message.reply_text("<b>Создание новой истории</b>\n\nВыберите тип истории?", reply_markup=reply_markup)


async def set_story_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text

    if message == 'Личная':
        text = personal_story_line_text
    elif message == 'Экспертная':
        text = expert_story_line_text
    else:
        reply_markup = ReplyKeyboardMarkup([
            ["Личная"],
            ["Экспертная"],
        ], one_time_keyboard=True, input_field_placeholder="Личная или Экспертная?")

        await update.message.reply_text(
            'Тип истории может быть либо Личная, либо Экспертная',
            reply_markup=reply_markup
        )
        return

    context.user_data['story_type'] = message
    context.user_data['action'] = StoryAction.SET_STORY_LINE
    context.user_data['story_part_index'] = 1
    context.user_data['story_line'] = {}

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardRemove(),
    )


async def set_story_line(update: Update, context: ContextTypes.DEFAULT_TYPE):
    story_text = update.message.text
    speech_style_names = [speech_styles[speech_style_index]['name'].lower() for speech_style_index in
                          context.user_data['author'].preferred_speech_styles]

    # Create story line
    story: Story
    if context.user_data['story_type'] == Story.PERSONAL:
        story_line = personal_story_line
        story_dict = await get_story_dictionary_from_text(story_text, story_line)
        if 'story_line' in context.user_data:
            context.user_data['story_line'].update(story_dict)
        else:
            context.user_data['story_line'] = story_dict

        story = StoryPersonal(
            clickbait_event=context.user_data['story_line'].get(1),
            plot_start=context.user_data['story_line'].get(2),
            plot_development=context.user_data['story_line'].get(3),
            storytelling=context.user_data['story_line'].get(4),
            plot_continuation=context.user_data['story_line'].get(5),
            intermediate_results=context.user_data['story_line'].get(6),
            conclusion=context.user_data['story_line'].get(7),
            speech_style_names=speech_style_names
        )
    else:
        story_line = expert_story_line
        story_dict = await get_story_dictionary_from_text(story_text, story_line)
        if 'story_line' in context.user_data:
            context.user_data['story_line'].update(story_dict)
        else:
            context.user_data['story_line'] = story_dict

        story = StoryExpert(
            hook=context.user_data['story_line'].get(1),
            reengagement=context.user_data['story_line'].get(2),
            plot_establishment=context.user_data['story_line'].get(3),
            climax=context.user_data['story_line'].get(4),
            resolution=context.user_data['story_line'].get(5),
            speech_style_names=speech_style_names
        )

    # Check if story line is valid
    absent_story_line_text = []
    for key in story_line.keys():
        if key not in context.user_data['story_line']:
            absent_story_line_text.append(f"{key}. {story_line[key]}")

    if absent_story_line_text:
        absent_story_line_text = "Пожалуйста заполните следующие пункты:\n\n" + "\n".join(absent_story_line_text)
        await update.message.reply_text(await story.get_story_line_text())
        await update.message.reply_text(absent_story_line_text)
        return
    else:
        await show_story_line_with_buttons(update, context)


async def show_story_line_with_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = StoryAction.SHOW_STORY_LINE
    speech_style_names = [speech_styles[speech_style_index]['name'].lower() for speech_style_index in
                          context.user_data['author'].preferred_speech_styles]

    # Create story line
    story: Story
    if context.user_data['story_type'] == Story.PERSONAL:
        story = StoryPersonal(
            clickbait_event=context.user_data['story_line'].get(1),
            plot_start=context.user_data['story_line'].get(2),
            plot_development=context.user_data['story_line'].get(3),
            storytelling=context.user_data['story_line'].get(4),
            plot_continuation=context.user_data['story_line'].get(5),
            intermediate_results=context.user_data['story_line'].get(6),
            conclusion=context.user_data['story_line'].get(7),
            speech_style_names=speech_style_names
        )
    else:
        story = StoryExpert(
            hook=context.user_data['story_line'].get(1),
            reengagement=context.user_data['story_line'].get(2),
            plot_establishment=context.user_data['story_line'].get(3),
            climax=context.user_data['story_line'].get(4),
            resolution=context.user_data['story_line'].get(5),
            speech_style_names=speech_style_names
        )

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Генерировать историю", callback_data=StoryAction.REGEN)],
        [InlineKeyboardButton("Редактировать начальную историю", callback_data=StoryAction.EDIT_STORY_LINE)],
    ])
    last_message = await update.message.reply_text(await story.get_story_line_text(), reply_markup=reply_markup)
    context.user_data['last_message'] = {
        'chat_id': last_message.chat_id,
        'message_id': last_message.message_id,
    }


async def show_story_line(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['action'] = StoryAction.SHOW_STORY_LINE
    speech_style_names = [speech_styles[speech_style_index]['name'].lower() for speech_style_index in
                          context.user_data['author'].preferred_speech_styles]

    # Create story line
    story: Story
    if context.user_data['story_type'] == Story.PERSONAL:
        story = StoryPersonal(
            clickbait_event=context.user_data['story_line'].get(1),
            plot_start=context.user_data['story_line'].get(2),
            plot_development=context.user_data['story_line'].get(3),
            storytelling=context.user_data['story_line'].get(4),
            plot_continuation=context.user_data['story_line'].get(5),
            intermediate_results=context.user_data['story_line'].get(6),
            conclusion=context.user_data['story_line'].get(7),
            speech_style_names=speech_style_names
        )
    else:
        story = StoryExpert(
            hook=context.user_data['story_line'].get(1),
            reengagement=context.user_data['story_line'].get(2),
            plot_establishment=context.user_data['story_line'].get(3),
            climax=context.user_data['story_line'].get(4),
            resolution=context.user_data['story_line'].get(5),
            speech_style_names=speech_style_names
        )

    await update.callback_query.message.reply_text(await story.get_story_line_text())


async def set_story_line_part(update: Update, context: ContextTypes.DEFAULT_TYPE):
    story_line_part = update.message.text
    story_type = context.user_data['story_type']
    story_part_index = context.user_data['story_part_index']

    if story_type == Story.PERSONAL:
        story_line = personal_story_line
        text = "<b>Создание личной истории</b>\n\n"
    else:
        story_line = expert_story_line
        text = "<b>Создание экспертной истории</b>\n\n"

    context.user_data['story_line'][story_part_index] = story_line_part

    if story_part_index < len(story_line):
        text += story_line[story_part_index + 1]
        context.user_data['story_part_index'] = story_part_index + 1
        await update.message.reply_text(text)
    else:
        await show_story_line_with_buttons(update, context)


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'story_line' not in context.user_data:
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return

    response_message = await update.callback_query.message.reply_text("Подождите пару секунд. Генерируем историю 🔮")

    story: Story
    speech_style_names = [speech_styles[speech_style_index]['name'].lower() for speech_style_index in
                          context.user_data['author'].preferred_speech_styles]
    if context.user_data['story_type'] == Story.PERSONAL:
        story = StoryPersonal(
            clickbait_event=context.user_data['story_line'].get(1),
            plot_start=context.user_data['story_line'].get(2),
            plot_development=context.user_data['story_line'].get(3),
            storytelling=context.user_data['story_line'].get(4),
            plot_continuation=context.user_data['story_line'].get(5),
            intermediate_results=context.user_data['story_line'].get(6),
            conclusion=context.user_data['story_line'].get(7),
            speech_style_names=speech_style_names
        )
    else:
        story = StoryExpert(
            hook=context.user_data['story_line'].get(1),
            reengagement=context.user_data['story_line'].get(2),
            plot_establishment=context.user_data['story_line'].get(3),
            climax=context.user_data['story_line'].get(4),
            resolution=context.user_data['story_line'].get(5),
            speech_style_names=speech_style_names
        )

    # Generate story
    generated_story = await story_generator.generate(story)
    generated_title = await story_generator.generate_title(story, generated_story)

    response_text = f"<b>{generated_title}</b>\n\n{generated_story}"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Перегенирировать историю", callback_data=StoryAction.REGEN)],
        [InlineKeyboardButton("Редактировать начальную историю", callback_data=StoryAction.SHOW_EDIT_STORY_LINE)],
        [InlineKeyboardButton("Завершить 🟢", callback_data=StoryAction.END)],
    ])

    last_message = await context.bot.edit_message_text(
        chat_id=response_message.chat_id,
        message_id=response_message.message_id,
        text=response_text,
        reply_markup=reply_markup,
    )
    context.user_data['last_message'] = {
        'chat_id': last_message.chat_id,
        'message_id': last_message.message_id,
    }

    await update.callback_query.edit_message_reply_markup(reply_markup=None)


async def show_edit_story_line(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'story_line' not in context.user_data:
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return

    await show_story_line(update, context)
    await edit_story_line(update, context)


async def edit_story_line(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'story_line' not in context.user_data:
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return

    context.user_data['action'] = StoryAction.EDIT_STORY_LINE

    message = """Для изменения сюжетной линии напишите пункт и новый текст.\n\nНапример:\n1. Блогер кинул меня на бабки.\n2. Eще с самого детства я хотел..."""
    await update.callback_query.message.reply_text(message)
    await update.callback_query.edit_message_reply_markup(reply_markup=None)


async def dispatch_story_data(context: ContextTypes.DEFAULT_TYPE):
    if 'action' in context.user_data:
        del context.user_data['action']
    if 'story_type' in context.user_data:
        del context.user_data['story_type']
    if 'story_part_index' in context.user_data:
        del context.user_data['story_part_index']
    if 'story_line' in context.user_data:
        del context.user_data['story_line']
    if 'last_message' in context.user_data:
        await context.bot.edit_message_reply_markup(
            chat_id=context.user_data['last_message']['chat_id'],
            message_id=context.user_data['last_message']['message_id'],
            reply_markup=None,
        )

        del context.user_data['last_message']


async def cancel_story_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await dispatch_story_data(context)
    await update.message.reply_text("Создание истории было прервано 📝🔥")


async def end_story_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await dispatch_story_data(context)
    await update.callback_query.message.reply_text("""Вот и всё! 🌟 Твой текст для видео готов. Надеюсь, тебе понравится результат. 🎬

Не забудь проверить все детали и адаптировать текст под свой стиль, если это необходимо. Если тебе нужно что-то изменить или создать ещё один текст, просто введи команду /start и следуй инструкциям. 🖋️

Спасибо, что выбрал InstaIdeas для создания контента! Жду тебя снова, чтобы вместе творить удивительные истории! ✨
""")
