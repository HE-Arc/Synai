from django.test import TestCase
from synaiapp.models import AudioFeatures

# Create your tests here.
# https://docs.djangoproject.com/fr/2.1/topics/testing/overview/


class AudioFeaturesTestCase(TestCase):
    """AudioFeatures test case"""
    def setUp(self):
        self.audiofeaturesList = [
            AudioFeatures(
                acousticness=0.2,
                danceability=0.2,
                energy=0.2,
                instrumentalness=0.2,
                liveness=0.2,
                valence=0.2,
                speechiness=0.2,
                tempo=0.2
                ),
            AudioFeatures(
                acousticness=0.6,
                danceability=0.6,
                energy=0.6,
                instrumentalness=0.6,
                liveness=0.6,
                valence=0.6,
                speechiness=0.6,
                tempo=0.6
                )
        ]
    
    def test_AudioFeatures_mean(self):
        """Test mean function of AudioFeatures Model"""
        mean_empirique = 0.4
        mean_computed = AudioFeatures.mean("acousticness",
            self.audiofeaturesList)
        self.assertAlmostEqual(mean_empirique, mean_computed)

        print("AudioFeatures mean function passed")

    def test_AudioFeatures_summarise(self):
        """Test summarize function of AudioFeatures Model"""
        mean_empirique = 0.4

        summary = AudioFeatures.summarise(self.audiofeaturesList)
        
        attributesOfAudioFeatures = [
            'acousticness',
            'danceability',
            'energy',
            'instrumentalness',
            'liveness',
            'valence',
            'speechiness',
            'tempo',
        ]

        for attribute in attributesOfAudioFeatures:
            self.assertAlmostEqual(mean_empirique, getattr(summary, attribute, 0))

        print("AudioFeatures summarise function passed")
