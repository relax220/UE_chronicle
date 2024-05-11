from django.urls import path
from .views import RecordListView, RecordDetailView, CommentCreateView, RecordCreateView, RecordUpdateView

urlpatterns = [
    path('', RecordListView.as_view(), name='home'),
    path('records/create/', RecordCreateView.as_view(), name='records_create'),
    path('records/<str:slug>/', RecordDetailView.as_view(), name='records_detail'),
    path('records/<str:slug>/update/', RecordUpdateView.as_view(), name='articles_update'),
    path('records/<int:pk>/comments/create/', CommentCreateView.as_view(), name='comment_create_view'),

]
