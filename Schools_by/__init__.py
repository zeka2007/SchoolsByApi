__all__ = [
    'WebUser',
    'Student',
    'StudentData',
    "Mark",
    "SplitMark",
    "Lesson",
]

from .Student import Student, StudentData
from .WebUser import WebUser
from .LessonsManager import Lesson
from .MarksManager import Mark, SplitMark
