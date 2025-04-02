# api/serializers.py
from rest_framework import serializers
from rooms.models import Room

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'created_at']