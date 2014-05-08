import uuid
import tornado.websocket


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """
    simple websocket server for bidirectional communication between client and server
    """
    
    # public means non authenticated
    # private means authenticated
    channels = {
        'public': {},
        'private': {}
    }
    
    def send_message(self, *args):
        """ alias to write_message """
        self.write_message(*args)
    
    def add_client(self, user_id=None):
        """
        Adds current instance to public or private channel.
        If user_id is specified it will be added to the private channel,
        If user_id is not specified it will be added to the public one instead.
        """
        if user_id is None:
            # generate a random uuid if it's an unauthenticated client
            self.channel = 'public'
            user_id = uuid.uuid1().hex
        else:
            self.channel = 'private'
        
        self.id = user_id
        self.channels[self.channel][self.id] = self
        print 'Client connected to the %s channel.' % self.channel
    
    def remove_client(self):
        """ removes a client """
        del self.channels[self.channel][self.id]
    
    @classmethod
    def broadcast(cls, message):
        """ broadcast message to all connected clients """
        clients = cls.get_clients()
        # loop over every client and send message
        for id, client in clients.iteritems():
            client.send_message(message)
    
    @classmethod
    def send_private_message(self, user_id, message):
        """
        Send a message to a specific client.
        Returns True if successful, False otherwise
        """
        try:
            client = self.channels['private'][str(user_id)]
        except KeyError:
            print '====debug===='
            print self.channels['private']
            print 'client with id %s not found' % user_id
            return False
        
        client.send_message(message)
        print 'message sent to client #%s' % user_id
        return True
    
    @classmethod
    def get_clients(self):
        """ return a merge of public and private clients """
        public = self.channels['public']
        private = self.channels['private']
        return dict(public.items() + private.items())
    
    def open(self):
        """ method which is called every time a new client connects """
        print 'Connection opened.'
        
        # retrieve user_id if specified
        user_id = self.get_argument("user_id", None)
        # add client to list of connected clients
        self.add_client(user_id)
        # welcome message
        self.send_message("Welcome to nodeshot websocket server.")
        # new client connected message
        client_count = len(self.get_clients().keys())
        new_client_message = 'New client connected, now we have %d %s!' % (client_count, 'client' if client_count <= 1 else 'clients')
        # broadcast new client connected message to all connected clients
        self.broadcast(new_client_message)
        
        print self.channels['private']

    def on_message(self, message):
        """ method which is called every time the server gets a message from a client """
        if message == "help":
            self.send_message("Need help, huh?")
        print 'Message received: \'%s\'' % message

    def on_close(self):
        """ method which is called every time a client disconnects """
        print 'Connection closed.'
        self.remove_client()
        
        client_count = len(self.get_clients().keys())
        new_client_message = '1 client disconnected, now we have %d %s!' % (client_count, 'client' if client_count <= 1 else 'clients')
        self.broadcast(new_client_message)
