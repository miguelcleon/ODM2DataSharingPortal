from rest_framework import serializers
from dataloader.models import People, Organization, Affiliation


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = People


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization


class AffiliationSerializer(serializers.ModelSerializer):
    person = PersonSerializer(required=False)
    organization = OrganizationSerializer(required=False)

    class Meta:
        model = Affiliation
