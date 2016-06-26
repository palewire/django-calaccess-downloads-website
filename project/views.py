from datetime import datetime
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from calaccess_raw import get_model_list
from calaccess_raw.models.tracking import RawDataVersion, RawDataFile


class VersionList(ListView):
    queryset = RawDataVersion.objects.order_by('-release_datetime')
    template_name = 'versions_list.html'
    context_object_name = 'versions'


class VersionDetail(DetailView):
    template_name = 'version.html'
    context_object_name = 'version'

    def get_object(self):
        object = get_object_or_404(
            RawDataVersion,
            release_datetime__date=datetime.strptime(
                self.kwargs['version'], '%Y-%m-%d',
            )
        )
        return object


class LatestVersion(VersionDetail):

    def get_object(self):
        try:
            object = RawDataVersion.objects.latest('release_datetime')
        except RawDataVersion.DoesNotExist:
            raise Http404("No versions found.")
        else:
            return object


class RawDataFileList(ListView):
    queryset = get_model_list()
    template_name = 'raw_data_files_list.html'
    context_object_name = 'raw data files'


class RawDataFileDetail(DetailView):
    template_name = 'raw_data_file.html'
    context_object_name = 'raw data file'

    def get_object(self):
        obj_search = [
            x for x in get_model_list() 
            if x().get_tsv_name() == self.kwargs['file_name'].upper() + '.TSV'
        ]
        
        if len(obj_search) == 0:
            raise Http404("No versions found.")
        else:
            return obj_search[0]

    def get_context_data(self, **kwargs):
        context = super(RawDataFileDetail, self).get_context_data(**kwargs)

        context['file_versions'] = RawDataFile.objects.filter(
            file_name=self.kwargs['file_name'].upper()
        ).order_by('-version__release_datetime')

        return context
