from django.shortcuts import render, get_object_or_404, redirect
from .models import PokerSession,PlayerProfile, PlayerObservation, PlayerTendency, PlayerProfile, PlayerTendency, ExploitTag, PlayerExploit, PokerNote, PokerNoteKeyword, StopIt
from hands.models import Hands
from .forms import PokerSessionForm, DateForm, PlayerProfileForm, PlayerObservationForm, PlayerTendencyForm, PlayerTendencyEditForm, PlayerExploitEditForm, PokerNoteForm, StopItForm
from .fields import STAKES_CHOICES
from django.utils import timezone
from django.db.models import Sum, ExpressionWrapper, F, DurationField, Count
from django.db.models.functions import ExtractWeekDay, TruncMonth
from django.contrib.auth.decorators import login_required
import traceback as _traceback
import os as _os
from django.conf import settings as _settings
from plotly.offline import plot
from plotly import graph_objs as go
import plotly.express as px
import pandas as pd
from calendar import month_name
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from .presets import TENDENCY_PRESETS, EXPLOIT_PRESETS
from datetime import datetime, timezone as datetime_timezone, timedelta
from django.contrib.auth.models import User
from datetime import date as dt_date


def finalize_plotly_figure(fig):
    """Apply safe defaults so labels don't get clipped when data density grows."""
    fig.update_layout(
        autosize=True,
        margin=dict(l=80, r=60, t=70, b=90),
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    fig.update_traces(cliponaxis=False)
    return fig




@login_required
def session_detail(request, session_id):
    session = get_object_or_404(PokerSession, id=session_id, player=request.user)
    try:
        hands = Hands.objects.get(session_id=session_id)
    except Hands.DoesNotExist:
        hands = None  # Set hands to None if no hands are found for the session

    session_started_at = None
    session_ended_at = None

    if session.timer_started_at_ms:
        started_dt = datetime.fromtimestamp(session.timer_started_at_ms / 1000, tz=datetime_timezone.utc)
        session_started_at = timezone.localtime(started_dt)

    if session.timer_completed_at_ms:
        ended_dt = datetime.fromtimestamp(session.timer_completed_at_ms / 1000, tz=datetime_timezone.utc)
        session_ended_at = timezone.localtime(ended_dt)

    if request.method == "POST" and request.POST.get("action") == "update_stop_state":
        new_state = request.POST.get("stop_state")
        if session.selected_stop and new_state in dict(StopIt._meta.get_field("state").choices):
            session.selected_stop.state = new_state
            session.selected_stop.save(update_fields=["state"])
            messages.success(request, "Stop state updated.")
            return redirect("poker:session_detail", session_id=session_id)

    show_important_notes = request.user.username.lower() != "penner"

    context = {
        "session": session,
        "hands": hands,
        "session_started_at": session_started_at,
        "session_ended_at": session_ended_at,
        "displayed_stop": session.selected_stop,
        "stop_state_choices": StopIt._meta.get_field("state").choices,
        "important_notes": PokerNote.objects.filter(player=request.user, is_important=True).order_by("-updated") if show_important_notes else PokerNote.objects.none(),
        "show_important_notes": show_important_notes,
        
    }
    return render(request, 'poker/session_detail.html', context)


@login_required
def head_to_head(request, user_a_id, user_b_id):
    # Compare wins/losses on dates where both users played
    user_a = get_object_or_404(User, pk=user_a_id)
    user_b = get_object_or_404(User, pk=user_b_id)

    # Dates each played (as sorted lists)
    dates_a = sorted(set(PokerSession.objects.filter(player=user_a).values_list('date', flat=True)))
    dates_b = sorted(set(PokerSession.objects.filter(player=user_b).values_list('date', flat=True)))

    # Try exact-date intersection first
    exact_shared = sorted(set(dates_a).intersection(dates_b))

    # If no exact shared dates, attempt nearest-date matching within +/-1 day
    matched_pairs = []  # list of tuples (label_date, date_a, date_b)
    if exact_shared:
        for d in exact_shared:
            matched_pairs.append((d, d, d))
    else:
        # try small window first, then a larger window if nothing found
        for delta_days in (1, 7):
            used_b = set()
            for da in dates_a:
                # find a db within +/- delta_days that isn't already used
                found = None
                for db in dates_b:
                    if db in used_b:
                        continue
                    if abs((db - da).days) <= delta_days:
                        found = db
                        break
                if found:
                    used_b.add(found)
                    # label with the earlier of the two dates for readability
                    label = da if da <= found else found
                    matched_pairs.append((label, da, found))
            if matched_pairs:
                # found matches with this delta; stop expanding window
                break

    # Build profit aggregates for matched pairs
    a_profit_by_date = {}
    b_profit_by_date = {}
    for label, da, db in matched_pairs:
        a_sessions = PokerSession.objects.filter(player=user_a, date=da)
        b_sessions = PokerSession.objects.filter(player=user_b, date=db)
        a_profit = sum(((s.cash_out or 0) - (s.buy_in or 0)) for s in a_sessions)
        b_profit = sum(((s.cash_out or 0) - (s.buy_in or 0)) for s in b_sessions)
        a_profit_by_date[label] = float(a_profit)
        b_profit_by_date[label] = float(b_profit)

    # Prepare plotly figure: grouped bar chart per shared date
    dates = [d.strftime('%Y-%m-%d') for d in sorted(a_profit_by_date.keys())]
    a_vals = [a_profit_by_date.get(d, 0) for d in sorted(a_profit_by_date.keys())]
    b_vals = [b_profit_by_date.get(d, 0) for d in sorted(b_profit_by_date.keys())]

    fig = go.Figure()
    fig.add_trace(go.Bar(name=str(user_a.username), x=dates, y=a_vals, marker_color='#2b8cbe'))
    fig.add_trace(go.Bar(name=str(user_b.username), x=dates, y=b_vals, marker_color='#f03b20'))
    fig.update_layout(barmode='group', title=f'Head-to-head: {user_a.username} vs {user_b.username}', xaxis_title='Date', yaxis_title='Profit ($)')
    finalize_plotly_figure(fig)
    chart_json = fig.to_plotly_json()
    # labels/dates used in the chart
    shared_dates = sorted(a_profit_by_date.keys())

    context = {
        'user_a': user_a,
        'user_b': user_b,
        'shared_dates_count': len(shared_dates),
        'shared_dates': shared_dates,
        'user_a_sessions_count': PokerSession.objects.filter(player=user_a).count(),
        'user_b_sessions_count': PokerSession.objects.filter(player=user_b).count(),
        'chart_json': chart_json,
    }
    return render(request, 'poker/head_to_head.html', context)


@login_required
def head_to_head_selector(request):
    # Presents a simple selector to choose two users to compare
    users = User.objects.order_by('username').all()
    return render(request, 'poker/head_to_head_selector.html', {'users': users})


def head_to_head_august(request):
    """List each user's win/loss per day for August 2026 in a side-by-side table.
    This view is intentionally simple and does not render a chart.
    """
    user_ids = [1, 2]
    users = list(User.objects.filter(id__in=user_ids).order_by('id'))
    if len(users) < 2:
        missing = set(user_ids) - set(u.id for u in users)
        return render(request, 'poker/head_to_head_august_table.html', {'error': f'Missing users: {sorted(list(missing))}'})

    year = 2026
    month = 8

    rows = []
    for day in range(1, 32):
        try:
            d = dt_date(year, month, day)
        except Exception:
            continue
        a_total = PokerSession.objects.filter(player=users[0], date=d).aggregate(total=Sum(F('cash_out') - F('buy_in')))['total'] or 0
        b_total = PokerSession.objects.filter(player=users[1], date=d).aggregate(total=Sum(F('cash_out') - F('buy_in')))['total'] or 0
        rows.append({'date': d, 'a_total': float(a_total), 'b_total': float(b_total)})

    context = {
        'users': users,
        'rows': rows,
        'year': year,
        'month': month,
    }
    return render(request, 'poker/head_to_head_august_table.html', context)

@login_required
def edit_session(request, session_id):
    session = get_object_or_404(PokerSession, id=session_id, player=request.user)

    if request.method == 'POST':
        form = PokerSessionForm(request.POST, instance=session)
        if form.is_valid():
            updated_session = form.save(commit=False)
            updated_session.player = request.user
            updated_session.save()
            return redirect('poker:session_detail', session_id=session_id)
    else:
        form = PokerSessionForm(instance=session)

    context = {
        'form': form,
        'session': session,
    }

    return render(request, 'poker/session_edit.html', context)

@login_required
def add_session(request):
    show_important_notes = request.user.username.lower() != "penner"
    important_notes = PokerNote.objects.filter(player=request.user, is_important=True).order_by("-updated") if show_important_notes else PokerNote.objects.none()
    available_stops = StopIt.objects.exclude(state="mastered")
    displayed_stop = None

    if request.method == 'POST':
        form = PokerSessionForm(request.POST)
        displayed_stop_id = request.POST.get("displayed_stop_id")
        if displayed_stop_id:
            displayed_stop = available_stops.filter(pk=displayed_stop_id).first()

        if displayed_stop is None:
            displayed_stop = available_stops.order_by("?").first()

        if form.is_valid():
            session = form.save(commit=False)
            session.player = request.user
            session.selected_stop = displayed_stop
            session.save()
            return redirect('poker:session_list')
    else:
        form = PokerSessionForm()
        displayed_stop = available_stops.order_by("?").first()

    return render(request, 'poker/add_session.html', {
        'form': form,
        'important_notes': important_notes,
        'displayed_stop': displayed_stop,
        'show_important_notes': show_important_notes,
    })


@login_required
def stop_create(request):
    if request.method == "POST":
        form = StopItForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Stop added.")
            return redirect("poker:stop_list")
    else:
        form = StopItForm()

    return render(request, "poker/child_form.html", {
        "form": form,
        "title": "Add Stop",
        "cancel_url": reverse("poker:stop_list"),
    })


@login_required
def stop_list(request):
    search_query = request.GET.get("q", "").strip()
    stops = StopIt.objects.all()

    if search_query:
        stops = stops.filter(
            Q(stop__icontains=search_query)
            | Q(state__icontains=search_query)
        )
        if search_query.isdigit():
            stops = stops.filter(Q(fails=int(search_query)))

    return render(request, "poker/stop_list.html", {
        "stops": stops,
        "search_query": search_query,
    })


@login_required
def stop_detail(request, pk):
    stop = get_object_or_404(StopIt, pk=pk)
    return render(request, "poker/stop_detail.html", {
        "stop": stop,
    })


@login_required
def stop_edit(request, pk):
    stop = get_object_or_404(StopIt, pk=pk)

    if request.method == "POST":
        form = StopItForm(request.POST, instance=stop)
        if form.is_valid():
            form.save()
            messages.success(request, "Stop updated.")
            return redirect("poker:stop_list")
    else:
        form = StopItForm(instance=stop)

    return render(request, "poker/child_form.html", {
        "form": form,
        "title": "Edit Stop",
        "cancel_url": reverse("poker:stop_list"),
    })


@login_required
def stop_delete(request, pk):
    stop = get_object_or_404(StopIt, pk=pk)

    if request.method == "POST":
        stop.delete()
        messages.success(request, "Stop deleted.")
        return redirect("poker:stop_list")

    return render(request, "poker/confirm_delete.html", {
        "object": stop,
        "cancel_url": reverse("poker:stop_list"),
    })

@login_required
def session_list(request):
    current_month = timezone.now().month
    current_year = timezone.now().year
    requested_month = int(request.GET.get('month', current_month))
    requested_year = int(request.GET.get('year', current_year))

    
    sessions = PokerSession.objects.filter(player=request.user, date__month=requested_month, date__year=requested_year)
    overall_total = sum(session.win_loss for session in sessions)
    overall_hours = sum(session.hours for session in sessions)
    overall_hourly_rate = overall_total / overall_hours if overall_hours > 0 else 0

    return render(request, 'poker/session_list.html', {
        'sessions': sessions,
        'overall_hourly_rate': overall_hourly_rate,
        'overall_total': overall_total,
        'current_month': current_month,
        'current_year': current_year,
    })
    


@login_required
def all_sessions(request):
    sessions = PokerSession.objects.filter(player=request.user)
    overall_total = sum(session.win_loss for session in sessions)
    overall_hours = sum(session.hours for session in sessions)
    overall_hourly_rate = overall_total / overall_hours if overall_hours > 0 else 0
    return render(request, 'poker/all_sessions.html', {'sessions': sessions, 'overall_hourly_rate':overall_hourly_rate, 'overall_total': overall_total,})

@login_required
def session_list_by_month(request):
    stakes_filter = request.GET.get('stakes')
    sessions = PokerSession.objects.filter(player=request.user)

    if stakes_filter:
        sessions = sessions.filter(stakes=stakes_filter)

    sessions_by_month = sessions.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_profit=Sum('cash_out') - Sum('buy_in'),
        total_hours=Sum('hours')
    ).order_by('-month')

    for session in sessions_by_month:
        if session['total_hours']:
            session['win_rate_per_hour'] = session['total_profit'] / session['total_hours']
        else:
            session['win_rate_per_hour'] = None

    context = {
        'sessions_by_month': sessions_by_month,
        'stakes_filter': stakes_filter,
    }
    return render(request, 'poker/session_list_by_month.html', context)

