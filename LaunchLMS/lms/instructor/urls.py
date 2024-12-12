from django.urls import path
from .views import (
    CourseListView, CourseCreateView, CourseEditView,
    ModuleCreateView, ModuleEditView, LessonCreateView, LessonEditView, CourseDetailView
)

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='instructor_courses'),
    path('course/<int:course_id>/', CourseDetailView.as_view(), name='instructor_course_detail'),
    path('courses/create/', CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', CourseEditView.as_view(), name='course_edit'),
    path('modules/<int:course_id>/create/', ModuleCreateView.as_view(), name='module_create'),
    path('modules/<int:pk>/edit/', ModuleEditView.as_view(), name='module_edit'),
    path('modules/<int:pk>/edit/', ModuleEditView.as_view(), name='module_delete'),
    path('lessons/<int:module_id>/create/', LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:pk>/edit/', LessonEditView.as_view(), name='lesson_edit'),
    path('lessons/<int:pk>/edit/', LessonEditView.as_view(), name='lesson_delete'),
]