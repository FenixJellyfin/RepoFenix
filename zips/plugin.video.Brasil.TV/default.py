# -*- coding: utf-8 -*-
import os
import binascii
import six
from lib.helper import *
from lib import xtream


_v01 = "5b434f4c4f52206c696d655d2d5b2f434f4c4f525d205b434f4c4f5279656c6c6f775d42524153494c2054565b2f434f4c4f525d205b434f4c4f52206c696d655d2d5b2f434f4c4f525d"
_v02 = "68747470733a2f2f7261772e67697468756275736572636f6e74656e742e636f6d2f547567615465616d766f642f726574696d652d666f74655832362f726566732f68656164732f6d61696e2f6368616e6e656c732e6a736f6e"

def _decode(data):
    return binascii.unhexlify(data).decode('utf-8')

TITULO = _decode(_v01)
API_CHANNELS = _decode(_v02)

# Inicialização do Perfil
if not exists(profile):
    try:
        os.mkdir(profile)
    except:
        pass

IPTV_PROBLEM_LOG = translate(os.path.join(profile, 'iptv_problems_log.txt'))

@route('/')
def index():
    addMenuItem({'name': TITULO, 'description': ''}, destiny='')
    # Menu principal focado na lista Brasil
    addMenuItem({'name': 'LISTAS IPTV BRASIL', 'description': 'Aceder aos servidores do Brasil'}, destiny='/playlistiptv')
    end()
    setview('WideList')

@route('/playlistiptv')
def playlistiptv(): 
    # O link é descodificado apenas no momento do pedido
    iptv = xtream.parselist(API_CHANNELS)
    if iptv:
        for n, (dns, username, password) in enumerate(iptv):
            n = n + 1
            addMenuItem({'name': 'LISTA {0}'.format(str(n)), 'description': 'Servidor IPTV {0}'.format(str(n)), 'dns': dns, 'username': str(username), 'password': str(password)}, destiny='/cat_channels')
        end()
        setview('WideList') 
    else:
        notify('Sem lista iptv disponível') 

@route('/cat_channels')
def cat_channels(param):
    dns = param['dns']
    username = param['username']
    password = param['password']
    cat = xtream.API(dns,username,password).channels_category()
    if cat:
        for i in cat:
            name, url = i
            addMenuItem({'name': name, 'description': '', 'dns': dns, 'username': str(username), 'password': str(password), 'url': url}, destiny='/open_channels')
        end()
        setview('WideList')
    else:
        url_problem = '{0}/get.php?username={1}&password={2}\n'.format(dns,username,password)
        
        if six.PY2:
            import io
            open_file = lambda filename, mode: io.open(filename, mode, encoding='utf-8')
        else:
            open_file = lambda filename, mode: open(filename, mode, encoding='utf-8')
        
        check = False
        if exists(IPTV_PROBLEM_LOG):
            with open(IPTV_PROBLEM_LOG, "r") as arquivo:
                if url_problem in arquivo.read():
                    check = True
        
        with open_file(IPTV_PROBLEM_LOG, "a") as arquivo:
            if not check:
                arquivo.write(url_problem)
        notify('Lista Offline')

@route('/open_channels')
def open_channels(param):
    dns = param['dns']
    username = param['username']
    password = param['password']
    url = param['url'] 
    open_ = xtream.API(dns,username,password).channels_open(url)
    if open_:
        setcontent('movies')
        for i in open_:
            name,link,thumb,desc = i
            addMenuItem({'name': name, 'description': desc, 'iconimage': thumb, 'url': link}, destiny='/play_iptv', folder=False)
        end()
        setview('List')
    else:
        notify('Opção indisponível')

@route('/play_iptv')
def play_iptv(param):
    name = param['name']
    description = param['description']
    iconimage = param['iconimage']
    url = param['url']
    # Reprodução via f4mTester
    plugin = 'plugin://plugin.video.f4mTester/?streamtype=HLSRETRY&name=' + quote_plus(str(name)) + '&iconImage=' + quote_plus(str(iconimage)) + '&thumbnailImage=' + quote_plus(str(iconimage)) + '&description=' + quote_plus(description) + '&url=' + quote_plus(url)
    xbmc.executebuiltin('RunPlugin(%s)' % plugin)