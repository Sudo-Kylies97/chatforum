from rest_framework import serializers
from .models import Category, Comment, PersonalAPIToken, Post, User

class UserSerializer(serializers.ModelSerializer):
    is_moderator = serializers.BooleanField(read_only=True)
    class Meta:
        model = User; fields = ["id", "username", "is_moderator"]

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Comment; fields = ["id", "author", "body", "created_at"]; read_only_fields = ["id", "created_at"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category; fields = ["slug", "name"]

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    liked_by_me = serializers.BooleanField(read_only=True)
    ai_moderation_score = serializers.SerializerMethodField()
    ai_moderation_rationale = serializers.SerializerMethodField()
    ai_needs_review = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ["id", "author", "title", "body", "category", "is_misleading", "created_at", "comments", "like_count", "comment_count", "liked_by_me", "ai_status", "embedding_status", "ai_moderation_score", "ai_moderation_rationale", "ai_needs_review", "vibe", "vibe_status"]
        read_only_fields = [f for f in fields if f not in ("title", "body")]
    def _moderator_value(self, obj, field):
        user = self.context["request"].user
        return getattr(obj, field) if user.is_authenticated and user.is_moderator else None
    def get_ai_moderation_score(self, obj): return self._moderator_value(obj, "ai_moderation_score")
    def get_ai_moderation_rationale(self, obj): return self._moderator_value(obj, "ai_moderation_rationale")
    def get_ai_needs_review(self, obj): return self._moderator_value(obj, "ai_needs_review")

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalAPIToken; fields = ["id", "name", "prefix", "created_at", "last_used_at", "revoked_at"]; read_only_fields = fields
