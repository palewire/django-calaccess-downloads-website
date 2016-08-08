import logging
from calaccess_raw import get_model_list
from calaccess_raw.annotations.filing_forms import all_filing_forms
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Refresh the DocumentCloud cache'

    def handle(self, *args, **options):
        docs = set()
        cached = set()

        for m in get_model_list():
            docs.update(set(m().DOCUMENTCLOUD_PAGES))

        for form in all_filing_forms:
            docs.add(form.documentcloud)

        for doc in docs:
            if doc and doc.metadata_filename not in cached:
                logger.debug('Caching {}'.format(doc.metadata_filename))
                doc._cache_metadata()
                cached.add(doc.metadata_filename)
