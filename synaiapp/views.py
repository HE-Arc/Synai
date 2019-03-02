from django.shortcuts import render
from django.views import generic, View
from django.views.generic import ListView

# User manipulation
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required



from .models import Song, AudioFeatures

def home(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    return render(request, 'home.html')

class SongsListView(generic.ListView):
    model = Song
    template_name="songs_list.html"

class FeedView(generic.TemplateView):
    template_name = "feed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add context data
        return context

class HistoryView(generic.TemplateView):
    template_name = "history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add context data
        return context

class DashboardView(generic.TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add context data
        return context