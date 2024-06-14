import asyncio
from datetime import datetime, timedelta
from typing import List

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from ..Schools_by import Student, QuarterManager
from ..Schools_by import Lesson
from ..Utils import PagesManager


class Mark:
    def __init__(self,
                 lesson: Lesson,
                 value: int | str | None,
                 date: datetime = None
                 ):
        self.value = value
        if type(value) is str:
            if value.isdigit():
                self.value = int(value)
        self.date = date
        self.lesson = lesson


class SplitMark(Mark):
    def __init__(self,
                 lesson: Lesson,
                 first_mark: int,
                 second_mark: int,
                 date: datetime = None
                 ):
        super().__init__(lesson, f'{first_mark}/{second_mark}', date)
        self.first_mark = first_mark
        self.second_mark = second_mark


async def get_quarters_marks(student: Student, quarter: int) -> list:
    async with ClientSession() as client_session:
        q_marks = []

        req = await client_session.get(f'{student.personal_url}/pupil/{student.student_id}/dnevnik/last-page',
                                       headers={'user-agent': student.agent},
                                       cookies=student.cookies)

        soup = BeautifulSoup(await req.content.read(), features="html.parser")
        req.close()

        # lessons names
        table_lessons = soup.find('div', {'id': f'daybook-last-page-container-{student.student_id}'})
        lessons_body = table_lessons.find('tbody')
        lessons_names = lessons_body.find_all('a')

        table = soup.find('table', {'id': f'daybook-last-page-table-{student.student_id}'})
        body = table.find('tbody')
        trs = body.find_all('tr', {'class': 'marks'})
        i = 0
        for tr in trs:
            tds = tr.find_all('td', {'class': 'qmark'})
            mark = tds[quarter - 1].text
            l_name = lessons_names[i].text
            l_full_name = lessons_names[i]['title']

            mark_obj = Mark(
                Lesson(l_name, l_full_name),
                None,
            )

            if mark == '':
                mark_obj.value = None
            else:
                mark_obj.value = mark

            q_marks.append(mark_obj)
            i += 1

        return q_marks


async def get_all_data_from_page(student: Student,
                                 interval: dict,
                                 quarter: int,
                                 page: int,
                                 lesson_obj: Lesson = Lesson()) -> dict:
    # get date
    current_year = datetime.now().year
    start_date = datetime(current_year,
                          interval[quarter].start_month,
                          interval[quarter].start_date)
    end_date = datetime(current_year,
                        interval[quarter].end_month,
                        interval[quarter].end_date)

    # get marks in this quarter
    full_quarter = await QuarterManager.get_quarter_id(student, quarter)

    date = start_date

    data_dict = {}

    i = 1
    async with ClientSession() as client_session:

        while True:
            if date > end_date:
                break

            if i == page:
                date_url = date.strftime("%Y-%m-%d")
                req = await client_session.get(f'{student.personal_url}/pupil/'
                                               f'{student.student_id}/dnevnik/'
                                               f'quarter/{full_quarter}/week/{date_url}',
                                               headers={'user-agent': student.agent},
                                               cookies=student.cookies)

                soup = BeautifulSoup(await req.content.read(), features="html.parser")
                req.close()

                table = soup.find_all('div', {'class': 'db_days clearfix'})[1]

                days = table.find_all('div', {'class': 'db_day'})
                day_int = 0
                for day in days:
                    lessons = day.find('tbody').find_all('tr')
                    data_to_insert = []
                    day_date = start_date + timedelta(
                        weeks=page - 1,
                        days=day_int)
                    for lesson in lessons:
                        ln = lesson.find('td', {'class': 'lesson'}).text
                        ln = ln.replace('\n', '')[2:]
                        ln = ln.strip()

                        if ln != '':
                            if ln == lesson_obj.name or lesson_obj.name is None:
                                mark = lesson.find('div', {'class': 'mark_box'}).text
                                mark = mark.replace('\n', '')

                                if mark != '':
                                    mark_date = start_date + timedelta(
                                        weeks=page - 1,
                                        days=day_int)
                                    if mark.find('/') != -1:
                                        data_to_insert.append(
                                            SplitMark(
                                                Lesson(ln),
                                                int(mark.split('/')[0]),
                                                int(mark.split('/')[1]),
                                                date=mark_date
                                            )
                                        )
                                    else:
                                        data_to_insert.append(
                                            Mark(
                                                Lesson(ln),
                                                mark,
                                                date=mark_date
                                            )
                                        )
                                else:
                                    data_to_insert.append(
                                        Lesson(
                                            ln
                                        )
                                    )
                    day_int += 1
                    data_dict[day_date.strftime("%d.%m")] = data_to_insert

            date = date + timedelta(weeks=1)
            i = i + 1
        return data_dict


async def get_all_marks_from_page(student: Student,
                                  interval: dict,
                                  quarter: int,
                                  page: int,
                                  lesson_obj: Lesson = Lesson()) -> list[Mark | SplitMark]:
    data = await get_all_data_from_page(student, interval, quarter, page, lesson_obj)
    r = []
    for d in data:
        for item in data[d]:
            if item.__class__ in [Mark, SplitMark]:
                item: Mark | SplitMark
                r.append(item)
    return r


async def get_all_marks(student: Student, quarter: int,
                        lesson_obj: Lesson = Lesson()) -> list:
    interval = await PagesManager.get_intervals(student)

    weeks = PagesManager.get_pages_count(interval, quarter)

    tasks = []

    for i in range(1, weeks + 1):
        task = asyncio.create_task(get_all_marks_from_page(student, interval, quarter, i, lesson_obj))
        tasks.append(task)

    result = await asyncio.gather(*tasks)

    r = [x for xs in result for x in xs]
    return r


def convert_marks_list(marks: List[Mark | SplitMark]) -> List[int | str]:
    result = []
    for mark in marks:
        if mark.__class__ == Mark:
            result.append(mark.value)

        if mark.__class__ == SplitMark:
            result.append(mark.first_mark)
            result.append(mark.second_mark)

    return result
