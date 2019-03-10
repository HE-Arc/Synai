from django.db import models
from django.contrib.auth.models import User

class AudioFeatures(models.Model):
    acousticness = models.FloatField()
    danceability = models.FloatField()
    energy = models.FloatField()
    instrumentalness = models.FloatField()
    liveness = models.FloatField()
    valence = models.FloatField()
    speechiness = models.FloatField()
    tempo = models.FloatField()

class Song(models.Model):
    spotify_id = models.CharField(max_length=100)
    song_name = models.CharField(max_length=255)
    audio_features = models.ForeignKey(AudioFeatures, null=True, on_delete=models.SET_NULL)

class Analysis(models.Model):
    songs = models.ManyToManyField(Song)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    summarised_audio_features = models.ForeignKey(AudioFeatures, on_delete=models.CASCADE)

    @classmethod
    def getUserHistory(cls, user):
        """
        Get the full analysis history of a user
        """
        pass

    @classmethod
    def getUserSummary(cls, user):
        """
        Get a summary of all the analysis done for a user
        """
        pass
    
    @classmethod
    def analyseSongsForUser(cls, listSong, user):
        """
        Analyse a list of songs for a user and return the summary
        """
        pass