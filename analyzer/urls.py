from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/new/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('projects/<int:project_id>/upload/', views.upload_image, name='upload_image'),
    path('images/<int:image_id>/classify/', views.classify_land_use, name='classify_image'),
    path('projects/<int:project_id>/analyze/', views.analyze_changes, name='analyze_changes'),
    path('results/<int:result_id>/', views.view_results, name='view_results'),
]