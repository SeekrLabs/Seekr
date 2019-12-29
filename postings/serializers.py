from .models import Posting
from rest_framework import serializers


class PostingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Posting
        fields = ['title', 'time_posted', 'url', 'vector', 'text']