from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='events_home'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/new/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_edit'),
    path('events/<int:pk>/register/', views.register_for_event, name='event_register'),
    path('events/<int:pk>/unregister/', views.unregister_for_event, name='event_unregister'),
]