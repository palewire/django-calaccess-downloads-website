import os
import re
from django import template
from django.template import defaultfilters
from django.utils.safestring import mark_safe
register = template.Library()


@register.simple_tag
def documentcloud_embed(slug):
    """
    Returns a DocumentCloud embed ready to serve.
    """
    template = """<div id="DV-viewer-{slug}" class="DV-container"></div>
<script src="//s3.amazonaws.com/s3.documentcloud.org/viewer/loader.js"></script>
<script>
  DV.load("//www.documentcloud.org/documents/{slug}.js", {{
  container: "#DV-viewer-{slug}",
  width: 680,
  height: 850,
  sidebar: false,
  zoom: 550,
  responsive: true
  }});
</script>"""
    return mark_safe(template.format(slug=slug))


@register.simple_tag
def archive_url(file_path, is_latest=False):
    """
    Accepts the relative path to a CAL-ACCESS file in our achive.

    Returns a fully-qualified absolute URL where it can be downloaded.
    """
    # If this is the 'latest' version of the file the path will need to be hacked
    if os.getenv("CALACCESS_WEBSITE_ENV").upper() == 'PROD':
        # stub = "calaccess.download"  This is currently broken
        stub = "s3-{aws_region_name}.amazonaws.com/{s3_archived_data_bucket}".format(**os.environ)
    else:
        stub = "s3-{aws_region_name}.amazonaws.com/{s3_archived_data_bucket}".format(**os.environ)

    if is_latest:
        # Split off the file name
        file_name = os.path.basename(file_path)
        # Special hack for the zip files
        if file_name.endswith('.zip'):
            file_name = re.sub(
                r'_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}',
                '',
                file_name,
            )

        # Concoct the latest URL
        path = os.path.join(
            stub,
            'latest',
            file_name,
        )
    # If not we can just join it to the subject name
    else:
        path = os.path.join(stub, file_path)

    # Either way, join it to the base and pass it back
    return "https://{}".format(path)


@register.filter
@defaultfilters.stringfilter
def slugify(value):
    """
    Extend the default slugify filter to replace underscores with hyphens.
    """
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', value)
    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
    return defaultfilters.slugify(s2).replace('_', '-')


@register.filter
@defaultfilters.stringfilter
def first_line(text):
    """
    Return only the first line of a text block.
    """
    return text.split('\n')[0]
