from django.conf import settings
from .models import Song, Artist, AudioFeatures
import requests
import json

class SpotifyRequestManager:
    """
    This class handles the request to the spotify API.
    You need to pass the access token as the constructor
    auth['access_token']
    """   
    def __init__(self, user_auth):
        self.user_auth = user_auth

    def get_song(self, spotify_id):
        response = requests.get(settings.SPOTIFY_BASE_URL + "tracks/" + spotify_id, params={'access_token' : self.user_auth})
        song = self.song_factory(api_response=response.text)
        return song

    def get_audio_features(self, song_id):
        response = requests.get(settings.SPOTIFY_BASE_URL + "audio-features/" + song_id, params={'access_token' : self.user_auth})
        audio_features = self.audio_features_factory(api_response=response.text)
        return audio_features


    def song_factory(self, api_response):
        json_response = json.loads(api_response)

        artists = self.artists_factory(json_response['artists'])
        audio_features = self.get_audio_features(json_response['id'])
        
        song = Song.create(json_response['id'], json_response['name'], audio_features)
        song.save()
        [song.artists.add(artist) for artist in artists]
        
        return song
    
    def artists_factory(self, artists_dict):
        artists = []

        for artist_json in artists_dict:
            artist = Artist.get_artist(artist_json['id'])
            if(artist == None):
                artist = Artist.create(artist_json['id'], artist_json['name'])
                artist.save()
            print(artist.artist_name)
            artists.append(artist)
        return artists

    def audio_features_factory(self, api_response):
        j_vals = json.loads(api_response)
        audio_features = AudioFeatures.create(j_vals)
        audio_features.save()
        return audio_features
  


     

    