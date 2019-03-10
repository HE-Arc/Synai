from synaiapp.models import AudioFeatures

from rest_framework import serializers

class AudioFeaturesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AudioFeatures
        fields = ('acousticness',
            'danceability',
            'energy',
            'instrumentalness',
            'liveness',
            'valence',
            'speechiness',
            'tempo',
            )