from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Event, Registration, Role, EventCategory
from .forms import EventForm, UserRegistrationForm


def home(request):
    return render(request, 'events/home.html')


@login_required
def dashboard(request):
    total_events = Event.objects.count()
    total_registrations = Registration.objects.filter(user=request.user).count()
    upcoming = Registration.objects.filter(user=request.user, event__start_date__gte=timezone.now()).select_related('event').order_by('event__start_date')[:5]
    recent_events = Event.objects.filter(status='published').order_by('-created_at')[:5]
    return render(request, 'events/dashboard.html', {
        'total_events': total_events,
        'total_registrations': total_registrations,
        'upcoming': upcoming,
        'recent_events': recent_events,
    })


class CustomLoginView(LoginView):
    template_name = 'events/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')


class RegisterView(FormView):
    form_class = UserRegistrationForm
    template_name = 'events/register.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Account created successfully!')
        return redirect('dashboard')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('events_home')


@login_required
def profile(request):
    return render(request, 'events/profile.html')


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        qs = Event.objects.filter(status='published').select_related('category').annotate(
            reg_count=Count('registrations')
        ).order_by('-start_date')
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        status = self.request.GET.get('status')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if category and category.isdigit():
            qs = qs.filter(category_id=int(category))
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = EventCategory.objects.all()
        context['search_q'] = self.request.GET.get('q', '')
        try:
            context['filter_category'] = int(self.request.GET.get('category', 0)) or None
        except (ValueError, TypeError):
            context['filter_category'] = None
        return context


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


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user if self.request.user.is_authenticated else None
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    context_object_name = 'event'
    success_url = reverse_lazy('event_list')


class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    context_object_name = 'event'
    success_url = reverse_lazy('event_list')


@login_required
def my_events(request):
    registrations = Registration.objects.filter(user=request.user).select_related('event', 'role').order_by('-registered_at')
    return render(request, 'events/my_events.html', {'registrations': registrations})


class CustomPasswordResetView(PasswordResetView):
    template_name = 'events/password_reset.html'
    email_template_name = 'events/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'events/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'events/password_reset_confirm.html'
    success_url = reverse_lazy('login')