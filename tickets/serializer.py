import time

import primitives as primitives
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers

from tickets import models


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    username = serializers.EmailField(read_only=True)

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        validated_data["username"] = validated_data["email"].split('@')[0]
        return User.objects.create_user(**validated_data)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TicketImages
        fields = ["image_name", "status", "image_uri"]


class TicketSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    num_of_images = serializers.IntegerField(required=True)
    ticket_id = serializers.CharField(read_only=True, source='external_id')
    status = serializers.ChoiceField(choices=models.TicketState.choices, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    images = ImageSerializer(
        many=True,
        read_only=True,
     )

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        return models.Ticket.objects.create(**validated_data)