import os
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import BooleanField, Count, Exists, OuterRef, Value
from django.middleware.csrf import get_token
from django.utils import timezone
from pgvector.django import CosineDistance
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .ai import analyse_post, embed_text, enabled
from .models import Category, Comment, Like, PersonalAPIToken, Post
from .serializers import CategorySerializer, CommentSerializer, PostSerializer, TokenSerializer, UserSerializer
from .tasks import create_post_embedding

def post_queryset(request):
    likes = Like.objects.filter(post=OuterRef("pk"), user=request.user.pk) if request.user.is_authenticated else Like.objects.none()
    return Post.objects.select_related("author", "category").prefetch_related("comments__author").annotate(like_count=Count("likes", distinct=True), comment_count=Count("comments", distinct=True), liked_by_me=Exists(likes) if request.user.is_authenticated else Value(False, output_field=BooleanField())).order_by("-created_at")

@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def csrf(request): return Response({"csrfToken": get_token(request)})

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    user = authenticate(request, username=request.data.get("username"), password=request.data.get("password"))
    if not user: return Response({"detail": "Invalid username or password."}, status=400)
    login(request, user); return Response(UserSerializer(user).data)

@api_view(["POST"])
def logout_view(request): logout(request); return Response(status=204)

@api_view(["GET"])
def me(request): return Response(UserSerializer(request.user).data)

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]
    def get_permissions(self):
        return [permissions.AllowAny()] if self.action in ("list", "retrieve", "search") else [permissions.IsAuthenticated()]
    def get_queryset(self):
        qs = post_queryset(self.request)
        category = self.request.query_params.get("category")
        return qs.filter(category__slug=category) if category else qs
    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        analyse_post(post)
        try: create_post_embedding.delay(post.pk)
        except Exception: Post.objects.filter(pk=post.pk).update(embedding_status=Post.AIStatus.FAILED)
    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Posts are immutable and cannot be deleted."}, status=405)
    @action(detail=True, methods=["post"])
    def comments(self, request, pk=None):
        serializer = CommentSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        serializer.save(post=self.get_object(), author=request.user)
        return Response(serializer.data, status=201)
    @action(detail=True, methods=["post", "delete"])
    def like(self, request, pk=None):
        post = self.get_object()
        if request.method == "DELETE": Like.objects.filter(post=post, user=request.user).delete(); return Response(status=204)
        if post.author_id == request.user.id: return Response({"detail": "You cannot like your own post."}, status=400)
        try:
            _, created = Like.objects.get_or_create(post=post, user=request.user)
        except IntegrityError:
            created = False
        if not created: return Response({"detail": "You already liked this post."}, status=409)
        return Response(status=201)
    @action(detail=True, methods=["post"])
    def moderation(self, request, pk=None):
        if not request.user.is_moderator: return Response({"detail": "Moderator access required."}, status=403)
        post = self.get_object(); post.is_misleading = bool(request.data.get("is_misleading")); post.flagged_by = request.user if post.is_misleading else None; post.flagged_at = timezone.now() if post.is_misleading else None; post.ai_needs_review = False
        post.save(update_fields=["is_misleading", "flagged_by", "flagged_at", "ai_needs_review"])
        return Response(self.get_serializer(post).data)
    @action(detail=True, methods=["post"])
    def retry_ai(self, request, pk=None):
        if not request.user.is_moderator: return Response({"detail": "Moderator access required."}, status=403)
        post = self.get_object(); analyse_post(post); create_post_embedding.delay(post.pk)
        return Response(self.get_serializer(post_queryset(request).get(pk=post.pk)).data)
    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def search(self, request):
        query = request.query_params.get("q", "").strip()
        if not enabled("AI_SEMANTIC_SEARCH_ENABLED"): return Response({"detail": "Semantic search is disabled."}, status=503)
        if len(query) < 2: return Response({"detail": "Search query must contain at least two characters."}, status=400)
        try:
            vector = embed_text(query)
            posts = self.get_queryset().filter(embedding__isnull=False).annotate(distance=CosineDistance("embedding", vector)).order_by("distance")[:20]
            return Response(self.get_serializer(posts, many=True).data)
        except Exception: return Response({"detail": "Semantic search is temporarily unavailable."}, status=503)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("name"); serializer_class = CategorySerializer; permission_classes = [permissions.AllowAny]

class TokenViewSet(viewsets.ModelViewSet):
    serializer_class = TokenSerializer; http_method_names = ["get", "post", "delete", "head", "options"]
    def get_queryset(self): return PersonalAPIToken.objects.filter(user=self.request.user)
    def create(self, request):
        name = str(request.data.get("name", "API token")).strip()[:80]
        token, raw = PersonalAPIToken.issue(request.user, name)
        data = TokenSerializer(token).data; data["token"] = raw
        return Response(data, status=201)
    def destroy(self, request, *args, **kwargs):
        token = self.get_object(); token.revoked_at = timezone.now(); token.save(update_fields=["revoked_at"])
        return Response(status=204)
