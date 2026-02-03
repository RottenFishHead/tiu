from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.contrib.auth import views as auth_views
from blog.views import index

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('expenses/', include('expenses.urls')),
    path('income/', include('income.urls')),
    path('poker/', include('poker.urls')),
    path('john/', include('john.urls')),
    path('todo/', include('todo.urls')),
    path('blog/', include('blog.urls')),
    path('hands/', include('hands.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
elif settings.SERVE_MEDIA:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
