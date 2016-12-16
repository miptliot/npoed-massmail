# coding=utf-8
from django.conf import settings
from django.contrib.sites.models import Site


def get_prefix_and_site():
    return {
        'prefix': getattr(settings, 'URL_PREFIX', 'https'),
        'site': Site.objects.get_current().domain,
        'PLATFORM_NAME': getattr(settings, 'PLATFORM_NAME', u'Задайте название платформы'),
    }


def get_host_url(request):
    """
    request.get_host возвращает некрасивый адрес http://host:80, поэтому пишем свою балалайку
    :return: корневой url сайта
    """
    host = request.get_host()
    scheme = request.scheme

    if ':' in host:
        _host, port = host.rsplit(':', 1)
        if (scheme == 'http' and port == '80') or (scheme == 'https' and port == '443'):
            host = _host

    return '{}://{}'.format(scheme, host)
