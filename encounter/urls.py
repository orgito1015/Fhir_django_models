from django.urls import path
from . import views

urlpatterns = [
    path('', views.EncounterListView.as_view(), name='encounter-list'),
    path('<str:fhir_id>/', views.EncounterDetailView.as_view(), name='encounter-detail'),
]
