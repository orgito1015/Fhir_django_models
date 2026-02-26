from django.urls import path
from . import views

urlpatterns = [
    path('', views.LocationListView.as_view(), name='location-list'),
    path('<str:fhir_id>/', views.LocationDetailView.as_view(), name='location-detail'),
]
