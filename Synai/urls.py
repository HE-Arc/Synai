"""Synai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from synaiapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('feed', views.FeedView.as_view(), name='feed'),
    path('history', views.HistoryView.as_view(), name='history'),
    path('dashboard', views.DashboardView.as_view(), name='dashboard'),
    path('about', TemplateView.as_view(template_name="about.html"), name="about"),

    # Partial views
    path('search_results', views.SearchResultsView.as_view(), name='search_results'),
    path('analyse', views.AnalyseResultsView.as_view(), name='analyse'),
    path('playlist_entries', views.PlaylistEntriesView.as_view(), name='playlist_entries'),

    # social auth app
    path('social/', include('social_django.urls', namespace='social')),
    path('', include('django.contrib.auth.urls')),  # add logout route
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler500 = "synaiapp.views.error_500"
handler400 = "synaiapp.views.error_400"

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
