from django.urls import path

from tickets import views

urlpatterns = [
    path('user/', views.UserResource.as_view()),
    path('ticket/', views.TicketResource.as_view()),
    path('ticket/<uuid:ticket_id>/upload/', views.ImageUploadResource.as_view()),
]