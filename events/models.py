from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    """An event with capacity limits."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_participants = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    """A role within an event (e.g. Attendee, Speaker) with optional capacity."""
    name = models.CharField(max_length=100)
    max_capacity = models.PositiveIntegerField(null=True, blank=True)  # null = unlimited
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='roles')

    def __str__(self):
        return f"{self.name} ({self.event.name})"


class Registration(models.Model):
    """A user's registration for an event, optionally with a role."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"
