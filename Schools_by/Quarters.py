from aiohttp import ClientSession
from bs4 import BeautifulSoup

from ..Schools_by import Student


class QuartersManager:
    def __init__(self, student: Student):
        self.student = student

    async def get_quarter_id(self, quarter: int = 0) -> int:
        """
        :param quarter: number from 1 to 4
        :return: Global quarter id
        """
        async with ClientSession() as client_session:
            req = await client_session.get(f'{self.student.personal_url}/pupil/{self.student.student_id}/dnevnik',
                                           headers={'user-agent': self.student.agent},
                                           cookies=self.student.cookies)
            soup = BeautifulSoup(await req.content.read(), features="html.parser")
            req.close()
            uls = soup.find_all('ul', {'id': f'db_quarters_menu_{self.student.student_id}'})
            for ul in uls:
                lis = ul.find_all('li')
                for li in lis:
                    a = li.find('a')
                    span = a.find('span').text
                    if span == f'{quarter} четверть':
                        return int(a['quarter_id'])

    async def get_current_quarter(self) -> int:
        """
        Get current quarter
        :return: Number from 1 to 4
        """
        async with ClientSession() as client_session:
            req = await client_session.get(f'{self.student.personal_url}/pupil/{self.student.student_id}/dnevnik',
                                           headers={'user-agent': self.student.agent},
                                           cookies=self.student.cookies)
            soup = BeautifulSoup(await req.content.read(), features="html.parser")
            req.close()
            num = soup.find('a', {'class': 'current'}).text
            num = int(num.split(' ')[0])
            return num

    async def get_current_quarter_full(self) -> int:
        """
        Get global id of current quarter
        :return: Global quarter id
        """
        async with ClientSession() as client_session:
            req = await client_session.get(f'{self.student.personal_url}/pupil/{self.student.student_id}/dnevnik',
                                           headers={'user-agent': self.student.agent},
                                           cookies=self.student.cookies)
            soup = BeautifulSoup(await req.content.read(), features="html.parser")
            req.close()
            num = soup.find('a', {'class': 'current'})['quarter_id']
            num = int(num)
            return num
