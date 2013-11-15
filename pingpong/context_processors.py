from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from django.contrib.auth import REDIRECT_FIELD_NAME


def login_url_with_redirect(request):
    login_url = reverse('auth_login')
    path = urlquote(request.get_full_path())
    url = '%s?%s=%s' % (login_url, REDIRECT_FIELD_NAME, path)
    return {'login_url': url}