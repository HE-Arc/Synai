from django.db import models
from django.contrib.auth.models import User
from functools import reduce
from django.utils import timezone
import json
import requests

class AudioFeatures(models.Model):
    acousticness = models.FloatField()
    danceability = models.FloatField()
    energy = models.FloatField()
    instrumentalness = models.FloatField()
    liveness = models.FloatField()
    valence = models.FloatField()
    speechiness = models.FloatField()
    tempo = models.FloatField()

    manager = models.Manager()

    @classmethod
    def summarise(cls, AudioFeatureList):
        summary = AudioFeatures()
        summary.acousticness = AudioFeatures.mean("acousticness", AudioFeatureList)
        summary.danceability = AudioFeatures.mean("danceability", AudioFeatureList)
        summary.energy = AudioFeatures.mean("energy", AudioFeatureList)
        summary.instrumentalness = AudioFeatures.mean("instrumentalness", AudioFeatureList)
        summary.liveness = AudioFeatures.mean("liveness", AudioFeatureList)
        summary.valence = AudioFeatures.mean("valence", AudioFeatureList)
        summary.speechiness = AudioFeatures.mean("speechiness", AudioFeatureList)
        summary.tempo = AudioFeatures.mean("tempo", AudioFeatureList)
        return summary

    
    @classmethod
    def mean(cls, attribute, AudioFeaturelist):
        return reduce(lambda a, b: a+b, [getattr(x, attribute, 0) for x in AudioFeaturelist]) /len(AudioFeaturelist)
    
    @classmethod
    def create(cls, audio_features):
        j_vals = json.loads(audio_features)

        af = cls()
        af.acousticness = j_vals['acousticness']
        af.danceability = j_vals['danceability']
        af.energy = j_vals['energy']
        af.instrumentalness = j_vals['instrumentalness']
        af.liveness = j_vals['liveness']
        af.valence = j_vals['valence']
        af.speechiness = j_vals['speechiness']
        af.tempo = j_vals['tempo']

        print(type(j_vals))
        return af

class Artist(models.Model):
    spotify_id = models.CharField(max_length=100)
    artist_name = models.CharField(max_length=255)

    @classmethod
    def get_artist(cls, artist_id):
        artist = Artist.objects.filter(spotify_id=artist_id)
        if(not(artist.exists())):
            pass
        return artist
    
    @classmethod
    def create(cls, spotify_id, artist_name):
        artist = cls(spotify_id=spotify_id, artist_name=artist_name)
        return artist


class Song(models.Model):
    spotify_id = models.CharField(max_length=100)
    song_name = models.CharField(max_length=255)
    artists = models.ManyToManyField(Artist)
    audio_features = models.ForeignKey(AudioFeatures, null=True, on_delete=models.SET_NULL)

    @classmethod
    def get_song(cls, song_req_id, auth):
        song = Song.objects.filter(spotify_id=song_req_id)
        if(not(song.exists())):
            print("Song not found going to the API...")
            response = requests.get("" + song_req_id, params={'access_token' : auth['access_token']})
            print("status : ", response.status_code)
            print(response.text)
        return song

    @classmethod
    def create(cls, song_id, song_name, audio_features):
        song = cls(spotify_id = song_id, song_name=song_name, audio_features=audio_features)
        return song

class Analysis(models.Model):
    songs = models.ManyToManyField(Song)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    summarised_audio_features = models.ForeignKey(AudioFeatures, on_delete=models.CASCADE)
    songs_len = models.IntegerField()
    created = models.DateTimeField(default=timezone.now)

    manager = models.Manager()

    @classmethod
    def getUserHistory(cls, user):
        """
        Get the full analysis history of a user
        """
        analysis = Analysis.manager.filter(user=user).all()
        songs = [ana.songs for ana in analysis]
        # audioFeatures = [ ana.summarised_audio_features for ana in analysis]
        audioFeatures = AudioFeatures.manager.all()
        return analysis, songs, audioFeatures

    @classmethod
    def getUserSummary(cls, user):
        """
        Get a summary of all the analysis done for a user
        """
        analysis, songs, audioFeatures = Analysis.getUserHistory(user)
        try:
            return AudioFeatures.summarise(audioFeatures)
        except:
            return None
    
    @classmethod
    def analyseSongsForUser(cls, listSong, user):
        """
        Analyse a list of songs for a user and return the summary
        """
        # Doit être dans feedView !
        pass