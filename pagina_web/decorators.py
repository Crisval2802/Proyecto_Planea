from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse

def token_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        try:
            auth = JWTAuthentication()
            user, _ = auth.authenticate(request)
            if not user:
                raise AuthenticationFailed('Invalid token or no user found.')
            request.user = user
        except AuthenticationFailed as e:
            return JsonResponse({'detail': str(e)}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view