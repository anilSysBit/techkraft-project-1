from rest_framework import serializers
from ..models import Property, PropertyImage, Favourite


class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = [
            "id",
            "image",
            "image_url",
            "alt_text",
            "is_primary",
            "display_order",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None



class PropertySerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    is_favourited = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "location",
            "price",
            "discount",
            "actual_price",
            "description",
            "images",
            "is_favourited",
            "created_at",
        ]

    def get_images(self, obj):
        images = obj.images.filter(is_deleted=False).order_by("display_order", "-created_at")
        return PropertyImageSerializer(images, many=True, context=self.context).data

    def get_is_favourited(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            return False

        return Favourite.objects.filter(
            user=user,
            property=obj,
            is_deleted=False
        ).exists()