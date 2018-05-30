import warnings
from rest_framework import serializers
from rest_framework import generics
from oscar.core.loading import get_model

Category = get_model('catalogue', 'Category')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'