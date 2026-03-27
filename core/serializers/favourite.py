from rest_framework import serializers
from ..models import Favourite, Property
from .property import PropertySerializer


class FavouriteSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.filter(is_deleted=False),
        source="property",
        write_only=True
    )

    class Meta:
        model = Favourite
        fields = [
            "id",
            "property",
            "property_id",
            "created_at",
        ]
        read_only_fields = ["id", "property", "created_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        property_obj = attrs["property"]

        if Favourite.objects.filter(
            user=user,
            property=property_obj,
            is_deleted=False
        ).exists():
            raise serializers.ValidationError({
                "property_id": "This property is already in your favourites."
            })

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        return Favourite.objects.create(
            user=user,
            created_by=user,
            **validated_data
        )