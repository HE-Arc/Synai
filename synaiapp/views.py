from django.shortcuts import render
from django.views import generic, View
from django.views.generic import ListView

# User manipulation
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from social_django.models import UserSocialAuth

# Services
from .services import SpotifyRequestManager

# Logger & debug
import logging
logger = logging.getLogger(__name__)

from .models import Song, AudioFeatures, Analysis, Album

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
    manager = SpotifyRequestManager(social)
    return manager

def error_500(request):
    return render(request, "api_request_error.html", status=500)

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
            song = manager.get_songs([song_id])[0]

        context['song'] = song
        context['artists'] = song.artists.all()
        return context
            

class SongsListView(generic.ListView):
    #model = Song
    queryset = Song.objects.prefetch_related('artists').select_related('audio_features').select_related('album').all()
    template_name="songs_list.html"

class FeedView(generic.TemplateView):
    template_name = "feed.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        has_feed = False # TODO determine if has feed (using get param ?, form ?)
        context = super().get_context_data(**kwargs)
        manager = request_manager_factory(request)
        user_id = self.request.user.social_auth.get(provider="spotify").uid

        # Playlists
        context['user_playlists'] = manager.get_user_playlists(user_id)

        context['has_feed'] = has_feed
        if has_feed:
            # TODO add data if present
            pass

        # add context data
        songs = Song.objects.select_related('audio_features').all()
        audio_features = Analysis.analyse_songs_for_user(songs)
        context["audio_features"] = audio_features
        context["stats"] = audio_features.as_array()
        context["stats_headers"] = AudioFeatures.features_headers()
        # Get correct recommandations
        context["recommandations"] = Song.objects.all()[:10]
        return render(request, FeedView.template_name, context)

class HistoryView(generic.TemplateView):
    template_name = "history.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data()
        sort_by = request.GET.get('sort','')
        if sort_by:
            analysis, songs, audio_features = Analysis.get_user_history(self.request.user)
        else:
            analysis, songs, audio_features = Analysis.get_user_history(self.request.user, order=-1)

        context["analysis"] = analysis
        context["analysis_len"] = len(analysis)
        context["songs"] = songs
        context["all_songs_len"] = len(songs)

        # for graphs use
        context["analysis_dataset"] = dict(zip([analy.id for analy in analysis], [analy.history_dataset() for analy in analysis]))
        return render(request, HistoryView.template_name, context)

class DashboardView(generic.TemplateView):
    template_name = "dashboard.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data()

        context["username"] = self.request.user.first_name
        context["summarised_dataset"] = Analysis.get_user_summarised_data(self.request.user)

        return render(request, DashboardView.template_name, context)

class SearchResultsView(generic.TemplateView):
    template_name = "_items/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = request_manager_factory(self.request)
        search_input = self.request.GET.get('search_input')
        search_result = manager.search_item(search_input, ['track'])
        context['tracks'] = search_result['tracks']
        return context
