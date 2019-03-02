from django.db import models

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
