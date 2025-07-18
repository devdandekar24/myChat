from django.urls import path
from .consumers import *

# the consumers file is equivalent to the views.py file

websocket_urlpatterns = [
    path('ws/chatroom/<chatroom_name>',ChatroomConsumer.as_asgi()),
]