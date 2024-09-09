from abc import ABC, abstractmethod

from openai import OpenAI

import config


class Story(ABC):
    PERSONAL = 'Личная'
    EXPERT = 'Экспертная'

    @property
    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    async def get_story_line_text(self):
        pass

    @abstractmethod
    async def get_prompt_for_title(self, generated_story: str):
        pass

    @abstractmethod
    async def get_prompt(self):
        pass


class StoryPersonal(Story):
    type = Story.PERSONAL

    def __init__(self,
                 clickbait_event,
                 plot_start,
                 plot_development,
                 storytelling,
                 plot_continuation,
                 intermediate_results,
                 conclusion,
                 speech_style_names,
                 ):
        self.clickbait_event = clickbait_event
        self.plot_start = plot_start
        self.plot_development = plot_development
        self.storytelling = storytelling
        self.plot_continuation = plot_continuation
        self.intermediate_results = intermediate_results
        self.conclusion = conclusion
        self.speech_style_names = speech_style_names

    async def get_story_line_text(self) -> str:
        return f"""<b>Сюжетная линия:</b>
        
1. {self.clickbait_event if self.clickbait_event else ''}
2. {self.plot_start if self.plot_start else ''}
3. {self.plot_development if self.plot_development else ''}
4. {self.storytelling if self.storytelling else ''}
5. {self.plot_continuation if self.plot_continuation else ''}
6. {self.intermediate_results if self.intermediate_results else ''}
7. {self.conclusion if self.conclusion else ''}"""

    async def get_prompt(self) -> str:
        speech_styles_prompt = ', '.join(self.speech_style_names)
        prompt = f"""Я хочу создать Reels для InstagramЯ хочу создать Reels для Instagram и ищу сценарий для сторителлинга.
            Твоя задача:
            Напиши текст для сценария на основе рекомендаций:
            Не меняй порядок повествования 
            Максимально простые слова
            Используй минимум 1500 символов
            История должна быть интригующей, раскрывая суть в самом конце
            Стиль текста должен соответствовать тону моей истории: {self.speech_style_names}, без сложных оборотов, меньше метафор
            
            Структура сценария:
            1. Инфоповод/Событие: Кратко и кликбейтно описать суть истории. Максимум 7 слов
            2. Старт сюжетной линии: Ввести зрителя в начало событий одним предложением.
            3. Развитие Сюжета: Описать развитие событий, ведущих к кульминации.
            4. Рассказ Истории: Подробно изложить основную часть истории, включая мои мысли и чувства.
            5. Продолжение линии: Показать, как события развиваются дальше после ключевого момента.
            6. Промежуточные результаты: Описать, что происходит непосредственно перед итогом.
            7. Итог: Заключительная часть, где подводятся итоги и делится мораль.
            
            Мне нужен один текст без оглавлений, по типу Инфоповод/Событие, Старт Сюжетной линии и т.д.
            
            Инфоповод/Событие: {self.clickbait_event}
            Старт сюжетной линии: {self.plot_start}
            Развитие Сюжета: {self.plot_development}
            Рассказ Истории: {self.storytelling}
            Продолжение линии: {self.plot_continuation}
            Промежуточные результаты: {self.intermediate_results}
            Итог: {self.conclusion}

            Объедини все это в один сценарий, который я могу использовать для создания интересного Reels."""

        return prompt

    async def get_prompt_for_title(self, generated_story: str):
        prompt = f"""
        У меня есть текст для видео Instagram Reels:
        {generated_story}

        Напиши кликбейтное название длиной максимум в 5 слов. Без ковычек.
        """
        return prompt


