from django.contrib import admin
from tickets import models


class TicketImageAdmin(admin.StackedInline):
    model = models.TicketImages
    extra = 1


class TicketAdmin(admin.ModelAdmin):
    inlines = [TicketImageAdmin]


admin.site.register(models.Ticket, TicketAdmin)