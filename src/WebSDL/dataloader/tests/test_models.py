from django.test import TestCase

# Create your tests here.
from dataloader.models import SamplingFeature, SamplingFeatureType


class TestSamplingFeature(TestCase):
    def setUp(self):
        sampling_feature_type_data = {
            "term": "site",
            "name": "Site",
            "category": "SamplingPoint",
            "definition": "A facility or location at which observations have been collected."
        }
        self.sampling_feature_type = SamplingFeatureType.objects.create(**sampling_feature_type_data)

        sampling_feature_data = {
            "sampling_feature_type": self.sampling_feature_type,
            "sampling_feature_code": "RB_KF_C",
            "sampling_feature_name": "Knowlton Fork Climate",
            "sampling_feature_description": "",
            "elevation_m": 2178.1008
        }
        self.sampling_feature = SamplingFeature.objects.create(**sampling_feature_data)

    def test_creation(self):
        self.assertTrue(isinstance(self.sampling_feature, SamplingFeature))

    def test_string_representation(self):
        self.assertEqual(str(self.sampling_feature), 'Site: RB_KF_C Knowlton Fork Climate')
        self.assertEqual(self.sampling_feature.__unicode__(), u'Site: RB_KF_C Knowlton Fork Climate')

    def tearDown(self):
        self.sampling_feature.delete()
        self.sampling_feature_type.delete()
