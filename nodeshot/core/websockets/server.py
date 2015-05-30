import time
import simplejson as json
from threading import Thread

import tornado.web
import tornado.ioloop

from .handlers import WebSocketHandler
from . import ADDRESS, PORT, PUBLIC_PIPE, PRIVATE_PIPE  # contained in __init__.py


application = tornado.web.Application([
    (r'/', WebSocketHandler),
])


def public_broadcaster():
    """
    Thread which runs in parallel and constantly checks for new messages
    in the public pipe and broadcasts them publicly to all connected clients.
    """
    while __websocket_server_running__:
        pipein = open(PUBLIC_PIPE, 'r')
        line = pipein.readline().replace('\n', '').replace('\r', '')
        if line != '':
            WebSocketHandler.broadcast(line)
            print line
            
            remaining_lines = pipein.read()
            pipein.close()
            pipeout = open(PUBLIC_PIPE, 'w')
            pipeout.write(remaining_lines)
            pipeout.close()
        else:
            pipein.close()
        
        time.sleep(0.05)

public_broadcaster_thread = Thread(target=public_broadcaster, args=[])
public_broadcaster_thread.deamon = True


def private_messenger():
    """
    Thread which runs in parallel and constantly checks for new messages
    in the private pipe and sends them to the specific client.
    If client is not connected the message is discarded.
    """
    while __websocket_server_running__:
        pipein = open(PRIVATE_PIPE, 'r')
        line = pipein.readline().replace('\n', '').replace('\r', '')
        if line != '':
            message = json.loads(line)
            WebSocketHandler.send_private_message(user_id=message['user_id'],
                                                  message=message)
            print line
            
            remaining_lines = pipein.read()
            pipein.close()
            pipeout = open(PRIVATE_PIPE, 'w')
            pipeout.write(remaining_lines)
            pipeout.close()
        else:
            pipein.close()
        
        time.sleep(0.05)

private_messenger_thread = Thread(target=private_messenger, args=[])
private_messenger_thread.deamon = True


def start():    
    global __websocket_server_running__
    __websocket_server_running__ = True
    
    application.listen(PORT, address=ADDRESS)
    websocktserver = tornado.ioloop.IOLoop.instance()
    
    try:
        print "\nStarted Tornado Wesocket Server at ws://%s:%s\n" % (ADDRESS, PORT)
        
        public_broadcaster_thread.start()
        private_messenger_thread.start()
        websocktserver.start()
    # on exit
    except (KeyboardInterrupt, SystemExit):
        __websocket_server_running__ = False
        websocktserver.stop()
        
        print "\nStopped Tornado Wesocket Server\n"
