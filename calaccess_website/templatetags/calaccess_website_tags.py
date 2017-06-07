import os
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
    if is_latest:
        # Split off the file name
        filepath = os.path.basename(file_path)
        # Special hack for the clean biggie zip
        if filepath.startswith("clean_"):
            filepath = "clean.zip"
        # Concoct the latest URL
        path = os.path.join(
            "calaccess.download",
            'latest',
            filepath
        )
    # If not we can just join it to the subject name
    else:
        path = os.path.join("calaccess.download", file_path)

    # Either way, join it to the base and pass it back
    return "https://{}".format(path)


@register.filter
@defaultfilters.stringfilter
def slugify(value):
    """
    Extend the default slugify filter to replace underscores with hyphens.
    """
    return defaultfilters.slugify(value).replace('_', '-')


@register.filter
@defaultfilters.stringfilter
def first_line(text):
    """
    Return only the first line of a text block.
    """
    return text.split('\n')[0]