@login_required
def session_detail_by_month(request, year, month):
    sessions_in_month = PokerSession.objects.filter(player=request.user,
        date__year=year,
        date__month=month,
    ).annotate(
        total_profit=Sum('cash_out') - Sum('buy_in')
    )
    total_profit_for_month = sessions_in_month.aggregate(Sum('total_profit'))['total_profit__sum']
    context = {
        'year': year,
        'month': month,
        'sessions_in_month': sessions_in_month,
       'total_profit_for_month': total_profit_for_month,
    }
    return render(request, 'poker/session_detail_by_month.html', context)

@login_required
def overall_chart(request):
    session =  PokerSession.objects.filter(player=request.user)
    start = request.GET.get('start')
    end = request.GET.get('end')
    stakes = request.GET.get('stakes')
    
    if start:
        session = session.filter(date__gte=start)
    if end:
        session = session.filter(date__lte=end)
    if stakes:
        session = session.filter(stakes=stakes)
    
    dates = [s.date for s in session]
    win_losses = [s.win_loss for s in session]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=win_losses,
        mode='lines+markers',
        name='Win/Loss'
    ))
    fig.update_layout(
        title='Overall Stats',
        xaxis_title='Date',
        yaxis_title='Win/Loss'
    )
    fig.update_xaxes(tickangle=45, tickfont=dict(family='Rockwell', color='green', size=14))
    fig.update_layout(title={
        'font_size': 22,
        'xanchor': 'center',

        'x': 0.5
    })
    finalize_plotly_figure(fig)
    
    chart = fig.to_html()
        
    context = {'chart': chart, 'form':DateForm}
    return render(request, 'poker/overall_chart.html', context)
    
