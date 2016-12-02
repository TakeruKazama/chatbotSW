import json
import re
from time import sleep


class BotCommand():
    '''
    ここにコマンドの説明を書きます
    '''

    def process(self, command):
        pass

    def pack(self, succes=True, type_='bot', text=''):
        return json.dumps({'success': succes, 'type': type_, 'text': text}).encode('utf8')


class PingCommand(BotCommand):
    '''
    ステータスチェックコマンド、pongを返します。
    '''
    name = 'ping'

    def process(self, command):
        return [self.pack(text='pong')]


class HelpCommand(BotCommand):
    '''
    コマンドのヘルプを見れます。
    '''
    name = 'help'

    def process(self, command):
        l = []
        for s in BotCommand.__subclasses__():
            l.append(self.pack(text=s.name+': '+s.__doc__))
        return l


class min3Command(BotCommand):
    '''
    ３分後に知らせてくれます。
    '''
    name = '3min'

    def process(self, command):
        for i in range(1, 4):
            sleep(60)
            yield self.pack(text=str(i)+'分経ちました。')
# ------------------------------------#


def bot_response(contents):
    command = re.split(': | |:', contents['text'])
    if len(command) < 3:
        command.append('')
    tar = next((x for x in BotCommand.__subclasses__() if x.name == command[1]), None)()

    return tar.process(command)
