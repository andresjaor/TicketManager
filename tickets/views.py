import base64
import logging
import pathlib
import time
import uuid

from typing import Dict
from datetime import datetime

import django.db.utils

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from tickets import models, serializer, tasks

_logger = logging.getLogger(__name__)


class UserResource(APIView):
    """
    Api to manage users
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        user_serializer = serializer.UserSerializer(data=request.data)
        if user_serializer.is_valid():
            try:
                user_serializer.save()
            except django.db.utils.IntegrityError:
                return Response({"error": "user already exists, please login."},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketResource(APIView, PageNumberPagination):
    """
    Api to manage tickets
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        user = request.user
        try:
            filters: Dict = self._build_filters(request.query_params)
        except Exception as e:
            return Response(repr(e), status=status.HTTP_400_BAD_REQUEST)
        print(filters)
        query = models.Ticket.objects.filter(
            user=user,
            **filters
        ).order_by('-created_at').all()
        results = self.paginate_queryset(query, request, view=self)
        serialized_data = serializer.TicketSerializer(results, many=True)
        return self.get_paginated_response(serialized_data.data)

    def post(self, request: Request):
        ticket_serializer = serializer.TicketSerializer(data=request.data)
        if ticket_serializer.is_valid():
            new_ticket = ticket_serializer.save(user=request.user)
            response_data = serializer.TicketSerializer(new_ticket)
            return Response(response_data.data, status=status.HTTP_201_CREATED)

        return Response(ticket_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _build_filters(filters: Dict) -> Dict:
        cleaned_filters = {}
        for key in filters.keys():
            if key == "ticket_id":
                cleaned_filters["external_id"] = uuid.UUID(filters[key], version=4)
            elif key == "from_date":
                cleaned_filters["created_at__gte"] = datetime.fromisoformat(filters[key])
            elif key == "to_date":
                cleaned_filters["created_at__lte"] = datetime.fromisoformat(filters[key])
            else:
                cleaned_filters[key] = filters[key]

        return cleaned_filters


class ImageUploadResource(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request: Request, ticket_id: str):
        try:
            ticket = models.Ticket.objects.get(user=request.user, external_id=ticket_id)
        except models.Ticket.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if self._is_ticket_images_quota_completed(ticket):
            return Response({"error": "All ticket images are already uploaded or in progress"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not request.data.get('b64_image'):
            return Response({"error": "No image stream was received"},
                            status=status.HTTP_400_BAD_REQUEST)
        file_path = settings.TEMP_FILE_DIR + f"/{int(time.time_ns() / 1000)}_{request.data['image_name']}"
        image_bytes = (base64.b64decode(request.data['b64_image']))

        with open(file_path, 'wb') as image:
            image.write(image_bytes)

        ticket_image = models.TicketImages.objects.create(
            ticket=ticket,
            image_name=request.data['image_name']
        )
        tasks.upload_image_to_server.delay(file_path,
                                           ticket_image.pk)

        return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def _is_ticket_images_quota_completed(ticket: models.Ticket):
        return models.TicketImages.objects.filter(ticket=ticket).count() >= ticket.num_of_images
