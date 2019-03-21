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
        return render(request, "dashboard.html")
    return render(request, "home.html")

def request_manager_factory(request):
    """ 
    This method is a helper ""factory"" to build SpotifyRequestManager object
    The user's auth are extracted from the request
    Returns the SpotifyRequestManager object built
    """ 
    social = request.user.social_auth.get(provider="spotify")
    manager  = SpotifyRequestManager(social)
    return manager

class SingleSongView(generic.TemplateView):
    model = Song
    template_name = "song_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song_id = self.kwargs['id']
        song = Song.get_song(song_id)
        if(song == None):
            print("Song does not exists... Going to the API")
            manager = request_manager_factory(self.request)
            song = manager.get_song(song_id)

        context['song'] = song
        context['artists'] = song.artists.all()
        return context
            

class SongsListView(generic.ListView):
    model = Song
    template_name="songs_list.html"

class FeedView(generic.TemplateView):
    template_name = "feed.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # add context data
        audio_features = Analysis.analyseSongsForUser(Song.objects.all())
        context["audio_features"] = audio_features
        context["stats"] = audio_features.asArray()
        context["stats_headers"] = AudioFeatures.featuresHeaders()
        # Get correct recommandations
        context["recommandations"] = Song.objects.all()
        return render(request, FeedView.template_name, context)

class HistoryView(generic.TemplateView):
    template_name = "history.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data()
        sort_by = request.GET.get('sort','')
        if sort_by:
            analysis, songs, audioFeatures = Analysis.getUserHistory(self.request.user)
        else:
            analysis, songs, audioFeatures = Analysis.getUserHistory(self.request.user, order=-1)

        context["analysis"] = analysis
        context["analysis_len"] = len(analysis)
        context["songs"] = songs
        context["all_songs_len"] = len(songs)

        # for graphs use
        context["analysis_dataset"] = dict(zip([analy.id for analy in analysis], [analy.asDataset() for analy in analysis]))
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