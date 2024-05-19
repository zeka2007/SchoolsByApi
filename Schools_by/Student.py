from aiohttp import ClientSession
from bs4 import BeautifulSoup


class StudentData:
    def __init__(self,
                 student_name: str,
                 in_class: str,
                 birthday: str,
                 ):
        self.birthday = birthday
        self.in_class = in_class
        self.student_name = student_name


class Student:
    def __init__(self,
                 login: str,
                 password: str,
                 csrf_token: str,
                 session_id: str,
                 site_prefix: str,
                 student_id: int,
                 agent: str = ''):
        self.site_prefix = site_prefix
        self.session_id = session_id
        self.csrf_token = csrf_token
        self.password = password
        self.login = login
        self.student_id = student_id
        self.agent = agent

        self.personal_url = f'https://{self.site_prefix}.schools.by'
        self.cookies = {
            'csrftoken': self.csrf_token,
            'sessionid': self.session_id,
            'slc_cookie': '{slcMakeBetter}{headerPopupsIsClosed}'
        }

    async def get_student_info(self) -> StudentData:
        info = {
            'student_name': None,
            'class': None,
            'birthday': None
        }
        async with ClientSession() as client_session:
            req = await client_session.get(f'{self.personal_url}/pupil/{self.student_id}',
                                           headers={'user-agent': self.agent},
                                           cookies=self.cookies)
            soup = BeautifulSoup(await req.content.read(), features="html.parser")
            req.close()
            info['student_name'] = soup.find('h1').text.replace('\n', '')

            divs = soup.find_all('div', {'class': 'pp_line'})
            for div in divs:
                b = div.find('b')
                if b is not None:
                    if b.text.startswith('Ученик'):
                        text = div.find('a').text
                        info['class'] = text.replace('-го', '')

                label = div.find('div', {'class': 'label'})
                if label is not None:
                    if label.text.find('Дата рождения') != -1:
                        info['birthday'] = div.find('div', {'class': 'cnt'}).text.replace('\n', '')

            return StudentData(
                info['student_name'],
                info['class'],
                info['birthday']
            )