import requests
import time
from bs4 import BeautifulSoup


class Cleaner:
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/87.0.4280.66 Safari/537.36 '
    login_headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": 'https://www.dcinside.com/',
        'User-Agent': user_agent
    }
    delete_headers = {
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
        'User-Agent': user_agent
    }

    def __init__(self, gui):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        self.user_id = None
        self.pw = None
        self.logged_in = False
        self.gui = gui

    @staticmethod
    def serialize_form(input_elements):
        form = {}
        for input_element in input_elements:
            form[input_element['name']] = input_element['value']
        return form

    def get_num_posts(self, post_type):
        gallog = f'https://gallog.dcinside.com/{self.user_id}/{post_type}'
        self.session.headers.update({'User-Agent': self.user_agent})
        res = self.session.get(gallog)
        soup = BeautifulSoup(res.text, 'html.parser')
        num_posts = soup.select_one('header > div > div.choice_sect > button.on > span').text
        num_posts = int(num_posts[1:-1])
        return num_posts

    def get_post_no(self, post_type):
        gallog = f'https://gallog.dcinside.com/{self.user_id}/{post_type}?p=1'
        self.session.headers.update({'User-Agent': self.user_agent})
        res = self.session.get(gallog)
        soup = BeautifulSoup(res.text, 'html.parser')
        if not soup.select_one('body'):
            return 'BLOCKED'

        post_list_elements = soup.select('.cont_listbox > li')
        if len(post_list_elements) < 1:
            return None

        return post_list_elements[0]['data-no']

    def login(self, user_id, pw):
        info = 'LOGIN\n\n'
        if self.logged_in:
            self.gui.output(info + f'이미 로그인 되었습니다.\nID : {self.user_id}\nPW : {("*" * len(self.pw))}')
            return True
        self.gui.output(info + f'로그인 시도중입니다.\nID : {user_id}\nPW : {("*" * len(pw))}')
        self.user_id = user_id
        self.pw = pw
        self.session.headers.update(self.login_headers)
        res = self.session.get('https://www.dcinside.com/')
        soup = BeautifulSoup(res.text, 'html.parser')

        input_elements = soup.select('#login_process > input')
        login_data = self.serialize_form(input_elements)
        login_data['user_id'], login_data['pw'] = user_id, pw
        self.session.post(
            'https://dcid.dcinside.com/join/member_check.php', data=login_data)
        res = self.session.get('https://www.dcinside.com/')
        soup = BeautifulSoup(res.text, 'html.parser')
        if bool(soup.select('.logout')):
            self.logged_in = True
            self.gui.output(info + f'로그인 성공.\nID : {user_id}\nPW : {("*" * len(pw))}')
        else:
            self.gui.output(info + '로그인 실패.\nID나 PW가 일치하지 않습니다.\n다시 시도해주세요.')
        return True

    def delete_post(self, post_no, post_type):
        gallog = f'https://gallog.dcinside.com/{self.user_id}/{post_type}'
        self.session.headers.update({'User-Agent': self.user_agent})
        res = self.session.get(gallog)
        soup = BeautifulSoup(res.text, 'html.parser')

        if not soup.select_one('body'):
            return False
        form_data = {
            'ci_t': self.session.cookies.get_dict()['ci_c'],
            'no': post_no,
            'service_code': 'undefined'
        }
        self.delete_headers['Referer'] = self.user_id
        self.session.headers.update(self.delete_headers)
        res = self.session.post(
            f'https://gallog.dcinside.com/{self.user_id}/ajax/log_list_ajax/delete',
            data=form_data
        )
        data = res.json()
        if res.status_code == 200 and data['result'] == 'success':
            return {}

        return data

    @staticmethod
    def get_time(_time):
        h = str(int(_time / 3600))
        m = str(int((_time % 3600) / 60))
        s = str(int((_time % 60)))
        return f'약 {h}시간 {m}분 {s}초'

    def delete_posts(self, post_type):
        info = f'DELETE {post_type.upper()}S\n\n'
        if not self.logged_in:
            self.gui.output(info + f'로그인이 되지 않았습니다.\nID와 PW를 입력한 후\n로그인 버튼을 눌러주세요.')
            return False
        hangul = {'posting': '게시글', 'comment': '댓글'}
        self.gui.output(info + f'잠시만 기다려주세요.\n{hangul[post_type]} 개수를 세고 있습니다.\n')
        num_posts = self.get_num_posts(post_type)
        cnt = 0
        sum_time = 0

        self.gui.output(info + f'{cnt} / {num_posts} 삭제 완료\n소요 시간 : {str(self.get_time(0))}\n')
        while True:
            start_time = time.time()
            post_no = self.get_post_no(post_type)
            if post_no == 'BLOCKED':
                return 'BLOCKED'
            elif post_no is None:
                break
            time.sleep(1)
            res = self.delete_post(post_no, post_type)
            if res and 'captcha' in res['result']:
                return 'CAPTCHA'
            cnt += 1
            sum_time += time.time() - start_time
            self.gui.progressbar.setValue(cnt / num_posts * 100)
            expected_time = sum_time if cnt == num_posts else sum_time / cnt * (num_posts - cnt)
            self.gui.output(
                info + f'{cnt} / {num_posts} 삭제 완료\n소요 시간 : {str(self.get_time(sum_time))}\n' +
                f'남은 시간 : {str(self.get_time(expected_time))}'
            )

        return True
