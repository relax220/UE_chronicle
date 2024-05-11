import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from taggit.models import Tag

from chronicle.forms import CommentCreateForm, RecordCreateForm, RecordUpdateForm
from chronicle.models import Record, ThroughPeopleTag, ThroughPlacesTag, Comment
from services.mixins import AuthorRequiredMixin


class RecordListView(ListView):
    model = Record
    template_name = 'chronicle/records_list.html'
    context_object_name = 'records'

    def get_queryset(self):
        parameters = dict(self.request.GET)
        if not parameters:
            return self.model.objects.all()
        start_date = parameters.pop('start_date')[0]
        finish_date = parameters.pop('finish_date')[0]
        if start_date:
            start_date = datetime.datetime.strptime(f'{start_date.replace('-', '')}', "%Y%m%d").date()
        if finish_date:
            finish_date = datetime.datetime.strptime(f'{finish_date.replace('-', '')}', "%Y%m%d").date()
        tags = Tag.objects.filter(name__in=parameters.keys()).values_list('name', flat=True)
        if tags:
            if start_date and finish_date:
                queryset = self.model.objects.filter(date_happened__gte=start_date).filter(
                    date_happened__lte=finish_date).filter(tags_people__name__in=tags)
            elif start_date:
                queryset = self.model.objects.filter(date_happened__gte=start_date).filter(tags_people__name__in=tags)
            elif finish_date:
                queryset = self.model.objects.filter(date_happened__lte=finish_date).filter(tags_people__name__in=tags)
            else:
                queryset = self.model.objects.filter(tags_people__name__in=tags)
        elif (start_date or finish_date) and not tags:
            if start_date and finish_date:
                queryset = self.model.objects.filter(date_happened__gte=start_date)
            elif start_date:
                queryset = self.model.objects.filter(date_happened__gte=start_date)
            else:
                queryset = self.model.objects.filter(date_happened__lte=finish_date)
        else:
            queryset = self.model.objects.all()
        return queryset
        # return self.model.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags_people'] = ThroughPeopleTag.objects.all().order_by('tag__name')
        context['tags_places'] = ThroughPlacesTag.objects.all().order_by('tag__name')
        context['parameters'] = dict(self.request.GET)
        return context


class RecordCreateView(LoginRequiredMixin, CreateView):
    """
    Представление: создание материалов на сайте
    """
    model = Record
    template_name = 'chronicle/records_create.html'
    form_class = RecordCreateForm
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление записи на сайт'
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)


class RecordUpdateView(AuthorRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Представление: обновления материала на сайте
    """
    model = Record
    template_name = 'chronicle/record_update.html'
    context_object_name = 'article'
    form_class = RecordUpdateForm
    login_url = 'home'
    success_message = 'Материал был успешно обновлен'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление записи: {self.object.title}'
        return context

    def form_valid(self, form):
        # form.instance.updater = self.request.user
        form.save()
        return super().form_valid(form)


class RecordDetailView(DetailView):
    model = Record
    template_name = 'chronicle/records_detail.html'
    context_object_name = 'record'
    queryset = model.objects.detail()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['form'] = CommentCreateForm
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentCreateForm
    login_url = 'login'

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.record_id = self.kwargs.get('pk')
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'time_create': comment.time_create.strftime('%Y-%b-%d %H:%M:%S'),
                'avatar': comment.author.profile.avatar.url,
                'content': comment.content,
                'get_absolute_url': comment.author.profile.get_absolute_url()
            }, status=200)

        return redirect(comment.record.get_absolute_url())

    def handle_no_permission(self):
        return JsonResponse({'error': 'Необходимо авторизоваться для добавления комментариев'}, status=400)
