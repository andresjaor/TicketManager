import uuid

from django.db import models
from django.contrib.auth.models import User


class TicketState(models.TextChoices):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.CharField()
    external_id = models.UUIDField(db_index=True, default=uuid.uuid4)
    status = models.CharField(choices=TicketState.choices, default=TicketState.CREATED)
    num_of_images = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    @property
    def images(self):
        return TicketImages.objects.filter(ticket=self.pk).all()

    def update_state(self, state: TicketState):
        self.status = state
        self.save()

    def __str__(self):
        return f"ID: {self.external_id}"


class TicketImageState(models.TextChoices):
    CREATED = "CREATED"
    UPLOADING = "UPLOADING"
    DONE = "DONE"


class TicketImages(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    image_name = models.CharField()
    image_uri = models.URLField()
    status = models.CharField(choices=TicketImageState.choices, default=TicketImageState.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_state(self, state: TicketImageState):
        self.status = state
        self.save()

    def __str__(self):
        return f"<{self.image_name} - {self.status}>"

