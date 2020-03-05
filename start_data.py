# coding:utf-8
import random
import json
import signal
import sys
import time
import re
import base64
from autobahn.twisted.websocket import connectWS
from autobahn.websocket.compress import (
    PerMessageDeflateOffer,
    PerMessageDeflateResponse,
    PerMessageDeflateResponseAccept,
)
from autobahn.websocket.protocol import WebSocketProtocol
from twisted.internet import reactor, ssl, task
from autobahn.twisted.websocket import WebSocketClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol
import requests
import global_var
from functools import reduce
import struct
import numpy


def get_tokens():
    #1337
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Mobile Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
        'application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    
    
    
    
    
    response = requests.get('https://www.bet365.it/#/HO/',headers=headers)
    token = decryptToken(parseTokens(response.text))
    
    if response.status_code != requests.codes.ok and 'pstk' not in response.cookies and 'aps03' not in response.cookies:
        print('service not avaliable')
        return

    
    
    # headers['Referer'] = "https://www.bet365.it/"
    # headers['Referer'] = "https://www.bet365.it/"
    # print(f'success get pstk: {response.cookies["pstk"]}')
    
    print('Parsing sports configuration...')
    headers['Referer'] = "https://www.bet365.it/#/HO/"
    headers['Host'] = "www.bet365.it"
    headers['Cookie'] = f"mbs=3; aps03={response.cookies['aps03']}; session=processform=0"
    raw = requests.get("https://www.bet365.it/defaultapi/sports-configuration",headers=headers)
    config = json.loads(raw.text)
    
    data=  {
        "pstk": config['flashvars']['SESSION_ID'], #response.cookies['pstk'],
        "token":token,
        "aps03":response.cookies['aps03'],
        "SERVER_TIME": config['ns_weblib_util']['WebsiteConfig']['SERVER_TIME']
    }
    
    data['UID'] = generateUID(token,data['SERVER_TIME'])
    
    for key in data:
        print (f"{key}:{data[key]}")
    return data
    


def parseTokens(bodyText):
    #1337
    first_token_regex = r"(?<=d\[b\('0x0'\)\]=').*?(?=';)"
    second_token_regex = r"(?<=d\[b\('0x1'\)\]=').*?(?=';)"

    token_two = re.findall(first_token_regex, bodyText)[0]
    token_one = re.findall(second_token_regex, bodyText)[0]
    return token_one + "." + token_two


def generateUID(token,SERVER_TIME):
    #1337
    javascriptFunctions = ''
    r = base64.b64decode(token)
    s = len (r)
    a = []
    v = ""
    for _ in range(random.randint(16, 17)):
        v += str(random.randint(0, 9))
    for t in range(0,s):
        a.append(r[t])
    a = a[::-1]
    v = int(v)
    def bytes_to_int(bytes):
        result = 0
        for b in bytes:
            result = result * 256 + int(b)
        return result
    
    
    return int(bytes_to_int(a) - 10 + ( int(str(time.time())[0:17].replace('.','')) / pow(3,9) - SERVER_TIME )) | v
    


def decryptToken(t):
    #1337
    n = ""
    i = ""
    o = len(t)
    r = 0
    s = 0
    MAP_LEN = 64
    charMap = [["A", "d"], ["B", "e"], ["C", "f"], ["D", "g"], ["E", "h"], ["F", "i"], ["G", "j"], ["H", "k"], ["I", "l"], ["J", "m"], ["K", "n"], ["L", "o"], ["M", "p"], ["N", "q"], ["O", "r"], ["P", "s"], ["Q", "t"], ["R", "u"], ["S", "v"], ["T", "w"], ["U", "x"], ["V", "y"], ["W", "z"], ["X", "a"], ["Y", "b"], ["Z", "c"], ["a", "Q"], ["b", "R"], ["c", "S"], ["d", "T"], ["e", "U"], ["f", "V"], [
        "g", "W"], ["h", "X"], ["i", "Y"], ["j", "Z"], ["k", "A"], ["l", "B"], ["m", "C"], ["n", "D"], ["o", "E"], ["p", "F"], ["q", "0"], ["r", "1"], ["s", "2"], ["t", "3"], ["u", "4"], ["v", "5"], ["w", "6"], ["x", "7"], ["y", "8"], ["z", "9"], ["0", "G"], ["1", "H"], ["2", "I"], ["3", "J"], ["4", "K"], ["5", "L"], ["6", "M"], ["7", "N"], ["8", "O"], ["9", "P"], ["\n", ":|~"], ["\r", ""]]
    for r in range(0, o):
        n = t[r]
        for s in range(0, MAP_LEN):
            if ":" == n and ":|~" == t[r:3]:
                n = "\n"
                r = r + 2
                break
            if n == charMap[s][1]:
                n = charMap[s][0]
                break
        i = i+n
    return i


