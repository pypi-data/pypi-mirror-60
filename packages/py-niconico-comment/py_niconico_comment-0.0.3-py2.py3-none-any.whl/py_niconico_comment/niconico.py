import json
import logging

from lxml import html
from py_niconico_comment import utils
from requests.sessions import Session

SRT_TEMPLATE = """
%0.f
%s,{0} --> %s,{0}
%s
"""

_logger = logging.getLogger(__name__)


class NiconicoComments(object):
    _session = None
    is_login = False

    def __init__(self, username, password, loglevel=logging.CRITICAL):
        _logger.setLevel(loglevel)
        self._session = Session()
        self.is_login = self._login(username, password)

    def _cookie_has(self, key):
        return key in self._session.cookies if self._session else False

    def _login(self, username, password):
        """https://account.nicovideo.jp/api/v1/login

        Args:
            username ([str]): Username.
            password ([str]): Password.

        Returns:
            [bool]: login success or not.
        """
        login_form_strs = {
            'mail_tel': username,
            'password': password,
        }
        try:
            self._request_webpage('https://account.nicovideo.jp/api/v1/login', action='login',
                                  data=(login_form_strs), headers={'content-type': 'application/x-www-form-urlencoded'})
            return self._cookie_has('user_session')
        except Exception as error:   # pragma: no cover
            _logger.info('unable to log in: {}'.format(error))
        return False   # pragma: no cover

    def _request_webpage(self, url_or_request, action=None, data=None, headers={}, query={}):
        """Returns the response handle

        Args:
            url_or_request ([str]): URL
            action ([str], optional): login/get-comments. Defaults to None.
            data ([dict], optional): request data. Defaults to None.
            headers (dict, optional): request headers. Defaults to {}.
            query (dict, optional): request query. Defaults to {}.

        Returns:
            [str]: text
        """
        if action in ['login', 'get-comments']:
            return self._session.post(url_or_request, data, headers).text
        return self._session.get(url_or_request).text

    def _get_api_data(self, html_string):
        for div in html.fromstring(html_string).cssselect('div'):
            api_data = div.get('data-api-data')
            if api_data is not None:
                return api_data

    def get_list_user(self, url, language='en'):
        """Get all user who commented on the giving URL.

        Args:
            url ([str]): Nicovideo URL e.g. https://www.nicovideo.jp/watch/sm32047026
            language ([str], optional): en/jp. Defaults to en.

        Returns:
            [dict]: e.g.
            '{ \
                "rbVzlqGMytJmCIimR1dPWvGRE7w": [ \
                    "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww" \
                ], \
                "1oYUfTHMjDooDge1QKRpu3QeAmk": [ \
                    "wow", \
                    "wwwwwwwwwwww" \
                ] \
            }'
        """
        comments = self.get_comments(url, language=language)
        users = {}
        for x in comments:
            if 'user_id' not in x.keys():
                continue
            if x['user_id'] not in users.keys():
                users.update({x['user_id']: [x['content']]})
            elif len(users[x['user_id']]) < 2:
                users[x['user_id']].append(x['content'])
        return users

    def get_comments(self, url, user_id=None, language='en'):
        """Get all comment from the giving URL.

        Args:
            url ([str]): Nicovideo URL e.g. https://www.nicovideo.jp/watch/sm32047026
            user_id ([str], optional): Filter by user_id. Defaults to None.
            language ([str], optional): en/jp. Defaults to en.

        Returns:
            [list]: List of comment.
        """
        comment_html = self._request_webpage(url)
        raw_api_data = self._get_api_data(comment_html)
        if not raw_api_data:
            raise ValueError('Cannot access the giving URL!')
        api_data = utils.parse_api_data(raw_api_data, language=language)
        url = 'https://nmsg.nicovideo.jp/api.json/'
        resp = self._request_webpage(
            url, action='get-comments', data=json.dumps(api_data), headers={'content-type': 'application/json'})
        chats = (x.get('chat') for x in json.loads(resp) if 'chat' in x.keys())
        if user_id:
            chats = (x for x in chats if x['user_id'] in user_id)
        return sorted(chats, key=lambda chat: int(chat['vpos']))

    def to_srt(self, list_comments=[], shift_time=0.0):
        """Convert the list of comment to .SRT file content.

        Args:
            list_comments (list, optional): List of comment. Defaults to [].
            shift_time (float, optional): +/- time. Defaults to 0.0.

        Returns:
            [str]: SRT file content.
        """
        content = ''
        shift_time = float(shift_time)
        shift_frame = int(str(shift_time).rpartition('.')[-1])
        for index, chat in enumerate(list_comments):
            start_time = int(chat.get('vpos', 0))
            frame = start_time % 100 + shift_frame
            start_time = start_time / 100 + shift_time
            end_time = start_time + 3 + shift_time
            line = chat.get('content', '').strip()
            if line:
                sub = SRT_TEMPLATE % (
                    index,
                    utils.seconds_to_string(start_time),
                    utils.seconds_to_string(end_time),
                    line)
                content += sub.format(frame)
        return content
