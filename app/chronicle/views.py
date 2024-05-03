from django.shortcuts import render
from django.views.generic import ListView

from chronicle.models import Record


class RecordListView(ListView):
    model = Record
    template_name = 'chronicle/records_list.html'
    context_object_name = 'records'

