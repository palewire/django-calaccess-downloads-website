from itertools import groupby
from calaccess_raw.annotations import FilingForm


class CalAccessModelListMixin(object):
    """
    Processes lists of CAL-ACCESS models to be better organized.
    """
    def get_klass_group(self, model_or_obj):
        # If it's a raw or processed file do our trick
        if 'calaccess_raw' in str(model_or_obj):
            return model_or_obj().klass_group
        elif 'calaccess_processed' in str(model_or_obj):
            return "Flat" if model_or_obj().is_flat else "Relational"
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
        sorted_list = sorted(
            model_list, key=lambda obj: self.get_klass_group(obj)
        )

        # Group the model list by klass_group
        grouped_list = [
            {'grouper': key, 'list': list(val)}
            for key, val in
            groupby(sorted_list, lambda obj: self.get_klass_group(obj))
        ]

        # Sort the inactive and deprecated models to the end
        resorted_groups = sorted(
            grouped_list, key=lambda d: self.sort_klass_group(d['grouper'])
        )

        # Return the list
        return resorted_groups
