import os

from ticket_manager import celery_app
from tickets import models
from tickets.cloudinary import upload_image
from django.db import transaction


@celery_app.task(name="upload_image_to_server", bind=True, max_retries=3)
def upload_image_to_server(self, file_path: str, ticket_image_id: int):
    print(f"Uploading image {file_path}")
    ticket_image: models.TicketImages = models.TicketImages.objects.get(pk=ticket_image_id)
    ticket: models.Ticket = ticket_image.ticket

    if ticket.status == models.TicketState.CREATED:
        ticket.update_state(models.TicketState.IN_PROGRESS)

    if ticket_image.status == models.TicketImageState.CREATED:
        ticket_image.update_state(models.TicketImageState.UPLOADING)

    try:
        ticket_image.image_uri = _upload_image(file_path)
        ticket.save()
        ticket_image.update_state(models.TicketImageState.DONE)
    except Exception as e:
        print(f"Error uploading image {repr(e)}")
        self.retry(countdown=3**self.request.retries)

    _delete_temp_file(file_path)

    if ticket_is_completed(ticket):
        ticket.update_state(models.TicketState.DONE)


def _upload_image(file_path: str) -> str:
    cloudinary_image = upload_image(file_path)
    print(cloudinary_image.url)
    return cloudinary_image.url


def _delete_temp_file(file_path: str) -> None:
    try:
        os.remove(file_path)
    except FileNotFoundError:
        ...


def ticket_is_completed(ticket: models.Ticket) -> bool:
    return models.TicketImages.objects.filter(
        ticket=ticket,
        status=models.TicketImageState.DONE
    ).count() == ticket.num_of_images