@login_required
def session_list_25(request):
    current_month = timezone.now().month
    current_year = timezone.now().year
    requested_month = int(request.GET.get('month', current_month))
    requested_year = int(request.GET.get('year', current_year))
    requested_stakes = request.GET.get('stakes', '25')  # Default to '25' if not provided

    # Generate month choices for the dropdown
    month_choices = [(str(i), month_name[i]) for i in range(1, 13)]

    sessions = PokerSession.objects.filter(
        player=request.user,
        date__month=requested_month,
        date__year=requested_year,
        stakes=requested_stakes
    )

    overall_aggregate = sessions.aggregate(
        total_win_loss=Sum(F('cash_out') - F('buy_in')),
        total_hours=Sum('hours')
    )

    overall_total = overall_aggregate['total_win_loss'] or 0
    overall_hours = overall_aggregate['total_hours'] or 0
    overall_hourly_rate = overall_total / overall_hours if overall_hours > 0 else 0
    overall_win_loss_rate = overall_total / overall_hours if overall_hours > 0 else 0

    return render(request, 'poker/session_list_25.html', {
        'sessions': sessions,
        'overall_hourly_rate': overall_hourly_rate,
        'overall_win_loss_rate': overall_win_loss_rate,
        'overall_total': overall_total,
        'current_month': current_month,
        'current_year': current_year,
        'requested_month': requested_month,
        'requested_stakes': requested_stakes,
        'month_choices': month_choices,
    })

