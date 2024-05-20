__all__ = [
    'WebUser',
    'Student',
    'StudentData',
    'MarksManager',
    'QuarterManager',
    'LessonsManager'
]

from .Student import Student, StudentData
from .WebUser import WebUser
from . import MarksManager, QuarterManager, LessonsManager
