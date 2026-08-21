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
        demo_posts = [
            (alex, "Welcome to Verity", "A thoughtful place to exchange ideas and ask useful questions.", "community", False),
            (sam, "How should we evaluate a strong claim?", "What sources and context help you decide whether an online claim is reliable?", "questions", False),
            (alex, "A claim worth a moderator review", "This deliberately seeded example demonstrates the public misinformation warning workflow.", "news", True),
        ]
        for author, title, body, category, flagged in demo_posts:
            post, _ = Post.objects.get_or_create(author=author, title=title, defaults={"body": body, "category": categories[category], "ai_status": Post.AIStatus.COMPLETE, "vibe_status": Post.AIStatus.COMPLETE, "vibe": Post.Vibe.CONSTRUCTIVE})
            if flagged:
                Post.objects.filter(pk=post.pk).update(is_misleading=True, flagged_by=mod, flagged_at=post.created_at, ai_moderation_score=.92, ai_moderation_rationale="Seeded review example for the moderator demo.", ai_needs_review=False)
            Comment.objects.get_or_create(post=post, author=sam if author == alex else alex, defaults={"body": "Thanks for sharing this context. I would like to hear another perspective."})
            if author != sam:
                Like.objects.get_or_create(post=post, user=sam)
        self.stdout.write(self.style.SUCCESS("Demo users, posts, comments, likes, categories, and a reviewed warning example are ready."))