class DataSourceClientProtocol(WebSocketClientProtocol):

    def onClose(self, wasClean, code, reason):
        print(f'websocket close{reason}')

    def onOpen(self):
        #print('onOpen')
        global_var.ws_start_ti = int(time.time())
        #print(f"Global Token: {self.factory.token}")
        req = u'#\x03P\x01__time,S_{},D_{}\x00'.format(self.factory.session_id,self.factory.token).encode('utf-8')
        print (f'Sending message: {req}')
        self.sendMessage(req)

    def onMessage(self, payload, isBinary):
        global_var.receive_msg_ti = int(time.time())
        msg = payload.decode('utf-8')
        print(f'Messge: {msg}')
        if msg.startswith('100'):
            req = u'\x16\x00CONFIG_1_3,OVInPlay_1_3,Media_L1_Z3,XL_L1_Z3_C1_W3\x01'.encode(
                'utf-8')
            self.sendMessage(req)
            return

        msgs = msg.split('\x08')
        print(msgs)
        # reactor.callInThread(msg_handle, msgs)

    def send_cmd(self, cmd):
        reactor.callFromThread(self.sendMessage, cmd)


class DataSourceClientFactory(WebSocketClientFactory):
    protocol = DataSourceClientProtocol

    def buildProtocol(self, address):
        proto = WebSocketClientFactory.buildProtocol(self, address)

        self.connectedProtocol = proto
        return proto





def connect2WS(b_in_main_thread):
    tokens = get_tokens()
    pstk = tokens['pstk']
    token = tokens['token']
    uid = generateUID(token.split('.')[0],tokens['SERVER_TIME'])
    
    if not pstk:
        print('get pstk failed, maybe in maintance')
        return

    USER_AGENT = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Mobile Safari/537.36"
    url = 'wss://premws-pt1.bet365.it/zap/?uid={}'.format(uid)

    global_var.factory = DataSourceClientFactory(
        url, useragent=USER_AGENT, protocols=['zap-protocol-v1'])

    global_var.factory.session_id = pstk
    global_var.factory.token = token

    def accept(response):
        if isinstance(response, PerMessageDeflateResponse):
            return PerMessageDeflateResponseAccept(response)

    global_var.factory.setProtocolOptions(perMessageCompressionAccept=accept)
    global_var.factory.setProtocolOptions(perMessageCompressionOffers=[PerMessageDeflateOffer(
        accept_max_window_bits=True,
        accept_no_context_takeover=True,
        request_max_window_bits=0,
        request_no_context_takeover=True
    )])

    if global_var.factory.isSecure:
        contextFactory = ssl.ClientContextFactory()
    else:
        contextFactory = None

    while True:
        try:
            if b_in_main_thread:
                connectWS(global_var.factory, contextFactory, timeout=60)
            else:
                reactor.callFromThread(
                    connectWS, global_var.factory, contextFactory, timeout=60)
        except:
            print('failed to connect ws server!')
            time.sleep(5)
        else:
            break


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    try:
        if global_var.factory and hasattr(global_var.factory, 'connectedProtocol') and \
                global_var.factory.connectedProtocol.state == WebSocketProtocol.STATE_OPEN:
            global_var.factory.connectedProtocol.dropConnection(abort=True)

        reactor.stop()
    except:
        sys.exit(0)


def repeat_task():
    cur_ti = int(time.time())

    print(
        f'repeat task global_var.receive_msg_ti = {time.ctime(global_var.receive_msg_ti)}')

    if global_var.receive_msg_ti != 0 and cur_ti - global_var.receive_msg_ti > 25:
        print(
            f'lost msg... drop connection... total ti = {int(time.time()) - global_var.ws_start_ti}')

        if global_var.factory and hasattr(global_var.factory, 'connectedProtocol') and \
                global_var.factory.connectedProtocol.state == WebSocketProtocol.STATE_OPEN:
            global_var.factory.connectedProtocol.dropConnection(abort=True)

        reactor.stop()

    if cur_ti - global_var.up_ti > 40 and global_var.ws_start_ti == 0:
        print(f'start not ok!!!')

        if global_var.factory and hasattr(global_var.factory, 'connectedProtocol') and \
                global_var.factory.connectedProtocol.state == WebSocketProtocol.STATE_OPEN:
            global_var.factory.connectedProtocol.dropConnection(abort=True)

        reactor.stop()


def main():
    global_var.up_ti = int(time.time())
    global_var.loop_task = task.LoopingCall(repeat_task)
    global_var.loop_task.start(1, now=False)
    reactor.suggestThreadPoolSize(50)
    connect2WS(True)
    signal.signal(signal.SIGINT, signal_handler)
    reactor.run()


if __name__ == '__main__':
    main()
