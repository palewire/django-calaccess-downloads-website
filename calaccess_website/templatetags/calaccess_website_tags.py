import os
from django import template
from django.conf import settings
from six.moves.urllib import parse as urlparse
from django.template.defaultfilters import stringfilter
register = template.Library()


@register.simple_tag
def archive_url(file_path, is_latest=False):
    """
    Accepts the relative path to a CAL-ACCESS file in our achive.

    Returns a fully-qualified absolute URL where it can be downloaded.
    """
    # Set the base for the URL
    base = "https://s3-{}.amazonaws.com/".format(settings.AWS_S3_REGION_NAME)

    # If this is the 'latest' version of the file the path will need to be hacked
    if is_latest:
        path = os.path.join(
            settings.AWS_STORAGE_BUCKET_NAME,
            'latest',
            os.path.basename(file_path)
        )
    # If not we can just join it to the subject name
    else:
        path = os.path.join(settings.AWS_STORAGE_BUCKET_NAME, file_path)

    # Either way, join it to the base and pass it back
    return urlparse.urljoin(base, path)


@register.filter
@stringfilter
def format_page_anchor(value):
    return value.lower().replace('_', '-')


@register.filter
@stringfilter
def first_line(text):
    return text.split('\n')[0]
