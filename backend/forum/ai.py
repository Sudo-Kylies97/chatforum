import json
import os
from openai import OpenAI
from .models import Post
VIBES={"Toxic","Constructive","Humorous","Informative"}
def enabled(name): return os.getenv(name,"true").lower()=="true"
def client():
    key=os.getenv("AI_API_KEY")
    if not key: raise RuntimeError("AI_API_KEY is not configured")
    return OpenAI(api_key=key,base_url=os.getenv("AI_BASE_URL","https://api.openai.com/v1"),timeout=float(os.getenv("AI_TIMEOUT_SECONDS","8")))
def analyse_post(post):
    if not enabled("AI_MODERATION_ENABLED"):
        post.ai_status=Post.AIStatus.DISABLED;post.save(update_fields=["ai_status"]);return
    prompt=f"Analyse this forum post for potentially misleading or false factual claims. Return JSON only with misinformation_confidence (0 to 1) and rationale (max 240 chars). Opinions and questions should score low.\nTitle: {post.title}\nBody: {post.body}"
    try:
        model=os.getenv("AI_CHAT_MODEL","gpt-4o-mini");result=client().chat.completions.create(model=model,response_format={"type":"json_object"},messages=[{"role":"user","content":prompt}]);data=json.loads(result.choices[0].message.content)
        score=min(1.0,max(0.0,float(data["misinformation_confidence"])));post.ai_status=Post.AIStatus.COMPLETE;post.ai_model=model;post.ai_moderation_score=score;post.ai_moderation_rationale=str(data.get("rationale",""))[:240];post.ai_needs_review=score>=float(os.getenv("AI_MODERATION_THRESHOLD","0.75"));post.save(update_fields=["ai_status","ai_model","ai_moderation_score","ai_moderation_rationale","ai_needs_review"])
    except Exception as exc:
        post.ai_status=Post.AIStatus.FAILED;post.ai_moderation_rationale=f"Analysis unavailable: {type(exc).__name__}";post.save(update_fields=["ai_status","ai_moderation_rationale"])
def analyse_thread_vibe(post):
    if not enabled("AI_VIBE_ENABLED"):
        Post.objects.filter(pk=post.pk).update(vibe_status=Post.AIStatus.DISABLED);return
    comments=list(post.comments.order_by("created_at").values_list("body",flat=True))
    if not comments:
        Post.objects.filter(pk=post.pk).update(vibe=Post.Vibe.UNKNOWN,vibe_status=Post.AIStatus.COMPLETE);return
    prompt="Classify the overall vibe of these forum comments. Return JSON only with vibe exactly one of Toxic, Constructive, Humorous, Informative.\nComments:\n"+"\n---\n".join(comments[-50:])
    try:
        result=client().chat.completions.create(model=os.getenv("AI_CHAT_MODEL","gpt-4o-mini"),response_format={"type":"json_object"},messages=[{"role":"user","content":prompt}]);value=str(json.loads(result.choices[0].message.content)["vibe"]).title();mapped={"Toxic":"toxic","Constructive":"constructive","Humorous":"humorous","Informative":"informative"}.get(value,"unknown");Post.objects.filter(pk=post.pk).update(vibe=mapped,vibe_status=Post.AIStatus.COMPLETE)
    except Exception: Post.objects.filter(pk=post.pk).update(vibe_status=Post.AIStatus.FAILED)
