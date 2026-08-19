from celery import shared_task
from .ai import embed_text, enabled
from .models import Post

@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def create_post_embedding(post_id):
    post = Post.objects.get(pk=post_id)
    if not enabled("AI_SEMANTIC_SEARCH_ENABLED"):
        Post.objects.filter(pk=post_id).update(embedding_status=Post.AIStatus.DISABLED)
        return
    try:
        vector = embed_text(f"{post.title}\n{post.body}")
        Post.objects.filter(pk=post_id).update(embedding=vector, embedding_status=Post.AIStatus.COMPLETE)
    except Exception:
        Post.objects.filter(pk=post_id).update(embedding_status=Post.AIStatus.FAILED)
        raise

