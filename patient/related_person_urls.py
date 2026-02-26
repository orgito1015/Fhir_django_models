from django.urls import path
from . import views

urlpatterns = [
    path('', views.RelatedPersonListView.as_view(), name='relatedperson-list'),
    path('<str:fhir_id>/', views.RelatedPersonDetailView.as_view(), name='relatedperson-detail'),
]
