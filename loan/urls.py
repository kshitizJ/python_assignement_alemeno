from django.urls import path
from . import views

urlpatterns = [
    path('create-loan/', views.create_loan),
    path('view-loan/<int:loan_id>/', views.view_loan_details),
]