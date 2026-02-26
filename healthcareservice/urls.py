from django.urls import path
from . import views

urlpatterns = [
    path('', views.HealthcareServiceListView.as_view(), name='healthcareservice-list'),
    path('<str:fhir_id>/', views.HealthcareServiceDetailView.as_view(), name='healthcareservice-detail'),
]
