from django.shortcuts import render
from django.views import generic, View
from django.views.generic import ListView

# User manipulation
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .services import SpotifyRequestManager

from .models import Song, AudioFeatures, Analysis

def home(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    return render(request, 'home.html')

class SingleSongView(generic.TemplateView):
    model = Song
  
    template_name = "single_song_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        social = self.request.user.social_auth.get(provider="spotify")
        access_token = social.extra_data['access_token']
        #print(access_token)
        manager  = SpotifyRequestManager(access_token)
        status_code, data = manager.get_analysis('11dFghVXANMlKmJXsNCbNl')

        audio_features = AudioFeatures.create(data)
        #songVals = Song.get_song('11dFghVXANMlKmJXsNCbNl', access_token)
        
        return context
            

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

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data()
        analysis, songs, audioFeatures = Analysis.getUserHistory(self.request.user)
        context["analysis"] = analysis
        context["analysis_len"] = len(analysis)
        context["songs"] = songs
        context["all_songs_len"] = len(songs)
        return render(request, HistoryView.template_name, context)


class DashboardView(generic.TemplateView):
    template_name = "dashboard.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {
            "username": "username spotify",
            "summary" : Analysis.getUserSummary(self.request.user)
            }
        return render(request, DashboardView.template_name, context)