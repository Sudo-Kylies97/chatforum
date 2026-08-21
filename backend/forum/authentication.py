import hashlib
from django.utils import timezone
from rest_framework import authentication, exceptions
from .models import PersonalAPIToken


class PersonalTokenAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode().split()
        if not header or header[0].lower() != self.keyword.lower():
            return None
        if len(header) != 2:
            raise exceptions.AuthenticationFailed("Invalid bearer token header.")
        digest = hashlib.sha256(header[1].encode()).hexdigest()
        try:
            token = PersonalAPIToken.objects.select_related("user").get(
                digest=digest, revoked_at__isnull=True
            )
        except PersonalAPIToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid or revoked token.")
        PersonalAPIToken.objects.filter(pk=token.pk).update(last_used_at=timezone.now())
        return token.user, token
