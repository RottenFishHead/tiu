
from django.urls import path
from expenses import views
from django.conf.urls.static import static
from django.conf import settings
from poker.views import (add_session, 
                         session_list, 
                         session_detail,
                         all_sessions, 
                         session_list_by_month, 
                         session_detail_by_month,
                         edit_session,
                         overall_chart,
                         session_list_25,
                         session_list_23,
                         homepage_view,
                         chart_25,
                         session_hands,
                         all_sessions_chart,
                         all_sessions_buyin_cashout_chart,
                         daily_winloss_chart,
                         weekday_winloss_chart,
                         profit_per_session_chart,
                         casino_win_rates,
                         head_to_head, head_to_head_selector, head_to_head_august,
                         player_list, 
                         player_create,
                         player_detail, player_update, player_delete,
                         observation_create, observation_update, observation_delete,
                         observation_quick_add,
                         tendency_create, tendency_update, tendency_delete, tendency_press,
                         exploit_press, exploit_update, exploit_delete,
                         poker_notes, poker_note_edit, poker_note_delete,
                         stop_list, stop_create, stop_detail, stop_edit, stop_delete
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
    path('23_sessions/', session_list_23, name='session_list_23'),
    path('chart_25/', chart_25, name='chart_25'),
    path('hands/', session_hands, name='session_hands'),
    path('all_sessions_chart/', all_sessions_chart, name='all_sessions_chart'),
    path('all_sessions_buyin_cashout_chart/', all_sessions_buyin_cashout_chart, name='all_sessions_buyin_cashout_chart'),
    path('daily_winloss/', daily_winloss_chart, name='daily_winloss_chart'),
    path('weekday_winloss/', weekday_winloss_chart, name='weekday_winloss_chart'),
    path('profit_per_session/', profit_per_session_chart, name='profit_per_session_chart'),
    path('casino-win-rates/', casino_win_rates, name='casino_win_rates'),
    path('head-to-head/<int:user_a_id>/<int:user_b_id>/', head_to_head, name='head_to_head'),
    path('head-to-head/', head_to_head_selector, name='head_to_head_selector'),
    path('head-to-head-august/', head_to_head_august, name='head_to_head_august'),
    path('notes/', poker_notes, name='poker_notes'),
    path('notes/<int:pk>/edit/', poker_note_edit, name='poker_note_edit'),
    path('notes/<int:pk>/delete/', poker_note_delete, name='poker_note_delete'),
    path('stops/', stop_list, name='stop_list'),
    path('stops/add/', stop_create, name='stop_create'),
    path('stops/<int:pk>/', stop_detail, name='stop_detail'),
    path('stops/<int:pk>/edit/', stop_edit, name='stop_edit'),
    path('stops/<int:pk>/delete/', stop_delete, name='stop_delete'),
    path("player/", player_list, name="player_list"),
    path("player/add/", player_create, name="player_create"),
    path("player/<int:pk>/", player_detail, name="player_detail"),
    path("player/<int:pk>/edit/", player_update, name="player_update"),
    path("player/<int:pk>/delete/", player_delete, name="player_delete"),
    # Observations (nested under player)
    path("player/<int:player_pk>/observations/add/", observation_create, name="observation_create"),
    path("player/<int:player_pk>/observations/quick-add/", observation_quick_add, name="observation_quick_add"),
    path("observations/<int:pk>/edit/", observation_update, name="observation_update"),
    path("observations/<int:pk>/delete/", observation_delete, name="observation_delete"),

    # Tendencies
    path("player/<int:player_pk>/tendencies/add/", tendency_create, name="tendency_create"),
    path("tendencies/<int:pk>/edit/", tendency_update, name="tendency_update"),
    path("tendencies/<int:pk>/delete/", tendency_delete, name="tendency_delete"),
    path("player/<int:player_pk>/tendencies/press/", tendency_press, name="tendency_press"),
    path("player/<int:player_pk>/exploits/press/", exploit_press, name="exploit_press"),
    path("exploits/<int:pk>/edit/", exploit_update, name="exploit_update"),
    path("exploits/<int:pk>/delete/", exploit_delete, name="exploit_delete"),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 
