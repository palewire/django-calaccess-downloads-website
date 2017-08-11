from itertools import groupby
from calaccess_raw.models import RawDataFile
from calaccess_raw.annotations import FilingForm
from calaccess_processed.models import ProcessedDataFile


class CalAccessModelListMixin(object):
    """
    Processes lists of CAL-ACCESS models to be better organized.
    """
    def get_klass_group(self, model_or_obj):
        # If it's a RawDataFile do our trick
        if (
            isinstance(model_or_obj, RawDataFile)
            or isinstance(model_or_obj, ProcessedDataFile)
        ):
            return model_or_obj.model().klass_group
        # If it's a FilingForm also do our trick
        elif isinstance(model_or_obj, FilingForm):
            return model_or_obj.group
        # If it's an object go ahead
        elif isinstance(model_or_obj.klass_group, str):
            return model_or_obj.klass_group
        # If not you will need to call it first with ()
        else:
            return model_or_obj().klass_group

    def sort_klass_group(self, group):
        """
        Accepts a klass group name and prepares it for sorting.
        """
        # Sort inactive and deprecated groups to the end.
        group = group.replace("inactive", "z")
        group = group.replace("Deprecated", "z")
        return group

    def regroup_by_klass_group(self, model_list):
        """
        Accepts a model list and returns them regrouped by klass_group
        """
        # First sort by the klass group
        l = sorted(model_list, key=lambda obj: self.get_klass_group(obj))

        # Group the model list by klass_group
        l = [
            {'grouper': key, 'list': list(val)}
            for key, val in
            groupby(l, lambda obj: self.get_klass_group(obj))
        ]

        # Sort the inactive and deprecated models to the end
        l = sorted(l, key=lambda d: self.sort_klass_group(d['grouper']))

        # Return the list
        return l
