from rest_framework import serializers
from dataloader.models import People, Organization, Affiliation


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = People
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class AffiliationSerializer(serializers.ModelSerializer):
    person = PersonSerializer(required=False)
    organization = OrganizationSerializer(required=False)

    class Meta:
        model = Affiliation
        fields = '__all__'
