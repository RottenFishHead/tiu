from django.urls import path
from .views import add_hand, edit_hand, delete_hand, hand_detail, send_mail_to_all, sessison_hands_list

app_name = 'hands'  

urlpatterns = [
    path('<int:session_id>/add/', add_hand, name='add_hand'),
    path('<int:hand_id>/edit/', edit_hand, name='edit_hand'),
    path('<int:hand_id>/delete/', delete_hand, name='delete_hand'),
    path('<int:hand_id>/', hand_detail, name='hand_detail'),
    path('session/<int:session_id>/', sessison_hands_list, name='session_hands_list'),
    path('sendmail/', send_mail_to_all, name="sendmail"),
]