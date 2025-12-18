from django.urls import path
from poker.views import (add_session, 
                         session_list, 
                         session_detail,
                         all_sessions, 
                         session_list_by_month, 
                         session_detail_by_month,
                         edit_session,
                         overall_chart,
                         session_list_25,
                         session_list_13,
                         homepage_view,
                         chart_25,
                         session_hands,
                         all_sessions_chart
                         )

app_name = 'poker' 

urlpatterns = [
    path('', homepage_view, name='home'),
    path('sessions/', session_list, name='session_list'),
    path('sessions/add/', add_session, name='add_session'),
    path('session_detail/<int:session_id>/', session_detail, name='session_detail'),
    path('all_sessions/', all_sessions, name='all_sessions'),
    path('sessions-by-month/', session_list_by_month, name='session_list_by_month'),
    path('sessions-by-month/<int:year>/<int:month>/', session_detail_by_month, name='session_detail_by_month'),
    path('session/edit/<int:session_id>/', edit_session, name='edit_session'),
    path('chart/', overall_chart, name='overall_chart'),
    path('25_sessions/', session_list_25, name='session_list_25'),
    path('13_sessions/', session_list_13, name='session_list_13'),
    path('chart_25/', chart_25, name='chart_25'),
    path('hands/', session_hands, name='session_hands'),
    path('all_sessions_chart/', all_sessions_chart, name='all_sessions_chart')
 
]