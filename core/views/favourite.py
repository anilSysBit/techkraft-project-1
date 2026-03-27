from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..models import Favourite, Property
from ..serializers.favourite import FavouriteSerializer


class MyFavouriteListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favourites = Favourite.objects.filter(
            user=request.user,
            is_deleted=False,
            property__is_deleted=False,
        ).select_related("property").order_by("-created_at")

        serializer = FavouriteSerializer(
            favourites,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)



class AddFavouriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FavouriteSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            favourite = serializer.save()
            return Response(
                {
                    "message": "Property added to favourites.",
                    "data": FavouriteSerializer(
                        favourite,
                        context={"request": request}
                    ).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class RemoveFavouriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, property_id):
        try:
            favourite = Favourite.objects.get(
                user=request.user,
                property_id=property_id,
                is_deleted=False
            )
        except Favourite.DoesNotExist:
            return Response(
                {"error": "Favourite not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        favourite.soft_delete(user=request.user)

        return Response(
            {"message": "Property removed from favourites."},
            status=status.HTTP_200_OK
        )


class ToggleFavouriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, property_id):
        try:
            property_obj = Property.objects.get(pk=property_id, is_deleted=False)
        except Property.DoesNotExist:
            return Response(
                {"error": "Property not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        favourite = Favourite.objects.filter(
            user=request.user,
            property=property_obj
        ).first()

        if favourite and not favourite.is_deleted:
            favourite.soft_delete(user=request.user)
            return Response(
                {"message": "Property removed from favourites.", "is_favourited": False},
                status=status.HTTP_200_OK
            )

        if favourite and favourite.is_deleted:
            favourite.restore(user=request.user)
            return Response(
                {"message": "Property added to favourites.", "is_favourited": True},
                status=status.HTTP_200_OK
            )

        Favourite.objects.create(
            user=request.user,
            property=property_obj,
            created_by=request.user
        )
        return Response(
            {"message": "Property added to favourites.", "is_favourited": True},
            status=status.HTTP_201_CREATED
        )