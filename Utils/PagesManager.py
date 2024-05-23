from math import ceil
from datetime import datetime
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from ..Schools_by import Student
from .DateFormat import date_format as df


class IntervalData:
    def __init__(self,
                 start_date: int,
                 start_month: str,
                 end_date: int,
                 end_month: str):
        self.end_month = end_month
        self.end_date = end_date
        self.start_month = start_month
        self.start_date = start_date


async def get_intervals(student: Student) -> dict:
    async with ClientSession() as client_session:
        interval = {}

        req = await client_session.get(f'{student.personal_url}/pupil/{student.student_id}/dnevnik/last-page',
                                       headers={'user-agent': student.agent},
                                       cookies=student.cookies)

        soup = BeautifulSoup(await req.content.read(), features="html.parser")
        req.close()
        tds = soup.find_all('td', {'class': 'qdates'})
        i = 1
        for td in tds:
            result = td.text.replace('-', ' ')
            result = result.replace('\n', '')
            result = result.strip()
            result = result.split(' ')

            date_start = int(result[0])
            month_start = df[result[1]]
            date_end = int(result[2])
            month_end = df[result[3]]
            interval[i] = IntervalData(
                date_start,
                month_start,
                date_end,
                month_end
            )
            i = i + 1

        return interval


def get_pages_count(intervals: dict, quarter: int) -> int:
    # get date
    current_year = datetime.now().year
    # if quarter <= 2:
    #     start_date = datetime.datetime(current_year - 1,
    #                                    interval[quarter]['start_month'],
    #                                    interval[quarter]['start_date'])
    #     end_date = datetime.datetime(current_year - 1,
    #                                  interval[quarter]['end_month'],
    #                                  interval[quarter]['end_date'])
    # else:
    start_date = datetime(current_year,
                          intervals[quarter].start_month,
                          intervals[quarter].start_date)
    end_date = datetime(current_year,
                        intervals[quarter].end_month,
                        intervals[quarter].end_date)

    date = end_date - start_date

    return int(((date.days - (date.days % 7)) / 7) + 1)


def get_current_page(intervals: dict, quarter: int) -> int:
    current_year = datetime.now().year
    current_day = datetime.now()

    start_date = datetime(current_year,
                          intervals[quarter].start_month,
                          intervals[quarter].start_date)
    days_count = (current_day - start_date).days
    return ceil(days_count / 7)
