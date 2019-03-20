from django.db import models
from django.contrib.auth.models import User
from functools import reduce
from django.utils import timezone
import json

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
        af = cls()
        af.acousticness = audio_features['acousticness']
        af.danceability = audio_features['danceability']
        af.energy = audio_features['energy']
        af.instrumentalness = audio_features['instrumentalness']
        af.liveness = audio_features['liveness']
        af.valence = audio_features['valence']
        af.speechiness = audio_features['speechiness']
        af.tempo = audio_features['tempo']

        return af

class Artist(models.Model):
    spotify_id = models.CharField(max_length=100)
    artist_name = models.CharField(max_length=255)

    @classmethod
    def get_artist(cls, artist_id):
        artist = Artist.objects.filter(spotify_id=artist_id).first()
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
    def get_song(cls, song_req_id):
        return cls.objects.filter(spotify_id=song_req_id).first()

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
    def analyseSongsForUser(cls, listSong):
        """
        Analyse a list of songs for a user and return the summary
        """
        # Doit être dans feedView !
        audio_features = [song.audio_features for song in listSong]
        return AudioFeatures.summarise(audio_features)
    