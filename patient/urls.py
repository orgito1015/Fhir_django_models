from django.urls import path
from . import views

urlpatterns = [
    path('', views.PatientListView.as_view(), name='patient-list'),
    path('<str:fhir_id>/', views.PatientDetailView.as_view(), name='patient-detail'),
]
