from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from zonesmart.product.serializers import ProductImageSerializer


class ProductActions:
    """
    Actions for product models
    """

    @action(detail=True, methods=["GET"])
    def get_images(self, request, *args, **kwargs):
        """
        Returns main image url and list of extra images
        """
        product = self.get_object()
        data = {
            "main_image": product.main_image.get_url()
            if getattr(product, "main_image", None)
            else None,
            "extra_images": [
                extra_image.get_url() for extra_image in product.extra_images.all()
            ],
        }
        return Response(data=data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["POST"],
        parser_classes=[MultiPartParser],
        url_path=r"upload_image/(?P<type>[\w]+)",
    )
    def upload_image(self, request, *args, **kwargs):
        """
        Uploads image depends on type from url kwarg: main or extra and returns serializer data
        """
        # Get image type
        try:
            image_type = kwargs.get("type")
            if image_type not in ["extra", "main"]:
                raise ValidationError("Wrong type specified. Choices are: main, extra.")
        except KeyError:
            raise ValidationError("No image type specified")
        # Validate image file by serializer
        serializer = ProductImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {}
        # Get product object
        product = self.get_object()
        # If image type is main
        if image_type == "main":
            # Check if product already has an image and delete it first
            if getattr(product, "main_image", None):
                product.main_image.delete()
            # Save image file into the ProductImage model and save
            product.main_image = serializer.save()
            product.save()
        # Else if image type is extra
        else:
            if product.extra_images.count() >= product.EXTRA_IMAGES_LIMIT:
                raise ValidationError(
                    f"You can't assign more than {product.EXTRA_IMAGES_LIMIT} extra images!"
                )
            product.extra_images.add(serializer.save())
            product.save()
            limit = product.EXTRA_IMAGES_LIMIT - product.extra_images.count()
            data.update({"extra_images_limit_remain:": limit})
        # Return successful upload message
        data.update(serializer.data)
        return Response(data=data, status=status.HTTP_201_CREATED)
