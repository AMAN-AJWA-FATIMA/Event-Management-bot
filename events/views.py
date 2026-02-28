from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Event
from .forms import EventForm


def home(request):
    return render(request, 'events/home.html')


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    ordering = ['-start_date']


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')


class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    context_object_name = 'event'
    success_url = reverse_lazy('event_list')