@login_required
def session_list_23(request):
    current_month = timezone.now().month
    current_year = timezone.now().year
    requested_month = int(request.GET.get('month', current_month))
    requested_year = int(request.GET.get('year', current_year))
    requested_stakes = request.GET.get('stakes', '23')  # Default to '23' if not provided

    # Generate month choices for the dropdown
    month_choices = [(str(i), month_name[i]) for i in range(1, 13)]

    sessions = PokerSession.objects.filter(
        player=request.user,
        date__month=requested_month,
        date__year=requested_year,
        stakes=requested_stakes
    )

    overall_aggregate = sessions.aggregate(
        total_win_loss=Sum(F('cash_out') - F('buy_in')),
        total_hours=Sum('hours')
    )

    overall_total = overall_aggregate['total_win_loss'] or 0
    overall_hours = overall_aggregate['total_hours'] or 0
    overall_hourly_rate = overall_total / overall_hours if overall_hours > 0 else 0
    overall_win_loss_rate = overall_total / overall_hours if overall_hours > 0 else 0

    return render(request, 'poker/session_list_23.html', {
        'sessions': sessions,
        'overall_hourly_rate': overall_hourly_rate,
        'overall_win_loss_rate': overall_win_loss_rate,
        'overall_total': overall_total,
        'current_month': current_month,
        'current_year': current_year,
        'requested_month': requested_month,
        'requested_stakes': requested_stakes,
        'month_choices': month_choices,
    })
@login_required
def homepage_view(request):
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    all_sessions = PokerSession.objects.filter(player=request.user)
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    try:
        selected_month = int(selected_month) if selected_month else current_month
    except (TypeError, ValueError):
        selected_month = current_month

    if selected_month < 1 or selected_month > 12:
        selected_month = current_month

    try:
        selected_year = int(selected_year) if selected_year else current_year
    except (TypeError, ValueError):
        selected_year = current_year

    month_choices = [(i, month_name[i]) for i in range(1, 13)]
    year_choices = all_sessions.dates('date', 'year', order='DESC')
  
    
    
    overall_total = sum(session.win_loss for session in all_sessions)
    overall_hours = sum(session.hours for session in all_sessions)
    overall_hourly_rate = overall_total / overall_hours if overall_hours > 0 else 0
    
    filtered_sessions = all_sessions.filter(date__month=selected_month, date__year=selected_year)

    current_month_sessions = filtered_sessions.order_by('-date', '-id')

    current_month_total = sum(session.win_loss for session in current_month_sessions)
    current_month_hours = sum(session.hours for session in current_month_sessions)
    current_month_hourly_rate = current_month_total / current_month_hours if current_month_hours > 0 else 0
    
    monthly_totals = (
        all_sessions
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total_win_loss=Sum(F('cash_out') - F('buy_in')))
        .order_by('month')
    )

    month_labels = [item['month'].strftime('%Y-%m') for item in monthly_totals]
    month_values = [item['total_win_loss'] or 0 for item in monthly_totals]
    bar_colors = ['#198754' if value >= 0 else '#dc3545' for value in month_values]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=month_labels,
        y=month_values,
        marker_color=bar_colors,
        name='Monthly Win/Loss',
        text=[f'${value:,.0f}' for value in month_values],
        textposition='outside'
    ))

    fig.update_layout(
        title='Monthly Win/Loss',
        xaxis_title='Month',
        yaxis_title='Win/Loss ($)',
        showlegend=False,
        autosize=True,
    )
    fig.update_xaxes(tickangle=35)
    finalize_plotly_figure(fig)
    
    chart = fig.to_html()
        
    context = {'chart': chart,
        'overall_hourly_rate': overall_hourly_rate,
        'overall_hours': overall_hours,
        'overall_total': overall_total,
        'current_month': selected_month,
        'current_year': selected_year,
        'current_month_sessions': current_month_sessions,
        'current_month_total': current_month_total,
        'current_month_hours': current_month_hours,
        'current_month_hourly_rate': current_month_hourly_rate,
        'month_choices': month_choices,
        'year_choices': year_choices,
        'selected_month': selected_month,
        'selected_year': selected_year,
            }
    return render(request, 'poker/home.html', context)

@login_required
def chart_25(request):
    """Profit per session bar chart with stakes filter"""
    # Get filter parameters
    stakes = request.GET.get('stakes', '25')  # Default to 2/5
    
    # Fetch sessions for the logged-in user with selected stakes
    sessions = PokerSession.objects.filter(player=request.user, stakes=stakes).order_by('date')
    
    # Create a DataFrame from the queryset
    data = {
        'date': [session.date for session in sessions],
        'profit': [session.win_loss for session in sessions],
    }
    df = pd.DataFrame(data)
    
    if not df.empty:
        # Create the bar chart
        fig = px.bar(df.sort_values("date"), x="date", y="profit", title=f"Profit per Session - Stakes: {dict(STAKES_CHOICES).get(stakes, stakes)}")
        fig.update_layout(yaxis_title="Profit $")
    else:
        # Empty chart if no data
        fig = go.Figure()
        fig.update_layout(
            title=f"No sessions found for stakes: {dict(STAKES_CHOICES).get(stakes, stakes)}",
            xaxis_title="Date",
            yaxis_title="Profit $"
        )
    finalize_plotly_figure(fig)
    
    chart = fig.to_html()
    
    context = {
        'chart': chart,
        'stakes_choices': STAKES_CHOICES,
        'selected_stakes': stakes,
    }
    return render(request, 'poker/chart_25.html', context)

