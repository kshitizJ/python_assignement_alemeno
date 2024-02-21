from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_customer),
    path('check-eligibility/', views.check_eligibility),
    path('view-loans/<int:customer_id>/', views.view_loans_by_customer),
]