from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Registration, Role
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registrations'] = self.object.registrations.select_related('user', 'role')
        context['is_registered'] = False
        if self.request.user.is_authenticated:
            context['is_registered'] = self.object.registrations.filter(user=self.request.user).exists()
        return context


@login_required
def register_for_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        current_count = event.registrations.count()
        if current_count >= event.max_participants:
            messages.warning(request, 'This event is full. Cannot register.')
            return redirect('event_detail', pk=pk)
        role_id = request.POST.get('role')
        role = None
        if role_id:
            role = Role.objects.filter(pk=role_id, event=event).first()
            if role and role.max_capacity:
                role_count = Registration.objects.filter(event=event, role=role).count()
                if role_count >= role.max_capacity:
                    messages.warning(request, f'Role "{role.name}" is full.')
                    return redirect('event_detail', pk=pk)
        if Registration.objects.filter(user=request.user, event=event).exists():
            messages.warning(request, 'You are already registered.')
        else:
            Registration.objects.create(user=request.user, event=event, role=role)
            messages.success(request, 'Successfully registered!')
        return redirect('event_detail', pk=pk)
    return redirect('event_detail', pk=pk)


@login_required
def unregister_for_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    Registration.objects.filter(user=request.user, event=event).delete()
    messages.success(request, 'You have unregistered from this event.')
    return redirect('event_detail', pk=pk)


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