@login_required
def session_hands(request):
    hands = Hands.objects.filter(session__player=request.user)
    sessions_with_hands = PokerSession.objects.filter(player=request.user, id__in=hands.values('session_id'))
    return render(request, 'poker/session_hands.html', {'sessions': sessions_with_hands})


@login_required
def all_sessions_chart(request):
    """Bankroll / Cumulative Profit Over Time chart starting at $2000"""
    # Fetch data from the database for the logged-in user
    sessions = PokerSession.objects.filter(player=request.user).order_by('date')

    # Create a DataFrame from the queryset
    data = {
        'date': [session.date for session in sessions],
        'profit': [session.win_loss for session in sessions],
    }
    df = pd.DataFrame(data)

    # Sort by date and calculate cumulative profit
    df = df.sort_values("date")
    df["cum_profit"] = df["profit"].cumsum()
    
    # Add starting bankroll of $2000
    starting_bankroll = 2000
    df["bankroll"] = starting_bankroll + df["cum_profit"]

    # Create the Plotly Express chart
    fig = px.line(df, x="date", y="bankroll", title="Bankroll Over Time")
    fig.update_layout(
        yaxis_title="Bankroll ($)",
        xaxis_title="Date",
        hovermode='x unified'
    )
    
    # Add a horizontal line at starting bankroll
    fig.add_hline(y=starting_bankroll, line_dash="dash", line_color="gray", 
                  annotation_text=f"Starting Bankroll: ${starting_bankroll}")
    finalize_plotly_figure(fig)

    # Convert the Plotly figure to JSON
    chart_json = fig.to_json()

    return render(request, 'poker/all_sessions_chart.html', {'chart_json': chart_json})


@login_required
def profit_per_session_chart(request):
    """Bar chart showing profit for each session"""
    # Fetch sessions for the logged-in user
    sessions = PokerSession.objects.filter(player=request.user).order_by('date')
    
    # Create a DataFrame from the queryset
    data = {
        'date': [session.date for session in sessions],
        'profit': [session.win_loss for session in sessions],
    }
    df = pd.DataFrame(data)
    
    # Create the bar chart
    fig = px.bar(df.sort_values("date"), x="date", y="profit", title="Profit per Session")
    fig.update_layout(yaxis_title="Profit $")
    finalize_plotly_figure(fig)
    
    # Convert the Plotly figure to JSON
    chart_json = fig.to_json()

    return render(request, 'poker/profit_per_session_chart.html', {'chart_json': chart_json})


@login_required
def daily_winloss_chart(request):
    """Bar chart showing win/loss for each session day, with optional month filter"""
    # Get filter parameters
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    # Start with all sessions for the logged-in user
    sessions = PokerSession.objects.filter(player=request.user)
    
    # Apply filters if provided
    if year:
        sessions = sessions.filter(date__year=year)
    if month:
        sessions = sessions.filter(date__month=month)
    
    # Order by date
    sessions = sessions.order_by('date')
    
    # Prepare data for the chart
    dates = [s.date.strftime('%Y-%m-%d') for s in sessions]
    win_losses = [s.win_loss for s in sessions]
    
    # Create color list (green for wins, red for losses)
    colors = ['green' if wl > 0 else 'red' for wl in win_losses]
    
    # Create bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dates,
        y=win_losses,
        marker_color=colors,
        name='Win/Loss',
        text=[f'${wl:,.0f}' for wl in win_losses],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Daily Win/Loss',
        xaxis_title='Date',
        yaxis_title='Win/Loss ($)',
        hovermode='x unified',
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=45)
    finalize_plotly_figure(fig)
    
    # Convert to HTML
    chart = fig.to_html()
    
    # Get available years and months for filter dropdowns
    all_sessions = PokerSession.objects.filter(player=request.user)
    years = all_sessions.dates('date', 'year', order='DESC')
    months = [(i, month_name[i]) for i in range(1, 13)]
    
    context = {
        'chart': chart,
        'years': years,
        'months': months,
        'selected_year': year,
        'selected_month': month,
    }
    
    return render(request, 'poker/daily_winloss_chart.html', context)


