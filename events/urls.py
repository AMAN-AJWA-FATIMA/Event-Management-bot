from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='events_home'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/new/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_edit'),
]