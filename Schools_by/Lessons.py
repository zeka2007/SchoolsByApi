from typing import List

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from . import Student


class Lesson:
    def __init__(self,
                 name: str = None,
                 full_name: str = None):
        self.full_name = full_name
        self.name = name


class LessonsManager:
    def __init__(self, student: Student):
        self.student = student

    async def get_lessons(self) -> List[Lesson]:
        async with ClientSession() as client_session:

            req = await client_session.get(
                f'{self.student.personal_url}/pupil/{self.student.student_id}/dnevnik/last-page',
                headers={'user-agent': self.student.agent},
                cookies=self.student.cookies
            )

            soup = BeautifulSoup(await req.content.read(), features="html.parser")
            req.close()
            table_lessons = soup.find('div', {'id': f'daybook-last-page-container-{self.student.student_id}'})
            lessons_body = table_lessons.find('tbody')
            lessons_names = lessons_body.find_all('a')

            lessons = [Lesson(' '.join(name.text.split()), name['title']) for name in lessons_names]

            return lessons
