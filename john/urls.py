from django.urls import path
from . import views


app_name = 'john'  

urlpatterns = [
    path("", views.dashboard, name="dashboard"), 
    path("bills/", views.bill_list, name="bill_list"),
    path("bills/paid/", views.paid_bills, name="paid_bills"),
    path("bills/new/", views.bill_create, name="bill_create"),
    path("bills/<int:pk>/", views.bill_detail, name="bill_detail"),
    path("bills/<int:pk>/edit/", views.bill_edit, name="bill_edit"),
    path("bills/<int:pk>/pay/", views.pay_bill, name="pay_bill"),
    path("time/", views.time_entries, name="time_entries"),
    path("time/new/", views.time_entry_create, name="time_entry_create"),
    path("mileage/", views.mileage_entries, name="mileage_entries"),
    path("mileage/new/", views.mileage_entry_create, name="mileage_entry_create"),
    path("reports/summary/", views.monthly_summary, name="monthly_summary"),
]