@login_required
def weekday_winloss_chart(request):
    """Bar chart showing aggregated win/loss by day of week."""
    year = request.GET.get('year')
    stakes = request.GET.get('stakes')

    sessions = PokerSession.objects.filter(player=request.user)
    if year:
        sessions = sessions.filter(date__year=year)
    if stakes:
        sessions = sessions.filter(stakes=stakes)

    weekday_totals = (
        sessions
        .annotate(weekday_num=ExtractWeekDay('date'))
        .values('weekday_num')
        .annotate(
            sessions_count=Count('id'),
            total_win_loss=Sum(F('cash_out') - F('buy_in')),
        )
    )

    totals_by_day = {item['weekday_num']: (item['total_win_loss'] or 0) for item in weekday_totals}

    weekday_order = [2, 3, 4, 5, 6, 7, 1]
    weekday_labels = {
        1: 'Sunday',
        2: 'Monday',
        3: 'Tuesday',
        4: 'Wednesday',
        5: 'Thursday',
        6: 'Friday',
        7: 'Saturday',
    }

    x_labels = [weekday_labels[d] for d in weekday_order]
    y_values = [totals_by_day.get(d, 0) for d in weekday_order]
    colors = ['#198754' if value >= 0 else '#dc3545' for value in y_values]

    weekday_data = {item['weekday_num']: item for item in weekday_totals}
    weekday_rows = []
    for day_num in weekday_order:
        day_stats = weekday_data.get(day_num, {})
        sessions_count = day_stats.get('sessions_count', 0) or 0
        total_win_loss = day_stats.get('total_win_loss', 0) or 0
        avg_per_session = (total_win_loss / sessions_count) if sessions_count else 0
        weekday_rows.append({
            'label': weekday_labels[day_num],
            'sessions_count': sessions_count,
            'total_win_loss': total_win_loss,
            'avg_per_session': avg_per_session,
        })

    total_sessions = sum(row['sessions_count'] for row in weekday_rows)
    total_win_loss = sum(row['total_win_loss'] for row in weekday_rows)
    overall_avg_per_session = (total_win_loss / total_sessions) if total_sessions else 0

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_labels,
        y=y_values,
        marker_color=colors,
        text=[f'${value:,.0f}' for value in y_values],
        textposition='outside',
        name='Win/Loss',
    ))

    fig.update_layout(
        title='Win/Loss by Day of Week',
        xaxis_title='Day of Week',
        yaxis_title='Win/Loss ($)',
        showlegend=False,
        hovermode='x unified',
    )
    finalize_plotly_figure(fig)

    chart = fig.to_html()
    all_sessions = PokerSession.objects.filter(player=request.user)
    years = all_sessions.dates('date', 'year', order='DESC')

    context = {
        'chart': chart,
        'weekday_rows': weekday_rows,
        'weekday_summary': {
            'total_sessions': total_sessions,
            'total_win_loss': total_win_loss,
            'overall_avg_per_session': overall_avg_per_session,
        },
        'years': years,
        'selected_year': year,
        'stakes_choices': STAKES_CHOICES,
        'selected_stakes': stakes,
    }
    return render(request, 'poker/weekday_winloss_chart.html', context)


@login_required
def casino_win_rates(request):
    """Show win-rate (percent of sessions that were winning) grouped by casino.
    If an exception occurs, write the traceback to BASE_DIR/casino_win_rates_error.txt
    so the developer can open it in the editor (useful when server logs aren't visible).
    """
    try:
        # filters
        start = request.GET.get('start')
        end = request.GET.get('end')
        stakes = request.GET.get('stakes')

        sessions = PokerSession.objects.filter(player=request.user)
        if start:
            sessions = sessions.filter(date__gte=start)
        if end:
            sessions = sessions.filter(date__lte=end)
        if stakes:
            sessions = sessions.filter(stakes=stakes)

        qs = (
            sessions
            .values('casino__id', 'casino__name')
            .annotate(
                session_count=Count('id'),
                wins=Count('id', filter=Q(cash_out__gt=F('buy_in'))),
            )
            .order_by('-wins')
        )

        rows = []
        for item in qs:
            sc = item.get('session_count') or 0
            wins = item.get('wins') or 0
            win_rate = (wins / sc * 100) if sc else 0
            rows.append({
                'casino_id': item.get('casino__id'),
                'casino_name': item.get('casino__name'),
                'session_count': sc,
                'wins': wins,
                'win_rate_pct': round(win_rate, 2),
            })

        context = {
            'rows': rows,
            'selected_start': start,
            'selected_end': end,
            'selected_stakes': stakes,
            'stakes_choices': STAKES_CHOICES,
        }
        return render(request, 'poker/casino_win_rates.html', context)
    except Exception as e:
        tb = _traceback.format_exc()
        # write traceback to project root so user can open it in editor
        try:
            out_path = _settings.BASE_DIR / 'casino_win_rates_error.txt'
            with open(out_path, 'w') as f:
                f.write(tb)
            file_path_str = str(out_path)
        except Exception:
            file_path_str = 'could not write file; see server logs'

        # Also return the traceback as plain text so it appears directly in the browser
        from django.http import HttpResponse
        body = f"Error: {str(e)}\n\nTraceback:\n{tb}\n\nTracefile: {file_path_str}\n"
        return HttpResponse(body, content_type='text/plain', status=200)
    return render(request, 'poker/casino_win_rates.html', context)


# --- Player poker ---


@login_required
def player_list(request):
    q = (request.GET.get("q") or "").strip()
    players = PlayerProfile.objects.all().order_by("display_name")

    if q:
        players = players.filter(
            Q(display_name__icontains=q)
            | Q(summary__icontains=q)
            | Q(description__icontains=q)
            | Q(tags__name__icontains=q)
        ).distinct()

    return render(request, "poker/player_list.html", {"players": players, "q": q})


@login_required
def player_detail(request, pk):
    player = get_object_or_404(PlayerProfile, pk=pk)
    observations = player.observations.all()
    tendencies = player.tendencies.all().order_by("metric", "street")
    quick_obs_form = PlayerObservationForm()
    exploits = player.exploits.select_related("tag").all().order_by("-confidence", "-strength", "-updated")
    return render(request, "poker/player_detail.html", {
        "player": player,
        "observations": observations,
        "tendencies": tendencies,
        "quick_obs_form": quick_obs_form,
        "tendency_presets": TENDENCY_PRESETS,
        "exploit_presets": EXPLOIT_PRESETS,
        "exploits": exploits,
    })

