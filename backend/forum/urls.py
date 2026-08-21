from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, PostViewSet, TokenViewSet, csrf, login_view, logout_view, me

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("categories", CategoryViewSet)
router.register("tokens", TokenViewSet, basename="token")
urlpatterns = [
    path("auth/csrf/", csrf),
    path("auth/login/", login_view),
    path("auth/logout/", logout_view),
    path("auth/me/", me),
    path("", include(router.urls)),
]
