from urllib import request

from django.shortcuts import render
from django.views import generic, View
from django.views.generic import ListView
from rest_framework.exceptions import ValidationError

# User manipulation
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from social_django.models import UserSocialAuth

# Services
from .services import SpotifyRequestManager

# Python utils
import re

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
    return render(request, "api_request_error_500.html", status=500)

def error_400(request):
    return render(request, "api_request_error_400.html", status=400)

class SingleSongView(generic.TemplateView):
    model = Song
    template_name = "song_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song_id = self.kwargs['id']
        song = Song.get_song(song_id)
        if(song == None):
            print("Song does not exists in the DB... Going to the API")
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
        context = super().get_context_data(**kwargs)
        manager = request_manager_factory(request)
        user_id = self.request.user.social_auth.get(provider="spotify").uid

        # History
        songs_history = manager.get_current_user_history()
        context['user_history'] = Song.get_songs_with_artists_and_album_names(songs_history)
        
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
        context["analysis_dataset"] = dict(zip([analy.id for analy in analysis], [analy.history_dataset(analy.songs.all()) for analy in analysis]))
        return render(request, HistoryView.template_name, context)

class DashboardView(generic.TemplateView):
    template_name = "dashboard.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data()

        context["username"] = self.request.user.first_name
        context["summarised_dataset"] = Analysis.get_user_summarised_data(self.request.user)

        return render(request, DashboardView.template_name, context)

@method_decorator(login_required, name='dispatch')
class SearchResultsView(generic.TemplateView):
    template_name = "_items/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = request_manager_factory(self.request)

        search_input = self.request.GET.get('search_input')

        search_result = manager.search_item(search_input, ['track', 'album', 'artist'])

        context['tracks'] = search_result['tracks']
        context['albums'] = search_result['albums']
        context['artists'] = search_result['artists']

        return context

class AnalyseResultsView(generic.TemplateView):
    template_name = "_items/analyse_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = request_manager_factory(self.request)

        self.request_type = {
            'song': lambda song_id: manager.get_songs([song_id]),
            'playlist': lambda playlist_id: manager.get_playlist(playlist_id),
            'artist': lambda artist_id: manager.get_artist_top_songs(artist_id),
            'history' : manager.get_current_user_history()
        }

        datasource_id = self.request.GET.get('id')
        datasource_name = self.request.GET.get('name')
        datasource_type = self.request.GET.get('type')

        # Request the songs depending the datasource
        if datasource_type == "history":
            songs = self.request_type['history']
            datasource_name = 'Recently played'
        else :
            # Verify ID integrity (15-30 char in base 62)
            match = re.match('[a-zA-Z0-9]{15,30}',datasource_id)
            if match is None:
                raise ValidationError
            try: 
                songs = self.request_type[datasource_type](datasource_id)
            except KeyError:
                raise ValidationError

        # Analyse the songs ! 
        analysis, audio_features = Analysis.analyse_songs_for_user(songs, self.request.user, datasource_type)

        # For graph use
        context["audio_features"] = audio_features
        context["stats"] = analysis.summarised_audio_features.as_array()
        context["stats_headers"] = AudioFeatures.features_headers()
        context["name"] = datasource_name

        # TODO Get correct recommandations
        context["recommandations"] = manager.get_recommendations(analysis)

        return context
    
@method_decorator(login_required, name='dispatch')
class PlaylistEntriesView(generic.TemplateView):
    template_name = "_items/playlist_entries.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = request_manager_factory(self.request)
        user_id = self.request.user.social_auth.get(provider="spotify").uid

        # Playlists
        context['user_playlists'] = manager.get_user_playlists(user_id)
        
        return context
    
