import json
import re


def bot_response(contents):
    command = re.split(': | |:', contents['text'])
    res = {'success': False, 'type': 'bot', 'text': ''}
    if command[1] == "ping":
        res['success'] = True
        res['text'] = 'pong'
    return json.dumps(res)
