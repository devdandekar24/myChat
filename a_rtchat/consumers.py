from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from .models import *
import json

# channels on serverside and websockets in client-side
# The channel layer is a message bus system (like a post office) that lets different parts of your application talk to each other.
# group_add(group_name, channel_name): subscribes a specific connection
# group_discard(group_name, channel_name): removes a connection from a group
# group_send(group_name, event_dictionary): the most important one for broadcasting. It sends a message (an event) to all connections subscribed to a group

class ChatroomConsumer(WebsocketConsumer):
    # called when user joins a chatroom
    def connect(self):
        # getting currently authenticated user
        self.user = self.scope['user']
        # extracts chatroom_name from websocket url route passed through routing.py
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name'] 
        # fetches chatgroup instance from databse
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)
        # async_to_sync :  special wrapper function that acts as a bridge from the synchronous world to the asynchronous world
        # self.channel_layer.group_add : tell the channel layer, "Please add the current user's connection (self.channel_name) to the group named self.chatroom_name
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )
        # add and update online users
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()
        # accepts the websocket connection
        self.accept()
        
    # This method is automatically called by Django Channels whenever a client's 
    # # 'close_code' is a number indicating why the connection was closed.
    def disconnect(self,close_code):
        async_to_sync(self.channel_layer.group_discard)(
            # The first argument is the name of the group to leave
            self.chatroom_name, 
            # The second argument is the unique ID for this specific connection.
            self.channel_name
        )
        
        # remove and update online users
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()
    
    def receive(self, text_data):
        # takes incoming data and extracts the message body
        #  converts the JSON string into a Python dictionary
        # pls note htmx does not send JSON by default but , When used with ws-send, HTMX actually serializes the form into JSON — not classic x-www-form-urlencoded
        text_data_json = json.loads(text_data)
        # extract the actual message
        body = text_data_json['body']
        # saves message to the database
        message = GroupMessage.objects.create(
            body = body,
            author = self.user, 
            group = self.chatroom 
        )
        # prepares an event to broadcast the new message.
        event = {
            'type':'message_handler',
            'message_id':message.id,
        }
        # Sends the event to everyone in the chatroom using Django Channels' group_send
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )
        
    # method is called when a WebSocket group event is received. It fetches a message from the database and sends it as HTML to the client (browser)    
    def message_handler(self, event):
        message_id=event['message_id']
        message=GroupMessage.objects.get(id=message_id)
        # Prepares the context for rendering an HTML template.
        context = {
            'message':message,
            'user':self.user,
        }
        # render_to_string(...) returns the HTML snippet as a string.
        # self.send(...) pushes that string to the browser over WebSocket
        html = render_to_string("a_rtchat/partials/chat_message_p.html",context=context)
        self.send(text_data=html)
        
    def update_online_count(self):
        online_count = self.chatroom.users_online.count()-1
        # prepares an event to broadcast the new message.
        event={
            'type':'online_count_handler',
            'online_count':online_count
        }
        async_to_sync(self.channel_layer.group_send)(self.chatroom_name, event)
        
    def online_count_handler(self, event):
        online_count = event['online_count']
        context={
            'online_count':online_count,
            'chat_group':self.chatroom,
        }
        html = render_to_string("a_rtchat/partials/online_count.html",context)
        self.send(text_data=html)
        
# setting online status of users 
class OnlineStatusConsumer(WebsocketConsumer):
    def connect(self):
        # self.scope is like request in Django views
        # self.user will hold the logged-in User object, just like request.user in normal Django views
        # but You must have Django’s AuthMiddlewareStack enabled in your Channels ASGI setup
        self.user = self.scope['user']
        self.group_name = 'online-status'
        # self.group = get_object_or_404(ChatGroup, group_name=self.group_name)
        self.group, created = ChatGroup.objects.get_or_create(group_name=self.group_name)

        if self.user not in self.group.users_online.all():
            self.group.users_online.add(self.user)
            
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )
            
        self.accept()
        # calls our own defined online_status method
        self.online_status()
        
    def disconnect(self, close_code):
        #  Removes the user from the users_online field of the group.
        self.group.users_online.remove(self.user)
        # Removes the WebSocket channel from the group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )
        # again send update to online_status
        self.online_status()
        
    def online_status(self):
        # creates event 
        event={
            'type':'online_status_handler'
        }
        # broadcast the event to the group
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, event
        )
        
    def online_status_handler(self, event):
        # get the public-chat group
        # get all online users except the current user
        public_chat = ChatGroup.objects.get(group_name='public-chat')
        public_chat_users = public_chat.users_online.exclude(id=self.user.id)
        # get all chats that current user is member of
        my_chats = self.user.chat_groups.all()
          
        # same goes for group chat
        group_chats = []
        # for chat in my_chats.filter(groupchat_name__isnull=False):
        for chat in my_chats.filter(groupchat_name__isnull=False).exclude(groupchat_name="Me"):
            other_online = chat.users_online.exclude(id=self.user.id)
            chat.online_count = other_online.count()
            group_chats.append(chat)
            
        # check if other user is online and if online get count and store it in private_chats list
        private_chats = []
        for chat in my_chats.filter(is_private=True):
            other_online = chat.users_online.exclude(id=self.user.id)
            chat.online_count = other_online.count()
            private_chats.append(chat)

        context = {
            'public_chat_users': public_chat_users,
            'private_chats': private_chats,
            'group_chats': group_chats,
            'user': self.user
        }
        # Renders the HTML for online status using a template
        # Sends it to the client over WebSocket
        html = render_to_string("a_rtchat/partials/online_status.html", context=context)
        self.send(text_data=html)
    
    # def online_status_handler(self, event):
    #     public_chat = ChatGroup.objects.get(group_name='public-chat')
    #     public_chat_users = public_chat.users_online.exclude(id=self.user.id)

    #     my_chats = self.user.chat_groups.all()

    #     private_chats = []
    #     group_chats = []

    #     for chat in my_chats:
    #         other_online = chat.users_online.exclude(id=self.user.id)
    #         chat.online_count = other_online.count()

    #         if chat.groupchat_name == "Me" or chat.is_private:
    #             private_chats.append(chat)
    #         elif chat.groupchat_name:
    #             group_chats.append(chat)

    #     context = {
    #         'public_chat_users': public_chat_users,
    #         'private_chats': private_chats,
    #         'group_chats': group_chats,
    #         'user': self.user
    #     }

    #     html = render_to_string("a_rtchat/partials/online_status.html", context=context)
    #     self.send(text_data=html)
