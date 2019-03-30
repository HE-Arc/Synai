from django.db import models
from django.contrib.auth.models import User
from functools import reduce
from django.utils import timezone
import json

# Logger & debug
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
    def summarise(cls, audio_features_list):
        summary = AudioFeatures()
        summary.acousticness = AudioFeatures.mean("acousticness", audio_features_list)
        summary.danceability = AudioFeatures.mean("danceability", audio_features_list)
        summary.energy = AudioFeatures.mean("energy", audio_features_list)
        summary.instrumentalness = AudioFeatures.mean("instrumentalness", audio_features_list)
        summary.liveness = AudioFeatures.mean("liveness", audio_features_list)
        summary.valence = AudioFeatures.mean("valence", audio_features_list)
        summary.speechiness = AudioFeatures.mean("speechiness", audio_features_list)
        summary.tempo = AudioFeatures.mean("tempo", audio_features_list)
        return summary

    
    @classmethod
    def mean(cls, attribute, audio_features_list):
        return reduce(lambda a, b: a+b, [getattr(x, attribute, 0) for x in audio_features_list]) /len(audio_features_list)
    
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
    def prepare_data_for_linegraph(cls, audio_features):
        graph_data = []
        # Foreach feature (acousticness, livness, valence,...)
        features_attributes = [attr.lower() for attr in cls.features_headers()[:-1]]
        for feature in features_attributes:
            # Add the title
            line = [feature]
            
            # Get the attrib value of each audio features
            for af in audio_features:
                value = getattr(af, feature, 0)
                line.append(value)
            # Add the line to the dataset
            graph_data.append(line)
        return graph_data


    @classmethod
    def features_headers(cls):
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

    def as_array(self):
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
    def create(cls, songs, user, summarised_audio_features):
        analysis = cls(user=user, summarised_audio_features=summarised_audio_features, songs_len=len(songs))
        analysis.save()
        for song in songs:
            analysis.songs.add(song)
        return analysis

    @classmethod
    def get_user_history(cls, user, order=1):
        """
        Get the full analysis history of a user
        """
        analysis = Analysis.manager.filter(user=user).prefetch_related('songs').select_related('summarised_audio_features')
        
        # yeah lazy load that analysis
        if order < 1:
            analysis = analysis.order_by('-created')

        # get all songs of the analysis
        songs = [ana.songs for ana in analysis]

        # get the summarised audio features of each analysis
        audio_features = [ana.summarised_audio_features for ana in analysis]

        return analysis, songs, audio_features

    @classmethod
    def get_user_summarised_data(cls, user):
        """
        Get a summary of all the analysis done for a user as an AudioFeatures
        """
        analysis, songs, audio_features = Analysis.get_user_history(user)
        if len(analysis) < 1:
            return None

        # Prepare the header
        graph_headers = ["Analysis"]
        graph_headers.extend(ana.created.strftime('%d.%m.%Y') for ana in analysis)
        
        # Prepare the data
        graph_data = AudioFeatures.prepare_data_for_linegraph(audio_features)

        # Join
        graph_data.insert(0, graph_headers)

        # Return the dataset
        return graph_data
    
    @classmethod
    def analyse_songs_for_user(cls, songs, user):
        """
        Analyse a list of songs for a user.
        Return the analysis and the audio features
        """
        # Get the audio features
        audio_features = [song.audio_features for song in songs]

        # Create the analysis using the summarised audio feature
        summarised_af = AudioFeatures.summarise(audio_features)
        summarised_af.save()
        
        analysis = Analysis.create(songs, user, summarised_af)
        analysis.save()
        
        # Return the analysis and the related audio features
        return analysis, audio_features

    def history_dataset(self):
        """
        Give an analysis as a dataset for history presentation
        """
        # Get the datas
        songs = self.songs.select_related('audio_features').all()
        audio_features_of_songs = [song.audio_features for song in songs]

        # Create the first line of the header
        features_headers = ["Feature"]
        features_headers.extend(song.name for song in songs)

        # Prepare datas
        features_data = AudioFeatures.prepare_data_for_linegraph(audio_features_of_songs)
        
        # Join
        features_data.insert(0, features_headers)

        # Return the dataset
        return features_data
