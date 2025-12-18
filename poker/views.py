from django.shortcuts import render, get_object_or_404, redirect
from .models import PokerSession
from hands.models import Hands
from .forms import PokerSessionForm, DateForm
from django.utils import timezone
from django.db.models import Sum, ExpressionWrapper, F, DurationField
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from plotly.offline import plot
from plotly import graph_objs as go
import plotly.express as px
import pandas as pd
from calendar import month_name




@login_required
def session_detail(request, session_id):
    session = get_object_or_404(PokerSession, id=session_id, player=request.user)
    try:
        hands = Hands.objects.get(session_id=session_id)
    except Hands.DoesNotExist:
        hands = None  # Set hands to None if no hands are found for the session

    context = {
        "session": session,
        "hands": hands
        
    }
    return render(request, 'poker/session_detail.html', context)

@login_required
def edit_session(request, session_id):
    session = get_object_or_404(PokerSession, id=session_id, player=request.user)

    if request.method == 'POST':
        form = PokerSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
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
    if request.method == 'POST':
        form = PokerSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.player = request.user
            session.save()
            return redirect('poker:session_list')
    else:
        form = PokerSessionForm()

    return render(request, 'poker/add_session.html', {'form': form})

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
    
    fig = px.line(
        x=[s.date for s in session],
        y=[s.win_loss for s in session],
        title='Overall Stats',
        labels={'x': 'Date', 'y': 'Win/Loss'}
    )
    fig.update_xaxes(tickangle=45, tickfont=dict(family='Rockwell', color='green', size=14))
    fig.update_layout(title={
        'font_size': 22,
        'xanchor': 'center',

        'x': 0.5
    })
    fig.update_layout(
        autosize=True)
    
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
def session_list_13(request):
    current_month = timezone.now().month
    current_year = timezone.now().year
    requested_month = int(request.GET.get('month', current_month))
    requested_year = int(request.GET.get('year', current_year))
    requested_stakes = request.GET.get('stakes', '13')  # Default to '25' if not provided

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

    return render(request, 'poker/session_list_13.html', {
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
    stakes_filter = request.GET.get('stakes')
    sessions =  PokerSession.objects.filter(player=request.user)
    current_month = timezone.now().month
    current_year = timezone.now().year
  
    
    
    overall_total = sum(session.win_loss for session in sessions)
    overall_hours = sum(session.hours for session in sessions)
    overall_hourly_rate = overall_total / overall_hours if overall_hours > 0 else 0
    
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
    
    fig = px.line(
        x=[s.date for s in sessions],
        y=[s.win_loss for s in sessions],
        title='Overall Stats',
        labels={'x': 'Date', 'y': 'Win/Loss'}
    )
    fig.update_xaxes(tickangle=45, tickfont=dict(family='Rockwell', color='green', size=14))
    fig.update_layout(title={
        'font_size': 22,
        'xanchor': 'center',

        'x': 0.5
    })
    fig.update_layout(
        autosize=True)
    
    chart = fig.to_html()
        
    context = {'chart': chart,
        'overall_hourly_rate': overall_hourly_rate,
        'overall_hours': overall_hours,
        'overall_total': overall_total,
        'current_month': current_month,
        'current_year': current_year,
        'sessions_by_month': sessions_by_month,
        'stakes_filter': stakes_filter,
            }
    return render(request, 'poker/home.html', context)

@login_required
def chart_25(request):
    session =  PokerSession.objects.filter(stakes='25').filter(player=request.user)
    start = request.GET.get('start')
    end = request.GET.get('end')
    stakes = request.GET.get('stakes')
    
    if start:
        session = session.filter(date__gte=start)
    if end:
        session = session.filter(date__lte=end)
    if stakes:
        session = session.filter(stakes=stakes)
    fig = px.line(
        x=[s.date for s in session],
        y=[s.win_loss for s in session],
        title='2/5 Chart',
        labels={'x': 'Date', 'y': 'Win/Loss'}
    )
    fig.update_xaxes(tickangle=45, tickfont=dict(family='Rockwell', color='green', size=14))
    fig.update_layout(title={
        'font_size': 22,
        'xanchor': 'center',

        'x': 0.5
    })
    fig.update_layout(
        autosize=True)
    
    chart = fig.to_html()
        
    context = {'chart': chart,
               'form': DateForm
            }
    return render(request, 'poker/chart_25.html', context)

@login_required
def session_hands(request):
    hands = Hands.objects.all()
    sessions_with_hands = PokerSession.objects.filter(id__in=hands.values('session_id'))
    return render(request, 'poker/session_hands.html', {'sessions': sessions_with_hands})


def all_sessions_chart(request):
    # Fetch data from the database
    sessions = PokerSession.objects.all()

    # Create a DataFrame from the queryset
    data = {
        'date': [session.date for session in sessions],
        'win_loss': [session.win_loss for session in sessions],
    }
    df = pd.DataFrame(data)

    # Group data by date and calculate cumulative sum for win_loss
    df['cumulative_win_loss'] = df.groupby('date')['win_loss'].cumsum()

    # Create the Plotly Express chart
    fig = px.line(df, x='date', y='cumulative_win_loss', title='Win Loss Over Time', labels={'cumulative_win_loss': 'Total Win/Loss', 'date': 'Date'})

    # Customize the layout if needed
    fig.update_layout(title='Win Loss Over Time', xaxis_title='Date', yaxis_title='Total Win/Loss')

    # Convert the Plotly figure to JSON
    chart_json = fig.to_json()

    return render(request, 'poker/all_sessions_chart.html', {'chart_json': chart_json})