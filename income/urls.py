# urls.py
from django.urls import path
from .views import income_list, income_detail, income_create, income_edit, income_delete, monthly_income_view

app_name = 'income' 

urlpatterns = [
    path('', income_list, name='income_list'),
    path('<int:pk>/', income_detail, name='income_detail'),
    path('edit/<int:pk>/', income_edit, name='income_edit'),
    path('new/', income_create, name='income_create'),
    path('monthly-income/', monthly_income_view, name='monthly_income'),
    path('delete/<int:pk>/', income_delete, name='income_delete'),
]
