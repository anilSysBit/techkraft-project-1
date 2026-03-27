from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from ..models import Property
from ..serializers.property import PropertySerializer

class PropertyPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 50

class PropertyListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        properties = Property.objects.filter(is_deleted=False).order_by("-created_at")

        search = request.query_params.get("search")
        if search:
            properties = properties.filter(
                Q(title__icontains=search) |
                Q(location__icontains=search) |
                Q(description__icontains=search)
            )

        paginator = PropertyPagination()
        paginated_queryset = paginator.paginate_queryset(properties, request)

        serializer = PropertySerializer(
            paginated_queryset,
            many=True,
            context={"request": request}
        )

        return paginator.get_paginated_response(serializer.data)

class PropertyDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            property_obj = Property.objects.get(pk=pk, is_deleted=False)
        except Property.DoesNotExist:
            return Response(
                {"error": "Property not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PropertySerializer(property_obj, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)