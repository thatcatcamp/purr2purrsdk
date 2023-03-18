"""
copyright (c) 2023 CAT Camp

copyright is just included for takedowns if this is used for commercial projects
DONT PANIC :)

this file is provided under the gplv3 license -see the full legal text in the project

use this if you have an artwork controller that can't be directly contacted from the
lidar and nfc modules (i.e. - a different box or unsupported languages.  we use this to
proxy from python to a chromium-based app in a sandbox (only http? supported)

from shell - you can push events in with:

curl -X POST http://localhost:8080/push
   -H 'Content-Type: application/json'
   -d '{"eventtype":"hooman","hooman_id":"", "hooman_name":"", "hooman_likes":""}'
"""
import hashlib
import os
import pathlib
import time
import cherrypy
import queue

# change to 0.0.0.0 if need to jump boxes - this is accessible only here
TALK_ON="127.0.0.1"
# change to something meaningful if have multiple
PING_RESPONSE = "ipcproxy 1.0"
Q = queue.Queue()
CACHE = "./cache/"

class IPCProxy(object):

    @cherrypy.expose
    def index(self):
        return PING_RESPONSE

    @cherrypy.expose
    def push(self):
        print('push')
        body = cherrypy.request.body.read().decode('utf-8')
        print(body)
        # no validation
        Q.put(body)
        print("pushed")

    @cherrypy.expose
    def say(self):
        body = cherrypy.request.body.read().decode('utf-8').replace("'", "").replace("\"", "")
        print("say: ", body)
        """
        all the default voices are horrendous - the requirements should install this, otherwise run:

        pip3 install -f 'https://synesthesiam.github.io/prebuilt-apps/' -f 'https://download.pytorch.org/whl/cpu/torch_stable.html' larynx

        alternatively - festival is tolerable - but this caching method works better on slow hw
        """
        # exec = f"festival -b '(voice_cmu_us_slt_arctic_hts)' '(SayText \"{body}\")'"
        try:
            os.mkdir(CACHE)
        except:
            pass
        key = hashlib.sha1(body.encode('utf-8')).hexdigest() + ".wav"
        if not pathlib.Path(os.path.join(CACHE, key)).is_file():
            print("creating")
            exec = f"larynx --voice harvard '{body}' > {pathlib.Path(os.path.join(CACHE, key))}"
            os.system(exec)
        print("playing")
        exec = f"aplay < {pathlib.Path(os.path.join(CACHE, key))}"
        os.system(exec)

    @cherrypy.expose
    def events(self):
        # throttle for small cpus
        if Q.empty():
            time.sleep(2)
            return ""
        event = str(Q.get(block=False)).encode('utf-8')
        if event is None or len(event) == 0:
            time.sleep(2)
            return ""
        print("events: ", event)
        time.sleep(1)
        return str(event)


conf = {
    '/': {
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'text/json'), ('Access-Control-Allow-Origin', '*')],
        'server.socket_host': 'localhost',
        'server.socket_port': 8080
    }
}

cherrypy.quickstart(IPCProxy(), '/', conf)
