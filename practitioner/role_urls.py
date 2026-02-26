from django.urls import path
from . import views

urlpatterns = [
    path('', views.PractitionerRoleListView.as_view(), name='practitionerrole-list'),
    path('<str:fhir_id>/', views.PractitionerRoleDetailView.as_view(), name='practitionerrole-detail'),
]
