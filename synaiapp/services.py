from django.conf import settings
from .models import Song, Artist, AudioFeatures
import requests

class SpotifyRequestManager:
    """
    This class handles the request to the spotify API.
    You need to pass the access token as the constructor
    auth['access_token']
    """   
    def __init__(self, user_auth):
        self.user_auth = user_auth

    def get_track(self, req_song_id):
        response = requests.get(settings.SPOTIFY_BASE_URL + "tracks/" + req_song_id, params={'access_token' : self.user_auth})
        return response.status_code, response.text

    def get_analysis(self, song_id):
        response = requests.get(settings.SPOTIFY_BASE_URL + "audio-features/" + song_id, params={'access_token' : self.user_auth})
        return response.status_code, response.text

def song_factory(api_response, audio_features_response):
    audio_features = AudioFeatures.create(audio_features_response)
    song = Song.create(api_response['id'], api_response['name'], audio_features)
    song.save()

    for artist_json in api_response['artists']:
        artist = Artist.get_artist(artist_json['id'])
        artist.save()
        song.artists.add(artist)
    return song