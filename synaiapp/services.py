from django.conf import settings
from urllib.parse import urlencode
from social_django.utils import load_strategy
from .models import Song, Artist, AudioFeatures, Album
import random
import requests

class SpotifyRequestManager:
    """
    This class handles the request to the spotify API.
    You need to pass the social auth infos to the constructor such as :
    social = request.user.social_auth.get(provider="spotify")
    """

    """
    This is a helper dictionary that builds the API path of different resources 
    """
    def __init__(self, social):
        self.social = social
        self.refresh_access_token()
        
        self.p_builder = {
            "album" : lambda album_id : "albums/" + album_id,
            "album_tracks" : lambda album_id : self.p_builder['album'](album_id) + "/tracks",
            "track" : lambda track_id : "tracks/" + track_id,
            "tracks" : "tracks?",
            "audio-features" : lambda track_id : "audio-features/" + track_id,
            "artist" : lambda artist_id : "artists/" + artist_id,
            "artists": "artists?",
            "artist_top" : lambda artist_id : self.p_builder['artist'](artist_id) + "/top-tracks?",
            "playlist" : lambda playlist_id : "playlists/" + playlist_id + "/tracks",
            "search" : "search?",
            "recommendations" : "recommendations?",
            "user_playlists" : lambda user_id : "users/" + user_id + "/playlists",
            "current_user_history" : "me/player/recently-played"
        }
        # this is a dict that is used for the search in the Spotify API
        # it builds the list of items using the JSON and methods in the class
        self.search_builder = {
            "tracks" : lambda r_data : self.get_songs([json['id'] for json in r_data['items']]),
            "albums" : lambda r_data : [self.get_album(json['id']) for json in r_data['items']],
            "artists" : lambda r_data : self.get_artists([json['id'] for json in r_data['items']], r_data['items']),
            #"playlists" : get_playlist,
        }

    def refresh_access_token(self):
        """
        A simple function that refreshes the Spotify access token provided to the object using social_django
        """
        strategy = load_strategy()
        self.social.refresh_token(strategy)

    def query_executor(self, query_path, query_dict=None):
        """
        This method executes a query given the adress's path (IE .../album/)
        The query_dict is the list of parameters that can be added and encoded in the query
        It returns the response's text in a JSON encoded form
        """
        query = settings.SPOTIFY_BASE_URL + query_path

        if(query_dict != None):
            query += '?' if query[-1:] != '?' else ''
            query += urlencode(query_dict)
        response = requests.get(query, params={'access_token' : self.social.extra_data['access_token']})
        
        if(response.status_code == 503):
            raise Exception("Spotify API is temporarily unavailable. Please retry in a few minutes")
        if(response.status_code == 429):
            raise Exception("Spotify API rate limit reached. Check the \"Retry-After\" header to check how many seconds you have to wait.")
        if(response.status_code != 200):
            raise Exception(f"Something went wrong...\nError: {response.status_code}\nMessage: {response.text}")
        
        return response.json()

    def get_songs(self, spotify_ids, album=None, songs_payload=None):
        """
        This method checks in the DB if the songs (spotify_ids) exists. If not, it builds them and returns them
        """
        # remove the None ids that can happen when we get an user's playlist with local songs for example
        spotify_ids = filter(None, spotify_ids)

        spotify_ids = [id.split(':')[-1] for id in spotify_ids]

        songs = list(Song.objects.filter(spotify_id__in=spotify_ids))

        missing_ids = list(set(spotify_ids) - set([song.spotify_id for song in songs]))
        # if we have missing ids we query the API
        if(len(missing_ids) != 0):
            # we subdivide the missing ids list into chunks because the API can give up to 50 tracks at the same time
            sub_lists = [missing_ids[id:id+settings.MAX_REQ_IDS] for id in range(0, len(missing_ids), settings.MAX_REQ_IDS)]
            for sub_list_ids in sub_lists:
                query_dict = {
                    'ids': ','.join(sub_list_ids)
                }
                response = self.query_executor(self.p_builder['tracks'], query_dict)
                missing_songs = [self.song_factory(json_track) for json_track in response['tracks']]
                # builds each track for each json slice in the api response
                songs.extend(missing_songs)

        return songs

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
        """
        This method checks in the DB if a specific album (album_id) exists. If not, it builds it and returns it
        You can specify data in a JSON form for a previous request to prevent multiple API acesses for no reason
        """
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
        response = self.query_executor(self.p_builder['album_tracks'](album_id))
        album = Album.get_album(album_id)
        return self.get_songs([json_track['id'] for json_track in response['items']])

    def get_artists(self, artist_ids, request_payload = None):
        """
        This method checks in the database if a list of artists (artist_ids) exist
        If they don't they are queried to the API
        The request_payload can be used to provide a previous request result that contains the data we need
        """
        artists = []
        
        if(request_payload == None):
            query_dict = {}
            query_dict['ids'] = ','.join(artist_ids)
            request_payload = self.query_executor(self.p_builder['artists'], query_dict)['artists']

        for id, artist_payload in zip(artist_ids, request_payload):
            artist = Artist.get_artist(id)
            if(artist == None):
                artist = self.artists_factory(id, artist_payload)
            artists.append(artist)
        return artists
    
    def get_artist_top_songs(self, artist_id):
        """
        This method uses the artist_id given as parameter and gets its top songs
        Builds and saves in the DB the artist and songs
        """
        artist = Artist.get_artist(artist_id)
        if(artist == None):
            artist = self.get_artists([artist_id])[0]
        
        # yeah it's static right now we have like 5 days before project is due
        query_dict = {'country':'CH'}

        response = self.query_executor(self.p_builder['artist_top'](artist_id), query_dict)
        return self.get_songs([json_track['id'] for json_track in response['tracks']])


    def get_playlist(self, playlist_id):
        """
        Get the songs of a playlist using the playlist id.
        Builds and saves in the DB the artists and songs
        """
        response = self.query_executor(self.p_builder['playlist'](playlist_id))
        return self.get_songs([json_track['track']['id'] for json_track in response['items']])


    @classmethod
    def get_playlist_json_as_dict(cls, json_playlist):
        return {
            "id" : json_playlist['id'],
            "image_url" : json_playlist['images'][0]['url'],
            "name" : json_playlist['name'],
            "owner" : json_playlist['owner']['display_name'],
            "nb_tracks" : json_playlist['tracks']['total'],
        }


    def get_user_playlists(self, user_id, limit=20):
        """
        Get the user's playlist using its uid.
        This method return a list of dictionnary of playlist
        """
        query_dict = {
            'limit': 50
        }
        response = self.query_executor(self.p_builder['user_playlists'](user_id), query_dict)
        return [SpotifyRequestManager.get_playlist_json_as_dict(json_playlist) for json_playlist in response['items']]

    def get_recommendations(self, analysis, limit=10):
        """
        This method returns songs (10 by default) recommended by the API given some parameters
        It uses the analysed features and songs as seed to get them
        """
        songs = analysis.songs.all()
        audio_features = analysis.summarised_audio_features
        query_dict = {}
        #cant use generator unfortunately for memory it would be better
        track_seeds = random.sample([song.spotify_id for song in songs], settings.MAX_SEED_OBJECTS)

        query_dict['seed_tracks'] = ','.join(track_seeds)
        for attr in audio_features.features_headers()[:-1]:
            attr_lower = attr.lower()
            val = getattr(audio_features, attr_lower)
            val_min = val - settings.FEATURES_DELTA
            val_max = val + settings.FEATURES_DELTA
            query_dict['min_' + attr_lower] = 0 if val_min < 0 else val_min
            query_dict['max_' + attr_lower] = 1 if val_max > 1 else val_max 

        query_dict['limit'] = limit

        recommended_tracks = self.query_executor(self.p_builder['recommendations'], query_dict)
        songs = self.get_songs((track['id'] for track in recommended_tracks['tracks']))
        return songs

    def get_current_user_history(self):
        """
        Get the 20 recently played songs of the current user
        """
        response = self.query_executor(self.p_builder['current_user_history'])
        return self.get_songs([json_track['track']['id'] for json_track in response['items']])


    def search_item(self, query_item, item_types, limit=5):
        """
        Search on the API for an item.
        Type is track, artist, playlist, album, etc.
        """
        query_dict = {}
        query_dict['q'] = query_item
        query_dict['type'] = ','.join(item_types)
        query_dict['limit'] = str(limit)

        response = self.query_executor(self.p_builder['search'], query_dict)

        # items are songs, artists, albums, playlists, etc.
        items = {}
        for item_type in response:
            # each item's list will be built using its JSON slice
            items[item_type] = self.search_builder[item_type](response[item_type])

        return items

    def song_factory(self, json_response, album=None):
        """
        This method is a helper ""factory"" to build a song
        It will request the audio features and check if artists exist in the DB already, if not build them and save them into the DB
        The AudioFeatures, for the song will be requested to the API
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
        """
        This method build an album and saves it into the DB given a JSON Spotify API response
        """
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
  


     

    