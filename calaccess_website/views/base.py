from itertools import groupby
from calaccess_raw.models import RawDataFile
from calaccess_raw.annotations import FilingForm


class CalAccessModelListMixin(object):
    """
    Processes lists of CAL-ACCESS models to be better organized.
    """
    def get_klass_group(self, model_or_obj):
        # If it's a RawDataFile do our trick
        if isinstance(model_or_obj, RawDataFile):
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

        # Sort the inactive models to the end
        l = sorted(l, key=lambda d: d['grouper'].replace("inactive", "z"))

        # Sort deprecated forms to the end
        l = sorted(l, key=lambda d: d['grouper'].replace("Deprecated", "z"))

        # Return the list
        return l