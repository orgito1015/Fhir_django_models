from django.urls import path
from . import views

urlpatterns = [
    path('', views.ObservationListView.as_view(), name='observation-list'),
    path('<str:fhir_id>/', views.ObservationDetailView.as_view(), name='observation-detail'),
]
