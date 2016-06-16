from datetime import datetime
from django.shortcuts import render
from calaccess_raw.models.tracking import RawDataVersion, RawDataFile


def versions_list(request):
    context = {
        'versions_list': RawDataVersion.objects.order_by('-release_datetime'),
    }
    return render(request, 'versions_list.html', context)


def version(request, version):
    context = {
        'version': RawDataVersion.objects.filter(
            release_datetime__date=datetime.strptime(version, '%Y-%m-%d')
        )[0]
    }
    return render(request, 'version.html', context)


def latest_version(request):
    context = {
        'version': RawDataVersion.objects.latest('release_datetime')
    }
    return render(request, 'version.html', context)


def data_files_list(request):
    context = {
        'files_list': RawDataFile.objects.distinct('file_name').order_by('file_name')
    }
    return render(request, 'data_files_list.html', context)


def data_file(request, file_name):
    file_name_upper = file_name.upper()
    context = {
        'file_name': file_name_upper,
        'file_versions': RawDataFile.objects.filter(file_name=file_name_upper).order_by('-id'),
    }
    return render(request, 'data_file.html', context)
