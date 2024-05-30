from aiohttp import ClientSession
from bs4 import BeautifulSoup

from ..Schools_by import Student


async def get_quarter_id(student: Student, quarter: int = 0) -> int:
    async with ClientSession() as client_session:
        req = await client_session.get(f'{student.personal_url}/pupil/{student.student_id}/dnevnik',
                                       headers={'user-agent': student.agent},
                                       cookies=student.cookies)
        soup = BeautifulSoup(await req.content.read(), features="html.parser")
        req.close()
        uls = soup.find_all('ul', {'id': f'db_quarters_menu_{student.student_id}'})
        for ul in uls:
            lis = ul.find_all('li')
            for li in lis:
                a = li.find('a')
                span = a.find('span').text
                if span == f'{quarter} четверть':
                    return a['quarter_id']


async def get_current_quarter(student: Student) -> int:
    async with ClientSession() as client_session:
        req = await client_session.get(f'{student.personal_url}/pupil/{student.student_id}/dnevnik',
                                       headers={'user-agent': student.agent},
                                       cookies=student.cookies)
        soup = BeautifulSoup(await req.content.read(), features="html.parser")
        req.close()
        num = soup.find('a', {'class': 'current'}).text
        num = int(num.split(' ')[0])
        return num


async def get_current_quarter_full(student: Student) -> int:
    async with ClientSession() as client_session:
        req = await client_session.get(f'{student.personal_url}/pupil/{student.student_id}/dnevnik',
                                       headers={'user-agent': student.agent},
                                       cookies=student.cookies)
        soup = BeautifulSoup(await req.content.read(), features="html.parser")
        req.close()
        num = soup.find('a', {'class': 'current'})['quarter_id']
        num = int(num)
        return num
