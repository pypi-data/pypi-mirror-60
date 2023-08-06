from rest_framework.generics import RetrieveDestroyAPIView

from zonesmart.product.models import ProductImage
from zonesmart.product.serializers import ProductImageSerializer


class ProductImageAPIVIew(RetrieveDestroyAPIView):
    serializer_class = ProductImageSerializer
    lookup_field = "id"

    def get_queryset(self):
        return ProductImage.objects.all()


product_image_api_view = ProductImageAPIVIew.as_view()
