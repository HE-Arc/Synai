from django.conf import settings
from social_django.utils import load_strategy
from .models import Song, Artist, AudioFeatures
import requests
import json

class SpotifyRequestManager:
    """
    This class handles the request to the spotify API.
    You need to pass the social auth infos to the constructor such as :
    social = request.user.social_auth.get(provider="spotify")
    """   
    def __init__(self, social):
        self.social = social

    def refresh_access_token(self):
        """
        A simple function that refreshes the Spotify access token provided to the object using social_django
        """
        strategy = load_strategy()
        self.social.refresh_token(strategy)

    def get_song(self, spotify_id):
        """
        This method will refresh the token, request a song to the API and save it in the database along with the artist, if not already saved
        2 requests will be sent to the API, one for the song and artist(s) and the audio features
        """
        self.refresh_access_token()
        response = requests.get(settings.SPOTIFY_BASE_URL + "tracks/" + spotify_id, params={'access_token' : self.social.extra_data['access_token']})
        song = self.song_factory(api_response=response.text)
        return song

    def get_audio_features(self, song_id):
        """
        This method should be called as you request a song to the API
        It requests the audio features such as acousticness, danceability, etc. to the API
        The audio features object will then be built and returned
        Given the spotify unique ID (song_id)
        """
        response = requests.get(settings.SPOTIFY_BASE_URL + "audio-features/" + song_id, params={'access_token' : self.social.extra_data['access_token']})
        audio_features = self.audio_features_factory(api_response=response.text)
        return audio_features


    def song_factory(self, api_response):
        """
        This method is a helper ""factory"" to build a song
        It will request the audio features and check if artists exist in the DB already, if not build them and save them into the DB
        The AudioFeatures for the song will be requested to the API
        """
        json_response = json.loads(api_response)
        artists = self.artists_factory(json_response['artists'])
        audio_features = self.get_audio_features(json_response['id'])
        
        song = Song.create(json_response['id'], json_response['name'], audio_features)
        song.save()
        [song.artists.add(artist) for artist in artists]
        
        return song
    
    def artists_factory(self, artists_dict):
        """
        This method fetches artists from the DB or the API
        The parameter artists_dict is a dictionary loaded from the JSON returned by the API
        If they are not in the DB, they will saved into it
        It does not need to request further informations to the API 
        """
        artists = []

        for artist_json in artists_dict:
            artist = Artist.get_artist(artist_json['id'])
            if(artist == None):
                artist = Artist.create(artist_json['id'], artist_json['name'])
                artist.save()
            artists.append(artist)
        return artists

    def audio_features_factory(self, api_response):
        """
        This method builds an AudioFeature object from the dictionary given as parameter
        The dictionary is built from the JSON returned by the API
        """
        j_vals = json.loads(api_response)
        audio_features = AudioFeatures.create(j_vals)
        audio_features.save()
        return audio_features
  


     

    