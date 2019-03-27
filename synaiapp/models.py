from django.db import models
from django.contrib.auth.models import User
from functools import reduce
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

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

    @classmethod
    def featuresHeaders(cls):
        return [
            "Acousticness",
            "Danceability",
            "Energy",
            "Instrumentalness",
            "Liveness",
            "Valence",
            "Speechiness",
            "Tempo"
        ]

    def asArray(self):
        return [
            self.acousticness,
            self.danceability,
            self.energy,
            self.instrumentalness,
            self.liveness,
            self.valence,
            self.speechiness,
            self.tempo/100,
        ]

class Artist(models.Model):
    spotify_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

    @classmethod
    def get_artist(cls, artist_id):
        artist = Artist.objects.filter(spotify_id=artist_id).first()
        return artist
    
    @classmethod
    def create(cls, spotify_id, name):
        artist = cls(spotify_id=spotify_id, name=name)
        return artist

class Album(models.Model):
    spotify_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

    @classmethod
    def get_album(cls, album_id):
        album = Album.objects.filter(spotify_id=album_id).first()
        return album

    @classmethod
    def create(cls, spotify_id, name):
        album = cls(spotify_id=spotify_id, name=name)
        return album

    def get_songs(self):
        return self.selected_related()

class Song(models.Model):
    spotify_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    artists = models.ManyToManyField(Artist)
    album = models.ForeignKey(Album, null=True, on_delete=models.SET_NULL)
    audio_features = models.ForeignKey(AudioFeatures, null=True, on_delete=models.SET_NULL)

    @classmethod
    def get_song(cls, song_req_id):
        return cls.objects.filter(spotify_id=song_req_id).first()

    @classmethod
    def create(cls, song_id, name, audio_features, album):
        song = cls(spotify_id = song_id, name=name, audio_features=audio_features, album = album)
        return song

class Analysis(models.Model):
    songs = models.ManyToManyField(Song)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    summarised_audio_features = models.ForeignKey(AudioFeatures, on_delete=models.CASCADE)
    songs_len = models.IntegerField()
    created = models.DateTimeField(default=timezone.now)

    manager = models.Manager()

    @classmethod
    def getUserHistory(cls, user, order=1):
        """
        Get the full analysis history of a user
        """
        analysis = Analysis.manager.filter(user=user).prefetch_related('songs').select_related('summarised_audio_features')
        
        # yeah lazy load that analysis
        if order < 1:
            analysis = analysis.order_by('-created')

        songs = [ana.songs for ana in analysis] # get all songs of the analysis
        
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
    def analyseSongsForUser(cls, songs):
        """
        Analyse a list of songs for a user and return the summary
        """
        # Doit être dans feedView !
        #songs = self.songs.all().selected_related('audio_features').all()
        #songs = list(Song.objects.filter(spotify_id__in=spotify_ids))
        #[print(song.audio_features) for song in songs]
        return AudioFeatures.summarise([song.audio_features for song in songs])

    def asDataset(self):
        # Need to be optimized
        features_headers = ["Feature"]
        features_data = []
       
        
        songs = self.songs.select_related('audio_features').all()
        audio_features_of_songs = [song.audio_features for song in songs]
        
        # Foreach feature (acousticness, livness, valence,...)
        features_attributes = [attr.lower() for attr in AudioFeatures.featuresHeaders()[:-1]]

        for feature in features_attributes:
            # Add the title
            line = [feature]

            # Add the value of the audio_feature of each song
            for af in audio_features_of_songs:
                value = getattr(af, feature, 0)
                line.append(value)

            features_data.append(line) # add in the dataset

        # Create the first line of the header
        features_headers.extend(song.name for song in songs)
        features_data.insert(0, features_headers)
        return features_data
    