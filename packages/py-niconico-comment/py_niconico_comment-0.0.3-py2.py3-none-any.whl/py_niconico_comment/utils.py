
import json
import time


def write_file(path, context):   # pragma: no cover
    with open(path, 'w') as fh:
        fh.write(str(context).replace('\n', '\r\n'))


def seconds_to_string(seconds):
    return time.strftime('%H:%M:%S', time.gmtime(seconds))


def parse_api_data(api_data, language='en'):
    data = json.loads(api_data)
    userkey = data.get('context', {}).get('userkey')
    thread_id = data.get('thread', {}).get('ids', {}).get('default')
    user_id = data.get('viewer', {}).get('id')
    language_id = {'en': 1, 'jp': 0}.get(language, 1)
    return [{
        'ping': {
            'content': 'rs:0'
        }
    }, {
        'ping': {
            'content': 'ps:0'
        }
    }, {
        'thread': {
            'thread': thread_id,
            'version': '20090904',
            'language': language_id,
            'user_id': user_id,
            'with_global': 0,
            'scores': 1,
            'nicoru': 3,
            'userkey': userkey
        }
    }, {
        'ping': {
            'content': 'pf:0'
        }
    }, {
        'ping': {
            'content': 'ps:1'
        }
    }, {
        'thread_leaves': {
            'thread': thread_id,
            'language': language_id,
            'user_id': user_id,
            'content': '0-10:100,500,nicoru:100',
            'scores': 1,
            'nicoru': 3,
            'userkey': userkey
        }
    }, {
        'ping': {
            'content': 'pf:1'
        }
    }, {
        'ping': {
            'content': 'rf:0'
        }
    }]
