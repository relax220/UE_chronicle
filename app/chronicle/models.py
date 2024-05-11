from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from services.utils import unique_slugify, image_compress

User = get_user_model()


class ThroughPeopleTag(TaggedItemBase):
    content_object = models.ForeignKey('Record', on_delete=models.CASCADE)


class ThroughPlacesTag(TaggedItemBase):
    content_object = models.ForeignKey('Record', on_delete=models.CASCADE)


class Record(models.Model):
    """
    Запись в хрониках
    """
    class RecordManager(models.Manager):
        """
        Менеджер для модели записи
        """

        def all(self):
            """
            Список статей (SQL запрос с фильтрацией для страницы списка статей)
            """
            return self.get_queryset().select_related('author',).filter(status='published')

        def detail(self):
            """
            Детальная статья (SQL запрос с фильтрацией для страницы со статьёй)
            """
            return self.get_queryset() \
                .select_related('author') \
                .prefetch_related('comments', 'comments__author', 'comments__author__profile') \
                .filter(status='published')

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )

    title = models.CharField(verbose_name='Заголовок', max_length=255)
    short_description = CKEditor5Field(max_length=500, verbose_name='Краткое описание', config_name='extends')
    full_description = CKEditor5Field(verbose_name='Полное описание', config_name='extends')
    slug = models.SlugField(verbose_name='URL', max_length=255, blank=True, unique=True)
    thumbnail = models.ImageField(
        verbose_name='Превью поста',
        blank=True,
        upload_to='images/thumbnails/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))]
    )
    status = models.CharField(choices=STATUS_OPTIONS, default='published', verbose_name='Статус поста', max_length=10)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время обновления')
    date_happened = models.DateField(verbose_name='Дата события', blank=True, null=True)
    author = models.ForeignKey(to=User, verbose_name='Автор', on_delete=models.SET_DEFAULT,
                               related_name='author_records',
                               default=1)
    updater = models.ManyToManyField(to=User, verbose_name='Обновили', blank=True,
                                     related_name='updaters_records', symmetrical=False)

    tags_places = TaggableManager(blank=True, verbose_name='Места', through=ThroughPlacesTag,
                                  related_name='tags_places')
    tags_people = TaggableManager(blank=True, verbose_name='Люди', through=ThroughPeopleTag, related_name='tags_people')

    objects = RecordManager()

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__thumbnail = self.thumbnail if self.pk else None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

        if self.__thumbnail != self.thumbnail and self.thumbnail:
            image_compress(self.thumbnail.path, width=400, height=500)

    def get_absolute_url(self):
        return reverse('records_detail', kwargs={'slug': self.slug})

    class Meta:
        db_table = 'app_records'
        ordering = ['-time_create']
        indexes = [models.Index(fields=['-time_create', 'status', 'date_happened'])]
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'


class Comment(MPTTModel):
    """
    Модель древовидных комментариев
    """

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )

    record = models.ForeignKey(Record, on_delete=models.CASCADE, verbose_name='Статья', related_name='comments')
    author = models.ForeignKey(User, verbose_name='Автор комментария', on_delete=models.CASCADE, related_name='comments_author')
    content = models.TextField(verbose_name='Текст комментария', max_length=3000)
    time_create = models.DateTimeField(verbose_name='Время добавления', auto_now_add=True)
    time_update = models.DateTimeField(verbose_name='Время обновления', auto_now=True)
    status = models.CharField(choices=STATUS_OPTIONS, default='published', verbose_name='Статус комментария', max_length=10)
    parent = TreeForeignKey('self', verbose_name='Родительский комментарий', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    class MTTMeta:
        order_insertion_by = ('-time_create',)

    class Meta:
        db_table = 'app_comments'
        indexes = [models.Index(fields=['-time_create', 'time_update', 'status', 'parent'])]
        ordering = ['-time_create']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author}:{self.content}'
