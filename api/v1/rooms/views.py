# api/views.py
from rest_framework import generics
from rooms.models import Room
from .serializers import RoomSerializer, RoomDetailSerializer

class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class RoomDetailView(generics.RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomDetailSerializer
    lookup_field = 'id'