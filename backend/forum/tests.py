import os
from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Category, Like, PersonalAPIToken, Post, User

AI_OFF = {"AI_CATEGORISATION_ENABLED": "false", "AI_MODERATION_ENABLED": "false", "AI_SEMANTIC_SEARCH_ENABLED": "false"}

class ForumAPITests(TestCase):
    def setUp(self):
        self.alex = User.objects.create_user("alex", password="password123")
        self.sam = User.objects.create_user("sam", password="password123")
        self.mod = User.objects.create_user("mod", password="password123", role=User.Role.MODERATOR)
        self.post = Post.objects.create(author=self.alex, title="A useful topic", body="Enough body content")
        self.client = APIClient()

    def test_anonymous_can_read_but_not_write(self):
        self.assertEqual(self.client.get("/api/v1/posts/").status_code, 200)
        self.assertIn(self.client.post("/api/v1/posts/", {"title":"No", "body":"Anonymous"}).status_code, (401, 403))

    @patch.dict(os.environ, AI_OFF)
    @patch("forum.views.create_post_embedding.delay")
    def test_authenticated_user_can_create_immutable_post(self, delay):
        self.client.force_authenticate(self.sam)
        response = self.client.post("/api/v1/posts/", {"title":"Created", "body":"A new contribution"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["ai_status"], Post.AIStatus.DISABLED)
        self.assertEqual(self.client.patch(f"/api/v1/posts/{response.data['id']}/", {"title":"Edited"}).status_code, 405)

    def test_like_rules_and_unlike(self):
        self.client.force_authenticate(self.sam)
        url = f"/api/v1/posts/{self.post.id}/like/"
        self.assertEqual(self.client.post(url).status_code, 201)
        self.assertEqual(self.client.post(url).status_code, 409)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.client.force_authenticate(self.alex)
        self.assertEqual(self.client.post(url).status_code, 400)

    def test_comment_and_moderation_permissions(self):
        self.client.force_authenticate(self.sam)
        comments = f"/api/v1/posts/{self.post.id}/comments/"
        self.assertEqual(self.client.post(comments, {"body":"Good context"}).status_code, 201)
        moderation = f"/api/v1/posts/{self.post.id}/moderation/"
        self.assertEqual(self.client.post(moderation, {"is_misleading":True}).status_code, 403)
        self.client.force_authenticate(self.mod)
        self.assertEqual(self.client.post(moderation, {"is_misleading":True}).status_code, 200)
        self.post.refresh_from_db(); self.assertTrue(self.post.is_misleading)

    def test_private_ai_review_is_hidden_from_regular_users(self):
        self.post.ai_moderation_score=.91; self.post.ai_moderation_rationale="Needs review"; self.post.ai_needs_review=True; self.post.save()
        self.client.force_authenticate(self.sam)
        regular = self.client.get(f"/api/v1/posts/{self.post.id}/").data
        self.assertIsNone(regular["ai_moderation_score"])
        self.client.force_authenticate(self.mod)
        moderator = self.client.get(f"/api/v1/posts/{self.post.id}/").data
        self.assertEqual(moderator["ai_moderation_score"], .91)

    def test_personal_token_is_returned_once_and_can_be_revoked(self):
        self.client.force_authenticate(self.sam)
        created = self.client.post("/api/v1/tokens/", {"name":"Automation"})
        self.assertEqual(created.status_code, 201); raw = created.data["token"]
        self.assertTrue(raw.startswith("vf_"))
        token = PersonalAPIToken.objects.get()
        self.assertNotEqual(token.digest, raw)
        external = APIClient(); external.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        self.assertEqual(external.get("/api/v1/auth/me/").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/v1/tokens/{token.id}/").status_code, 204)
        self.assertEqual(external.get("/api/v1/auth/me/").status_code, 403)

class AIServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("author", password="password123")
        self.category = Category.objects.create(name="Technology", slug="technology")
        self.post = Post.objects.create(author=self.user, title="Chip update", body="A factual claim")

    @patch.dict(os.environ, {"AI_API_KEY":"test", "AI_CATEGORISATION_ENABLED":"true", "AI_MODERATION_ENABLED":"true", "AI_MODERATION_THRESHOLD":"0.75"})
    @patch("forum.ai.client")
    def test_structured_analysis_sets_category_and_private_preflag(self, mock_client):
        from types import SimpleNamespace
        from .ai import analyse_post
        choice = SimpleNamespace(message=SimpleNamespace(content='{"misinformation_confidence":0.9,"rationale":"Check this claim"}'))
        mock_client.return_value.chat.completions.create.return_value = SimpleNamespace(choices=[choice])
        analyse_post(self.post); self.post.refresh_from_db()
        self.assertTrue(self.post.ai_needs_review); self.assertFalse(self.post.is_misleading)

    @patch.dict(os.environ, {"AI_API_KEY":"test", "AI_VIBE_ENABLED":"true"})
    @patch("forum.ai.client")
    def test_thread_vibe_uses_comment_context(self, mock_client):
        from types import SimpleNamespace
        from .ai import analyse_thread_vibe
        from .models import Comment
        Comment.objects.create(post=self.post, author=self.user, body="This is a useful and clear explanation.")
        choice = SimpleNamespace(message=SimpleNamespace(content='{"vibe":"Constructive"}'))
        mock_client.return_value.chat.completions.create.return_value = SimpleNamespace(choices=[choice])
        analyse_thread_vibe(self.post); self.post.refresh_from_db()
        self.assertEqual(self.post.vibe, Post.Vibe.CONSTRUCTIVE)

    @patch.dict(os.environ, {"AI_API_KEY":"test", "AI_CATEGORISATION_ENABLED":"true", "AI_MODERATION_ENABLED":"true"})
    @patch("forum.ai.client")
    def test_malformed_ai_response_fails_open(self, mock_client):
        from types import SimpleNamespace
        from .ai import analyse_post
        choice = SimpleNamespace(message=SimpleNamespace(content="not json"))
        mock_client.return_value.chat.completions.create.return_value = SimpleNamespace(choices=[choice])
        analyse_post(self.post); self.post.refresh_from_db()
        self.assertEqual(self.post.ai_status, Post.AIStatus.FAILED)

    @patch.dict(os.environ, {"AI_API_KEY":"", "AI_CATEGORISATION_ENABLED":"true", "AI_MODERATION_ENABLED":"true"})
    def test_missing_api_key_fails_open_without_network(self):
        from .ai import analyse_post
        analyse_post(self.post); self.post.refresh_from_db()
        self.assertEqual(self.post.ai_status, Post.AIStatus.FAILED)
        self.assertIn("RuntimeError", self.post.ai_moderation_rationale)

    @patch.dict(os.environ, {"AI_SEMANTIC_SEARCH_ENABLED":"false"})
    def test_embedding_task_marks_disabled_without_provider_call(self):
        from .tasks import create_post_embedding
        with patch("forum.tasks.embed_text") as embed:
            create_post_embedding.run(self.post.id)
        embed.assert_not_called(); self.post.refresh_from_db()
        self.assertEqual(self.post.embedding_status, Post.AIStatus.DISABLED)

    @patch.dict(os.environ, {"AI_SEMANTIC_SEARCH_ENABLED":"true"})
    def test_embedding_failure_is_recorded_and_re_raised_for_retry(self):
        from .tasks import create_post_embedding
        with patch("forum.tasks.embed_text", side_effect=ConnectionError("offline")):
            with self.assertRaises(ConnectionError): create_post_embedding.run(self.post.id)
        self.post.refresh_from_db(); self.assertEqual(self.post.embedding_status, Post.AIStatus.FAILED)


class AuthenticationAndSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("reader", password="password123")
        self.other = User.objects.create_user("other", password="password123")
        self.post = Post.objects.create(author=self.other, title="Searchable", body="Clean energy storage")
        self.client = APIClient()

    def test_password_login_and_logout(self):
        bad = self.client.post("/api/v1/auth/login/", {"username":"reader", "password":"wrong"})
        self.assertEqual(bad.status_code, 400)
        good = self.client.post("/api/v1/auth/login/", {"username":"reader", "password":"password123"})
        self.assertEqual(good.status_code, 200); self.assertEqual(good.data["username"], "reader")
        self.assertEqual(self.client.get("/api/v1/auth/me/").status_code, 200)
        self.assertEqual(self.client.post("/api/v1/auth/logout/").status_code, 204)
        self.assertIn(self.client.get("/api/v1/auth/me/").status_code, (401, 403))

    @patch.dict(os.environ, {"AI_SEMANTIC_SEARCH_ENABLED":"false"})
    def test_disabled_semantic_search_never_calls_provider(self):
        with patch("forum.views.embed_text") as embed:
            response = self.client.get("/api/v1/posts/search/?q=energy")
        self.assertEqual(response.status_code, 503); embed.assert_not_called()

    @patch.dict(os.environ, {"AI_SEMANTIC_SEARCH_ENABLED":"true"})
    @patch("forum.views.embed_text", side_effect=ConnectionError("offline"))
    def test_search_connection_failure_returns_stable_503(self, embed):
        response = self.client.get("/api/v1/posts/search/?q=energy")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["detail"], "Semantic search is temporarily unavailable.")

    def test_tokens_are_scoped_to_owner(self):
        mine, _ = PersonalAPIToken.issue(self.user, "Mine")
        theirs, _ = PersonalAPIToken.issue(self.other, "Theirs")
        self.client.force_authenticate(self.user)
        listed = self.client.get("/api/v1/tokens/").data["results"]
        self.assertEqual([row["id"] for row in listed], [mine.id])
        self.assertEqual(self.client.delete(f"/api/v1/tokens/{theirs.id}/").status_code, 404)

    def test_public_post_delete_is_explicitly_rejected(self):
        self.client.force_authenticate(self.other)
        response = self.client.delete(f"/api/v1/posts/{self.post.id}/")
        self.assertEqual(response.status_code, 405)
