import hashlib
import secrets
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        REGULAR = "regular", "Regular"
        MODERATOR = "moderator", "Moderator"
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.REGULAR)

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR or self.is_staff


class Category(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    class AIStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"
        DISABLED = "disabled", "Disabled"
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="posts")
    title = models.CharField(max_length=180)
    body = models.TextField(max_length=10000)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="posts")
    is_misleading = models.BooleanField(default=False)
    flagged_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="moderated_posts")
    flagged_at = models.DateTimeField(null=True, blank=True)
    ai_status = models.CharField(max_length=12, choices=AIStatus.choices, default=AIStatus.PENDING)
    ai_moderation_score = models.FloatField(null=True, blank=True)
    ai_moderation_rationale = models.TextField(blank=True)
    ai_needs_review = models.BooleanField(default=False)
    ai_model = models.CharField(max_length=120, blank=True)
    class Vibe(models.TextChoices):
        TOXIC = "toxic", "Toxic"
        CONSTRUCTIVE = "constructive", "Constructive"
        HUMOROUS = "humorous", "Humorous"
        INFORMATIVE = "informative", "Informative"
        UNKNOWN = "unknown", "Unknown"
    vibe = models.CharField(max_length=16, choices=Vibe.choices, default=Vibe.UNKNOWN)
    vibe_status = models.CharField(max_length=12, choices=AIStatus.choices, default=AIStatus.DISABLED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"]), models.Index(fields=["category", "-created_at"])]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="comments")
    body = models.TextField(max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["created_at"]


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["post", "user"], name="one_like_per_user_post")]


class PersonalAPIToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_tokens")
    name = models.CharField(max_length=80)
    prefix = models.CharField(max_length=12, db_index=True)
    digest = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def issue(cls, user, name):
        raw = "vf_" + secrets.token_urlsafe(32)
        token = cls.objects.create(user=user, name=name, prefix=raw[:10], digest=hashlib.sha256(raw.encode()).hexdigest())
        return token, raw
