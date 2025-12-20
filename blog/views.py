from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage,\
                                  PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, PostForm
from expenses.models import Expense, FixedExpense, Budget, Category
from income.models import Income
from poker.models import PokerSession
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import calendar
from datetime import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, F, DecimalField, Value
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.utils.text import slugify


@login_required
def index(request):
    current_month = timezone.now().month
    current_year = timezone.now().year
    current_month_name = calendar.month_name[current_month]
    expenses = Expense.objects.filter(created__month=current_month, created__year=current_year)
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] 
    fixed_expenses = FixedExpense.objects.aggregate(Sum('amount'))['amount__sum']
    all_expenses =     (
    fixed_expenses + total_expenses if total_expenses != 0 else Decimal(0)
) if fixed_expenses is not None and total_expenses is not None else Decimal(0)
    
    #income calculations
    monthly_incomes = Income.objects.filter(created__month=current_month, created__year=current_year)
    total_monthly_income = monthly_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    differential = total_monthly_income - all_expenses
    #Poker calculations
    sessions =  PokerSession.objects.filter(date__month=current_month, date__year=current_year)
    overall_cash = sessions.aggregate(Sum('cash_out'))['cash_out__sum']
    overall_buyin = sessions.aggregate(Sum('buy_in'))['buy_in__sum']
    if overall_cash is None and overall_buyin is None:
        overall_earned = Decimal(0)
    else:
        overall_earned = (overall_cash or Decimal(0)) - (overall_buyin or Decimal(0))
    overall_hours = sessions.aggregate(Sum('hours'))['hours__sum']
    overall_earned = overall_earned or Decimal(0)
    overall_hours = overall_hours or Decimal(0)
    overall_hourly_rate = (
    overall_earned/ overall_hours if overall_hours != 0 else Decimal(0)
) if overall_earned is not None and overall_hours is not None else Decimal(0)
    
    
    #Budget calcs
    today = datetime.now()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    categories = Category.objects.all()
    
    expenses = Expense.objects.filter(created__range=(first_day_of_month, last_day_of_month)) \
                              .values('category')\
                              .annotate(total_expenses=Coalesce(Sum('amount'), Value(0, output_field=DecimalField())))
    
    budgets = Budget.objects.all()\
                            .values('category')\
                            .annotate(total_budget=Coalesce(Sum('amount'), Value(0, output_field=DecimalField())))
    
    total_expenses_all = sum(item['total_expenses'] for item in expenses)
    total_budget_all = sum(item['total_budget'] for item in budgets)
    remaining_total = total_budget_all - total_expenses_all if total_expenses_all != 0 else Decimal(0)

    budget_remaining = []
    for category in categories:
        total_expenses = next((item['total_expenses'] for item in expenses if item['category'] == category.id), 0)
        total_budget = next((item['total_budget'] for item in budgets if item['category'] == category.id), 0)
        total_expenses = total_expenses or Decimal(0)
        total_budget = total_budget or Decimal(0)

        remaining_budget = total_budget - total_expenses
        budget_remaining.append({
            'category_name': category.name,
            'total_budget': total_budget,
            'total_expenses': total_expenses,
            'remaining_budget': remaining_budget
            
        })
   

    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'fixed_expenses': fixed_expenses,
        'all_expenses': all_expenses,
        'all_income': total_monthly_income,
        'differential': differential,
        'overall_hourly_rate': overall_hourly_rate,
        'overall_hours': overall_hours,
        'overall_total': overall_earned,
        'current_month_name': current_month_name,
        'current_year': current_year,
        'budget_remaining': budget_remaining, 
        'total_expenses_all': total_expenses_all, 
        'total_budget_all': total_budget_all, 
        'remaining_total': remaining_total

    }
    return render(request, 'blog/index.html', context)


def post_list(request):
    post_list = Post.published.all()
    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,
                 'blog/post/list.html',
                 {'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form})


class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, \
                                   status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'kjsonnenberg@gmail.com',
                      [cd['to']])
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, \
                                   status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(request, 'blog/post/comment.html',
                           {'post': post,
                            'form': form,
                            'comment': comment})


@login_required
def post_create(request):
    """View to create a new blog post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:post_detail', 
                          year=post.publish.year,
                          month=post.publish.month,
                          day=post.publish.day,
                          post=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'blog/post/post_form.html', {
        'form': form,
        'title': 'Create New Post'
    })


@login_required
def post_edit(request, post_id):
    """View to edit an existing blog post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Only allow the author to edit
    if post.author != request.user:
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail',
                          year=post.publish.year,
                          month=post.publish.month,
                          day=post.publish.day,
                          post=post.slug)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post/post_form.html', {
        'form': form,
        'post': post,
        'title': 'Edit Post'
    })


@login_required
def post_delete(request, post_id):
    """View to delete a blog post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Only allow the author to delete
    if post.author != request.user:
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        post.delete()
        return redirect('blog:post_list')
    
    return render(request, 'blog/post/post_confirm_delete.html', {
        'post': post
    })
