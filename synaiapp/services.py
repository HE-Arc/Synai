from django.conf import settings
from urllib.parse import urlencode
from social_django.utils import load_strategy
from .models import Song, Artist, AudioFeatures, Album
import requests
import json

# https://stackoverflow.com/questions/3738381/what-do-i-do-when-i-need-a-self-referential-dictionary
class SpotifyRequestManager:
    """
    This class handles the request to the spotify API.
    You need to pass the social auth infos to the constructor such as :
    social = request.user.social_auth.get(provider="spotify")
    """

    """
    This is a helper dictionary that builds the API path of different resources 
    """
    p_builder = {
        "album" : lambda album_id : "albums/" + album_id,
        "album_tracks" : lambda album_id : "albums/" + album_id + "/tracks",
        #"album_tracks" : lambda album_id : p_builder['album'](album_id), + "/tracks" # this doesn't work unfortunately
        "track" : lambda track_id : "tracks/" + track_id,
        "audio-features" : lambda track_id : "audio-features/" + track_id,
        "artist" : lambda artist_id : "artists/" + artist_id,
    }

    search_builder = {
        "tracks" : "get_song",
        "albums" : "get_album",
        "artists" : "get_artists",
        "playlists" : "get_playlists"
    }

    def __init__(self, social):
        self.social = social
        self.refresh_access_token()

    def refresh_access_token(self):
        """
        A simple function that refreshes the Spotify access token provided to the object using social_django
        """
        strategy = load_strategy()
        self.social.refresh_token(strategy)

    def query_executor(self, query_path, query_dict=None):
        query = settings.SPOTIFY_BASE_URL + query_path
        if(not(query_dict == None)):
            query += urlencode(query_dict)

        response = requests.get(query, params={'access_token' : self.social.extra_data['access_token']})
        return json.loads(response.text)

    def get_song(self, spotify_id, album=None):
        """

        """
        song = Song.get_song(spotify_id)
        if(song == None):
            response = self.query_executor(self.p_builder['track'](spotify_id))
            song = self.song_factory(response, album)
        return song

    def get_audio_features(self, song_id):
        """
        This method should be called as you request a song to the API
        It requests the audio features such as acousticness, danceability, etc. to the API
        The audio features object will then be built and returned
        Given the spotify unique ID (song_id)
        """
        response = self.query_executor(self.p_builder['audio-features'](song_id))
        audio_features = self.audio_features_factory(response)
        return audio_features

    def get_album(self, album_id, request_payload=None):
        album = Album.get_album(album_id)
        if(album == None):
            if(request_payload == None):
                request_payload = self.query_executor(self.p_builder['album'](album_id))
            album = self.album_factory(request_payload)
        return album

    def get_album_tracks(self, album_id):
        """
        This method should be called as you request a song to the API
        It requests the album tracks 
        The audio features object will then be built and returned
        Given the spotify unique ID (song_id)
        """
        songs = []
        response = self.query_executor(self.p_builder['album_tracks'](album_id))
        album = Album.get_album(album_id)
        for json_track in response['items']:
            song = self.get_song(json_track['id'], album)
            songs.append(song)
        return songs

    def get_artists(self, artist_ids, request_payload = None):
        artists = []

        for id, artist_payload in zip(artist_ids, request_payload):
            artist = Artist.get_artist(id)
            if(artist == None):
                if(artist_payload == None):
                    artist_payload = self.query_executor(self.p_builder['artist'](id))
                artist = self.artists_factory(id, artist_payload)
            artists.append(artist)
        return artists

    def search_item(self, query_item, item_types, limit=5):
        """
        Search on the API for an item.
        Type is track, artist, playlist, album, etc.
        """
        query_dict = {}
        query_dict['q'] = query_item
        query_dict['type'] = ','.join(item_types)
        query_dict['limit'] = str(limit)

        response = self.query_executor("search?", query_dict)

    def song_factory(self, json_response, album=None):
        """
        This method is a helper ""factory"" to build a song
        It will request the audio features and check if artists exist in the DB already, if not build them and save them into the DB
        The AudioFeatures for the song will be requested to the API
        """
        artist_ids = [artist_dict['id'] for artist_dict in json_response['artists']]
        artists = self.get_artists(artist_ids, json_response['artists'])
        if(album == None):
            album = self.get_album(json_response['album']['id'], json_response['album'])
        audio_features = self.get_audio_features(json_response['id'])
        
        song = Song.create(json_response['id'], json_response['name'], audio_features, album)
        song.save()
        [song.artists.add(artist) for artist in artists]

        return song
    
    def album_factory(self, album_dict):
        album = Album.create(album_dict['id'], album_dict['name'])
        album.save()
        return album

    def artists_factory(self, artist_id, artists_dict=None):
        """
        This method fetches artists from the DB or the API
        The parameter artists_dict is a dictionary loaded from the JSON returned by the API
        If they are not in the DB, they will saved into it
        It does not need to request further informations to the API 
        """

        artist = None


        artist = Artist.create(artists_dict['id'], artists_dict['name'])
        artist.save()
        return artist

    def audio_features_factory(self, api_response):
        """
        This method builds an AudioFeature object from the dictionary given as parameter
        The dictionary is built from the JSON returned by the API
        """
        audio_features = AudioFeatures.create(api_response)
        audio_features.save()
        return audio_features
  


     

    