class StoryExpert(Story):
    type = Story.EXPERT

    def __init__(self, hook, reengagement, plot_establishment, climax, resolution, speech_style_names):
        super().__init__()
        self.hook = hook
        self.reengagement = reengagement
        self.plot_establishment = plot_establishment
        self.climax = climax
        self.resolution = resolution
        self.speech_style_names = speech_style_names

    async def get_story_line_text(self):
        return f"""<b>Сюжетная линия:</b>
        
1. {self.hook if self.hook else ''}
2. {self.reengagement if self.reengagement else ''}
3. {self.plot_establishment if self.plot_establishment else ''}
4. {self.climax if self.climax else ''}
5. {self.resolution if self.resolution else ''}"""

    async def get_prompt(self):
        speech_styles_prompt = ', '.join(self.speech_style_names)
        prompt = f"""Я хочу создать Reels для Instagram и ищу сценарий для экспертного видео.
         Твоя задача:
         Напиши мне текст для сценария, следуя моим рекомендациям, и представь его в виде единого, непрерывного текста, не разбивая на отдельные пункты. Важно соблюдать указанный порядок повествования, использовать максимально простые слова и добиться длины в минимум 1500 символов. История должна быть интригующей с развязкой в самом конце. Тон текста — {speech_styles_prompt}, без сложных оборотов и метафор. Вот структура сценария и основные моменты моей истории:
         
1. Хук: Этот элемент представляет собой ключевой момент, который должен мгновенно привлечь внимание аудитории и вызвать желание узнать больше. Он задает тон всему видео и является первым шагом к захвату интереса зрителя. Хук должен быть кратким и мощным, способным зацепить зрителя в первые секунды просмотра.
2. Повторное вовлечение: После того как первоначальный интерес аудитории был пробужден хуком, повторное вовлечение помогает поддерживать этот интерес на протяжении всего видео. Это достигается за счет предоставления дополнительной ценности или обещания бонусного контента, которые подталкивают зрителя продолжать просмотр до конца.
3. Установка и развитие сюжета: На этом этапе создатель контента раскрывает основную тему или проблему, которая будет обсуждаться в видео. Это может включать в себя представление ключевых идей, аргументов или персонажей истории. Установка и развитие сюжета обеспечивают контекст и глубину рассказу, делая его более увлекательным и информативным для аудитории.
4. Кульминация: Это момент наивысшего напряжения и эмоционального пика сюжета, к которому ведет вся предыдущая подготовка. Кульминация является ключевым элементом, который показывает разрешение проблемы или достижение цели, обсуждаемой в видео. Она должна быть эмоционально насыщенной и запоминающейся, чтобы оставить сильное впечатление на зрителя.
5. Гуш и завершение: Завершающий этап сюжета, где подводятся итоги и повторяется основное сообщение видео. Завершение может включать призыв к действию, стимулирование обсуждения или просто подчеркивание главной мысли ролика. Это момент, когда создатель контента имеет возможность оставить последнее впечатление на аудиторию и подтвердить значимость представленного контента.
Мне нужен один текст без оглавлений, по типу Хук, Повторное вовлечение и т.д.
Моя история:
1. {self.hook}
2. {self.reengagement}
3. {self.plot_establishment}
4. {self.climax}
5. {self.resolution}

Объедини все это в один сценарий, который я могу использовать для создания интересного и полезного Reels."""
        return prompt

    async def get_prompt_for_title(self, generated_story: str):
        prompt = f"""
        У меня есть текст для видео Instagram Reels:
        {generated_story}

        Напиши кликбейтное название длиной максимум в 5 слов. Без ковычек.
        """
        return prompt


class StoryGenerator(ABC):
    @abstractmethod
    async def generate(self, story: Story) -> str:
        pass

    @abstractmethod
    async def generate_title(self, story: Story) -> str:
        pass


client = OpenAI(api_key=config.OPENAI_API_KEY)


class OpenAIStoryGenerator(StoryGenerator):
    async def generate_personal(self, story: Story) -> str:
        messages = [
            {"role": "system", "content": "Вы помощник, который пишет сценарий для видео в Instagram Reels."},
            {"role": "user", "content": await story.get_prompt()}
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        gpt_text = response.choices[0].message.content

        return gpt_text

    def after_personal(self, gpt_text: str) -> str:
        pass

    async def generate_expert(self, story: Story) -> str:
        messages = [
            {"role": "system", "content": "Вы помощник, который пишет сценарий для экспертного видео."},
            {"role": "user", "content": await story.get_prompt()}
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        gpt_text = response.choices[0].message.content

        return gpt_text

    async def after_expert(self, gpt_text: str) -> str:
        substrings = [
            "Хук",
            "Повторное вовлечение",
            "Установка и развитие сюжета",
            "Кульминация",
            "Гуш и завершение",
        ]

        text_parts = []
        for i in range(len(substrings)):
            text_from = gpt_text.find(substrings[i])
            if text_from == -1:
                break

            text_to = gpt_text.find(substrings[i + 1]) if i + 1 != len(substrings) else -1
            text_part = gpt_text[text_from:text_to]

            text_part = text_part.replace(substrings[i], "")
            text_part = text_part.strip(":").strip("")
            if text_part.startswith('"') and text_part.endswith('"'):
                text_part = text_part[1:-2]

            text_parts.append(text_part)

        if text_parts:
            return "".join(text_parts)

        return gpt_text

    async def generate(self, story: Story) -> str:
        if story.type == Story.PERSONAL:
            gpt_text = await self.generate_personal(story)
        else:
            gpt_text = await self.generate_expert(story)
            gpt_text = await self.after_expert(gpt_text)

        return gpt_text

    async def generate_title_personal(self, generated_story: str) -> str:
        messages = [
            {
                "role": "user",
                "content": generated_story + " .Придумай кликбейтное название для истории (максимум 5 слов)",
            }
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        title = response.choices[0].message.content

        return title

    async def generate_title_expert(self, generated_story: str) -> str:
        messages = [
            {
                "role": "user",
                "content": generated_story + " .Придумай кликбейтное название для истории (максимум 5 слов)",
            }
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        title = response.choices[0].message.content

        return title

    async def generate_title(self, story: Story, generated_story: str) -> str:
        if story.type == Story.PERSONAL:
            title = await self.generate_title_personal(generated_story)
        else:
            title = await self.generate_title_expert(generated_story)

        title = title.strip('"')

        return title


class DumpStoryGenerator(StoryGenerator):
    async def generate(self, story: Story) -> str:
        return await story.get_prompt()

    async def generate_title(self, story: Story) -> str:
        return await story.get_prompt()


story_generator = OpenAIStoryGenerator()
