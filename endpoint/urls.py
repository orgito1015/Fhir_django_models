from django.urls import path
from . import views

urlpatterns = [
    path('', views.EndpointListView.as_view(), name='endpoint-list'),
    path('<str:fhir_id>/', views.EndpointDetailView.as_view(), name='endpoint-detail'),
]
