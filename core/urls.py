
from django.urls import path
from .views.base import RegisterAPIView, LoginAPIView, LogoutAPIView, MeAPIView
from .views.property import PropertyListAPIView, PropertyDetailAPIView
from .views.favourite import (
    MyFavouriteListAPIView,
    AddFavouriteAPIView,
    RemoveFavouriteAPIView,
    ToggleFavouriteAPIView,
)

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="logout"),
    path("auth/me/", MeAPIView.as_view(), name="me"),

    path("properties/", PropertyListAPIView.as_view(), name="property-list"),
    path("properties/<int:pk>/", PropertyDetailAPIView.as_view(), name="property-detail"),

    path("favourites/", MyFavouriteListAPIView.as_view(), name="my-favourites"),
    path("favourites/add/", AddFavouriteAPIView.as_view(), name="add-favourite"),
    path("favourites/remove/<int:property_id>/", RemoveFavouriteAPIView.as_view(), name="remove-favourite"),
    path("favourites/toggle/<int:property_id>/", ToggleFavouriteAPIView.as_view(), name="toggle-favourite"),
]