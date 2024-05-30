from aiohttp import ClientSession
from bs4 import BeautifulSoup
from ..Schools_by import Student
from ..Utils import Config


class WebUser:
    def __init__(self, agent: str = ''):
        self.agent = agent

    async def login_user(self, login: str, password: str) -> Student | None:
        headers = {
            'user-agent': self.agent,
            'Referer': Config.URL
        }

        async with ClientSession() as clientSession:
            # Retrieve the CSRF token first
            req = await clientSession.get('https://schools.by/login',
                                          headers={'user-agent': self.agent})

            soup = BeautifulSoup(await req.content.read(), features="html.parser")
            req.close()
            csrftoken = soup.find('input', dict(name='csrfmiddlewaretoken'))['value']

            login_data = {
                'csrfmiddlewaretoken': csrftoken,
                'username': login,
                'password': password,
                '|123': '|123'
            }
            req = await clientSession.post(
                Config.URL,
                data=login_data,
                headers=headers,
                allow_redirects=True)
            redirect_url = str(req.url)
            if redirect_url == Config.URL:
                req.close()
                return None

            site_prefix = redirect_url.split('.')[0].replace('https://', '')
            student_id = int(redirect_url.split('/')[-1])

            csrf_token = ''
            session_id = ''

            for resp in req.history:
                csrf_token = resp.cookies['csrftoken'].value
                session_id = resp.cookies['sessionid'].value
            req.close()

            return Student(
                login,
                password,
                csrf_token,
                session_id,
                site_prefix,
                student_id,
                self.agent
            )

    async def check_login_data(self, csrf_token: str, session_id: str) -> bool:
        async with ClientSession() as clientSession:
            # Retrieve the CSRF token first
            req = await clientSession.get('https://schools.by/login',
                                          headers={'user-agent': self.agent},
                                          cookies={
                                                'csrftoken': csrf_token,
                                                'sessionid': session_id,
                                                'slc_cookie': '{slcMakeBetter}{headerPopupsIsClosed}'
                                            },
                                          allow_redirects=True
                                          )

            redirect_url = str(req.url)
            req.close()
            if redirect_url == Config.URL:
                return False
            return True
