from django.urls import path
from . import views

urlpatterns = [
    path('', views.PractitionerListView.as_view(), name='practitioner-list'),
    path('<str:fhir_id>/', views.PractitionerDetailView.as_view(), name='practitioner-detail'),
]
