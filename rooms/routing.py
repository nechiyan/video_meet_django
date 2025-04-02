# rooms/routing.py
from django.urls import re_path
from rooms.consumers import SignalingConsumer

websocket_urlpatterns = [
    re_path(r'ws/signaling/(?P<room_id>[^/]+)/$', SignalingConsumer.as_asgi()),
]