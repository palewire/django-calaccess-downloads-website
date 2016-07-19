from django import template
from six.moves.urllib import parse as urlparse
from django.template.defaultfilters import stringfilter
register = template.Library()


@register.simple_tag
def archive_url(file_path):
    """
    Accepts the relative path to a CAL-ACCESS file in our achive.

    Returns a fully-qualified absolute URL where it can be downloaded.
    """
    base_url = "https://s3-us-west-2.amazonaws.com/django-calaccess/"
    return urlparse.urljoin(base_url, file_path)


@register.filter
@stringfilter
def format_page_anchor(value):
    return value.lower().replace('_', '-')
