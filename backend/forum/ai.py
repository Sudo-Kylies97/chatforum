import json
import os
from openai import OpenAI
from .models import Category, Post

CATEGORIES = ["Technology", "News", "Questions", "Community", "General"]

def enabled(name):
    return os.getenv(name, "true").lower() == "true"

def client():
    key = os.getenv("AI_API_KEY")
    if not key:
        raise RuntimeError("AI_API_KEY is not configured")
    return OpenAI(api_key=key, base_url=os.getenv("AI_BASE_URL", "https://api.openai.com/v1"), timeout=float(os.getenv("AI_TIMEOUT_SECONDS", "8")))

def analyse_post(post):
    category_on = enabled("AI_CATEGORISATION_ENABLED")
    moderation_on = enabled("AI_MODERATION_ENABLED")
    if not category_on and not moderation_on:
        post.ai_status = Post.AIStatus.DISABLED
        post.save(update_fields=["ai_status"])
        return
    prompt = f"""Analyse this forum post. Return JSON only with category (one of {CATEGORIES}), misinformation_confidence (0 to 1), and rationale (max 240 chars). Confidence measures likelihood that factual claims are misleading; opinions and questions should score low.\nTitle: {post.title}\nBody: {post.body}"""
    try:
        model = os.getenv("AI_CHAT_MODEL", "gpt-4o-mini")
        result = client().chat.completions.create(model=model, response_format={"type": "json_object"}, messages=[{"role": "user", "content": prompt}])
        data = json.loads(result.choices[0].message.content)
        fields = ["ai_status", "ai_model"]
        post.ai_status, post.ai_model = Post.AIStatus.COMPLETE, model
        if category_on and data.get("category") in CATEGORIES:
            post.category = Category.objects.get(name=data["category"]); fields.append("category")
        if moderation_on:
            score = min(1.0, max(0.0, float(data["misinformation_confidence"])))
            post.ai_moderation_score = score
            post.ai_moderation_rationale = str(data.get("rationale", ""))[:240]
            post.ai_needs_review = score >= float(os.getenv("AI_MODERATION_THRESHOLD", "0.75"))
            fields += ["ai_moderation_score", "ai_moderation_rationale", "ai_needs_review"]
        post.save(update_fields=fields)
    except Exception as exc:
        post.ai_status = Post.AIStatus.FAILED
        post.ai_moderation_rationale = f"Analysis unavailable: {type(exc).__name__}"
        post.save(update_fields=["ai_status", "ai_moderation_rationale"])

def embed_text(text):
    response = client().embeddings.create(model=os.getenv("AI_EMBEDDING_MODEL", "text-embedding-3-small"), input=text)
    return response.data[0].embedding

