from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.api.serializers.auth import (
    LoginSerializer,
    MeSerializer,
    RefreshRequestSerializer,
    TokenPairSerializer,
)


@extend_schema_view(post=extend_schema(responses=TokenPairSerializer))
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


@extend_schema_view(
    post=extend_schema(request=RefreshRequestSerializer, responses=TokenPairSerializer)
)
class RefreshView(TokenRefreshView):
    pass


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=MeSerializer)
    def get(self, request: Request) -> Response:
        return Response(MeSerializer.from_user(request.user))
