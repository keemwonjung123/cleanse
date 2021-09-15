import requests
from bs4 import BeautifulSoup


class Cleaner:
    AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/87.0.4280.66 Safari/537.36 '
    LOGIN_HEADERS = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": 'https://www.dcinside.com/',
        'User-Agent': AGENT
    }
    DELETE_HEADERS = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'gallog.dcinside.com',
        'Origin': 'https://gallog.dcinside.com',
        'Referer': '',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': AGENT
    }

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.AGENT})
        self.user_id = None
        self.pw = None
        self.logged_in = False

    @staticmethod
    def serialize_form(input_elements):
        form = {}
        for input_element in input_elements:
            form[input_element['name']] = input_element['value']
        return form

    def get_number_of_posts(self, post_type):
        gallog = f'https://gallog.dcinside.com/{self.user_id}/{post_type}'
        self.session.headers.update({'User-Agent': self.AGENT})
        res = self.session.get(gallog)
        soup = BeautifulSoup(res.text, 'html.parser')
        num_posts = soup.select_one('header > div > div.choice_sect > button.on > span').text
        num_posts = int(num_posts[1:-1])
        return num_posts

    def get_post_number(self, post_type):
        gallog = f'https://gallog.dcinside.com/{self.user_id}/{post_type}?p=1'
        self.session.headers.update({'User-Agent': self.AGENT})
        res = self.session.get(gallog)
        soup = BeautifulSoup(res.text, 'html.parser')
        if not soup.select_one('body'):
            return 'BLOCKED'

        post_list_elements = soup.select('.cont_listbox > li')
        if len(post_list_elements) < 1:
            return None

        return post_list_elements[0]['data-no']

    def login(self, user_id, pw):
        self.user_id = user_id
        self.pw = pw
        self.session.headers.update(self.LOGIN_HEADERS)
        res = self.session.get('https://www.dcinside.com/')
        soup = BeautifulSoup(res.text, 'html.parser')

        input_elements = soup.select('#login_process > input')
        login_data = self.serialize_form(input_elements)
        login_data['user_id'], login_data['pw'] = user_id, pw
        self.session.post(
            'https://dcid.dcinside.com/join/member_check.php', data=login_data)
        res = self.session.get('https://www.dcinside.com/')
        soup = BeautifulSoup(res.text, 'html.parser')
        return bool(soup.select('.logout'))

    def delete_post(self, post_no, post_type):
        gallog = f'https://gallog.dcinside.com/{self.user_id}/{post_type}'
        self.session.headers.update({'User-Agent': self.AGENT})
        res = self.session.get(gallog)
        soup = BeautifulSoup(res.text, 'html.parser')

        if not soup.select_one('body'):
            return False
        form_data = {
            'ci_t': self.session.cookies.get_dict()['ci_c'],
            'no': post_no,
            'service_code': 'undefined'
        }
        self.DELETE_HEADERS['Referer'] = self.user_id
        self.session.headers.update(self.DELETE_HEADERS)
        res = self.session.post(
            f'https://gallog.dcinside.com/{self.user_id}/ajax/log_list_ajax/delete',
            data=form_data
        )
        data = res.json()
        if res.status_code == 200 and data['result'] == 'success':
            return {}

        return data
