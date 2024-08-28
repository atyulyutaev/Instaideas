from enum import Enum, auto


class StrEnum(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class Action(StrEnum):
    SET_PROFILE = auto()
    EDIT_PROFILE = auto()
    CREATE_STORY = auto()


class ProfileAction(StrEnum):
    SET_GENDER = auto()
    SET_AGE = auto()
    SET_SPEECH_STYLE = auto()
    SAVE = auto()
    END_SPEECH_STYLE = auto()
    EDIT_GENDER = auto()
    EDIT_AGE = auto()
    EDIT_SPEECH_STYLE = auto()


class StoryAction(StrEnum):
    SET_STORY_LINE = auto()
    EDIT_STORY_LINE = auto()
    SHOW_EDIT_STORY_LINE = auto()
    SHOW_STORY_LINE = auto()
    REGEN = auto()
    END = auto()