@login_required
def tendency_press(request, player_pk):
    player = get_object_or_404(PlayerProfile, pk=player_pk)
    if request.method != "POST":
        return redirect("profiles:player_detail", pk=player.pk)

    metric = request.POST.get("metric", "").strip()
    street = request.POST.get("street", "").strip()

    if not metric or not street:
        messages.error(request, "Missing tendency data.")
        return redirect("profiles:player_detail", pk=player.pk)

    obj, created = PlayerTendency.objects.get_or_create(
        player=player,
        metric=metric,
        street=street,
        defaults={"sample_size": 1, "confidence": 3}
    )

    if not created:
        obj.sample_size = (obj.sample_size or 0) + 1
        obj.confidence = min(5, (obj.confidence or 1) + 1)
        obj.save(update_fields=["sample_size", "confidence", "updated"])
        messages.success(request, "Tendency reinforced (+1 sample).")
    else:
        messages.success(request, "Tendency added.")

    return redirect("profiles:player_detail", pk=player.pk)


@login_required
def player_create(request):
    if request.method == "POST":
        form = PlayerProfileForm(request.POST, request.FILES)  # ✅ FILES
        if form.is_valid():
            player = form.save()
            messages.success(request, "Player created.")
            return redirect("poker:player_detail", pk=player.pk)
    else:
        form = PlayerProfileForm()

    return render(request, "poker/player_form.html", {"form": form, "mode": "create"})


@login_required
def player_update(request, pk):
    player = get_object_or_404(PlayerProfile, pk=pk)

    if request.method == "POST":
        form = PlayerProfileForm(request.POST, request.FILES, instance=player)  
        if form.is_valid():
            form.save()
            messages.success(request, "Player updated.")
            return redirect("poker:player_detail", pk=player.pk)
    else:
        form = PlayerProfileForm(instance=player)

    return render(request, "poker/player_form.html", {"form": form, "mode": "edit", "player": player})


@login_required
def player_delete(request, pk):
    player = get_object_or_404(PlayerProfile, pk=pk)

    if request.method == "POST":
        player.delete()
        messages.success(request, "Player deleted.")
        return redirect("poker:player_list")

    return render(request, "poker/confirm_delete.html", {
        "object": player,
        "cancel_url": reverse("poker:player_detail", kwargs={"pk": player.pk}),
    })


# --- Observations ---

@login_required
def observation_quick_add(request, player_pk):
    """
    ✅ POST-only endpoint used by the modal on player_detail.
    """
    player = get_object_or_404(PlayerProfile, pk=player_pk)

    if request.method != "POST":
        return redirect("poker:player_detail", pk=player.pk)

    form = PlayerObservationForm(request.POST)
    if form.is_valid():
        obs = form.save(commit=False)
        obs.player = player
        obs.save()
        messages.success(request, "Observation added.")
    else:
        # Keep it simple: show first error in a flash message
        # (If you want, we can re-render detail with modal opened + errors.)
        messages.error(request, "Could not add observation. Please check the fields.")

    return redirect("poker:player_detail", pk=player.pk)


@login_required
def observation_create(request, player_pk):
    player = get_object_or_404(PlayerProfile, pk=player_pk)

    if request.method == "POST":
        form = PlayerObservationForm(request.POST)
        if form.is_valid():
            obs = form.save(commit=False)
            obs.player = player
            obs.save()
            messages.success(request, "Observation added.")
            return redirect("poker:player_detail", pk=player.pk)
    else:
        form = PlayerObservationForm()

    return render(request, "poker/child_form.html", {
        "form": form,
        "title": f"Add Observation: {player.display_name}",
        "cancel_url": reverse("poker:player_detail", kwargs={"pk": player.pk}),
    })


@login_required
def observation_update(request, pk):
    obs = get_object_or_404(PlayerObservation, pk=pk)
    player = obs.player

    if request.method == "POST":
        form = PlayerObservationForm(request.POST, instance=obs)
        if form.is_valid():
            form.save()
            messages.success(request, "Observation updated.")
            return redirect("poker:player_detail", pk=player.pk)
    else:
        form = PlayerObservationForm(instance=obs)

    return render(request, "poker/child_form.html", {
        "form": form,
        "title": f"Edit Observation: {player.display_name}",
        "cancel_url": reverse("poker:player_detail", kwargs={"pk": player.pk}),
    })


@login_required
def observation_delete(request, pk):
    obs = get_object_or_404(PlayerObservation, pk=pk)
    player = obs.player

    if request.method == "POST":
        obs.delete()
        messages.success(request, "Observation deleted.")
        return redirect("poker:player_detail", pk=player.pk)

    return render(request, "poker/confirm_delete.html", {
        "object": obs,
        "cancel_url": reverse("poker:player_detail", kwargs={"pk": player.pk}),
    })


# --- Tendencies ---

@login_required
def tendency_create(request, player_pk):
    player = get_object_or_404(PlayerProfile, pk=player_pk)

    if request.method == "POST":
        form = PlayerTendencyForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.player = player
            t.save()
            messages.success(request, "Tendency added.")
            return redirect("poker:player_detail", pk=player.pk)
    else:
        form = PlayerTendencyForm()

    return render(request, "poker/child_form.html", {
        "form": form,
        "title": f"Add Tendency: {player.display_name}",
        "cancel_url": reverse("poker:player_detail", kwargs={"pk": player.pk}),
    })


@login_required
def tendency_update(request, pk):
    t = get_object_or_404(PlayerTendency, pk=pk)
    player = t.player

    if request.method == "POST":
        form = PlayerTendencyEditForm(request.POST, instance=t)
        if form.is_valid():
            form.save()
            messages.success(request, "Tendency updated.")
            return redirect("profiles:player_detail", pk=player.pk)
    else:
        form = PlayerTendencyEditForm(instance=t)

    return render(request, "profiles/child_form.html", {
        "form": form,
        "title": f"Edit Tendency: {player.display_name} ({t.get_metric_display}{' - ' + t.get_street_display if t.street else ''})",
        "cancel_url": reverse("profiles:player_detail", kwargs={"pk": player.pk}),
    })


