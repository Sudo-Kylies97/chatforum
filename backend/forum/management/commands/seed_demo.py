from django.core.management.base import BaseCommand
from forum.models import Category, Comment, Like, Post, User

class Command(BaseCommand):
    help = "Create deterministic assessment demo data"
    def handle(self, *args, **kwargs):
        categories = {}
        for slug, name in [("technology", "Technology"), ("news", "News"), ("questions", "Questions"), ("community", "Community"), ("general", "General")]:
            categories[slug], _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
        alex, _ = User.objects.get_or_create(username="alex", defaults={"email": "alex@example.com", "role": User.Role.REGULAR})
        alex.set_password("VerityDemo123!"); alex.save()
        sam, _ = User.objects.get_or_create(username="sam", defaults={"email": "sam@example.com", "role": User.Role.REGULAR})
        sam.set_password("VerityDemo123!"); sam.save()
        mod, _ = User.objects.get_or_create(username="moderator", defaults={"email": "moderator@example.com", "role": User.Role.MODERATOR, "is_staff": True})
        mod.set_password("VerityMod123!"); mod.save()
        post, _ = Post.objects.get_or_create(author=alex, title="Welcome to Verity", defaults={"body": "A thoughtful place to exchange ideas and ask useful questions.", "category": categories["community"], "ai_status": Post.AIStatus.COMPLETE, "embedding_status": Post.AIStatus.DISABLED})
        comment, _ = Comment.objects.get_or_create(post=post, author=sam, body="Glad to be here. What should we discuss first?")
        Like.objects.get_or_create(post=post, user=sam)
        self.stdout.write(self.style.SUCCESS("Demo users and forum data are ready."))
