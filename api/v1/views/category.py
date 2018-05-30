from rest_framework.generics import ListAPIView
from oscar.core.loading import get_model


from api.v1.serializers import CategorySerializer

Category = get_model('catalogue', 'Category')

class CategoryList(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer