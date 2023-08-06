from django.urls import path, include


urlpatterns = [
    # Djoser auth urls
    path("", include("djoser.urls")),
    # Djoser JWT
    path("", include("djoser.urls.jwt")),
    # Custom user urls
    path("users/phone/", include("zonesmart.users.urls")),
]