@login_required
def tendency_delete(request, pk):
    t = get_object_or_404(PlayerTendency, pk=pk)
    player = t.player

    if request.method == "POST":
        t.delete()
        messages.success(request, "Tendency deleted.")
        return redirect("poker:player_detail", pk=player.pk)

    return render(request, "poker/confirm_delete.html", {
        "object": t,
        "cancel_url": reverse("poker:player_detail", kwargs={"pk": player.pk}),
    })
    
@login_required
def exploit_press(request, player_pk):
    player = get_object_or_404(PlayerProfile, pk=player_pk)
    if request.method != "POST":
        return redirect("poker:player_detail", pk=player.pk)

    name = (request.POST.get("name") or "").strip()
    desc = (request.POST.get("desc") or "").strip()

    if not name:
        messages.error(request, "Missing exploit.")
        return redirect("poker:player_detail", pk=player.pk)

    tag, _ = ExploitTag.objects.get_or_create(name=name, defaults={"description": desc})

    link, created = PlayerExploit.objects.get_or_create(
        player=player,
        tag=tag,
        defaults={"strength": 1, "confidence": 3},
    )

    if not created:
        link.strength = min(10, link.strength + 1)
        link.confidence = min(5, link.confidence + 1)
        link.save(update_fields=["strength", "confidence", "updated"])
        messages.success(request, "Exploit reinforced (+1 strength).")
    else:
        messages.success(request, "Exploit added.")

    return redirect("poker:player_detail", pk=player.pk)

@login_required
def exploit_update(request, pk):
    obj = get_object_or_404(PlayerExploit, pk=pk)
    player = obj.player

    if request.method == "POST":
        form = PlayerExploitEditForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Exploit updated.")
            return redirect("profiles:player_detail", pk=player.pk)
    else:
        form = PlayerExploitEditForm(instance=obj)

    return render(request, "profiles/child_form.html", {
        "form": form,
        "title": f"Edit Exploit: {player.display_name} — {obj.tag.name}",
        "cancel_url": reverse("profiles:player_detail", kwargs={"pk": player.pk}),
    })


@login_required
def exploit_delete(request, pk):
    obj = get_object_or_404(PlayerExploit, pk=pk)
    player = obj.player

    if request.method == "POST":
        obj.delete()
        messages.success(request, "Exploit deleted.")
        return redirect("profiles:player_detail", pk=player.pk)

    return render(request, "profiles/confirm_delete.html", {
        "object": obj,
        "cancel_url": reverse("profiles:player_detail", kwargs={"pk": player.pk}),
    })


@login_required
def poker_notes(request):
    q = (request.GET.get("q") or "").strip()
    keyword = (request.GET.get("keyword") or "").strip()
    important_only = request.GET.get("important") == "1"
    edit_pk = (request.GET.get("edit") or "").strip()

    editing_note = None
    if edit_pk:
        editing_note = get_object_or_404(PokerNote, pk=edit_pk, player=request.user)

    notes = PokerNote.objects.filter(player=request.user).select_related("session").prefetch_related("keywords")

    if q:
        notes = notes.filter(
            Q(title__icontains=q)
            | Q(note__icontains=q)
            | Q(keywords__name__icontains=q)
        ).distinct()

    if keyword:
        notes = notes.filter(keywords__name__iexact=keyword)

    if important_only:
        notes = notes.filter(is_important=True)

    create_form = PokerNoteForm(user=request.user)
    edit_form = PokerNoteForm(instance=editing_note, user=request.user) if editing_note else None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update":
            note_id = request.POST.get("note_id")
            target_note = get_object_or_404(PokerNote, pk=note_id, player=request.user)
            edit_form = PokerNoteForm(request.POST, instance=target_note, user=request.user)
            editing_note = target_note
            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, "Poker note updated.")
                return redirect("poker:poker_notes")
        else:
            create_form = PokerNoteForm(request.POST, user=request.user)
            if create_form.is_valid():
                create_form.save()
                messages.success(request, "Poker note saved.")
                return redirect("poker:poker_notes")

    popular_keywords = (
        PokerNoteKeyword.objects.filter(notes__player=request.user)
        .annotate(total=Count("notes"))
        .order_by("-total", "name")[:20]
    )

    return render(request, "poker/notes.html", {
        "create_form": create_form,
        "edit_form": edit_form,
        "editing_note": editing_note,
        "notes": notes,
        "q": q,
        "keyword": keyword,
        "important_only": important_only,
        "popular_keywords": popular_keywords,
    })


@login_required
def poker_note_edit(request, pk):
    note = get_object_or_404(PokerNote, pk=pk, player=request.user)

    if request.method == "POST":
        form = PokerNoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Poker note updated.")
            return redirect("poker:poker_notes")
    else:
        form = PokerNoteForm(instance=note, user=request.user)

    return render(request, "poker/child_form.html", {
        "form": form,
        "title": "Edit Poker Note",
        "cancel_url": reverse("poker:poker_notes"),
    })


@login_required
def poker_note_delete(request, pk):
    note = get_object_or_404(PokerNote, pk=pk, player=request.user)

    if request.method == "POST":
        note.delete()
        messages.success(request, "Poker note deleted.")
        return redirect("poker:poker_notes")

    return render(request, "poker/confirm_delete.html", {
        "object": note,
        "cancel_url": reverse("poker:poker_notes"),
    })