from django.urls import path
from . import views
from .views import LessonDetailView, ModuleDetailView, CourseDetailView, QuizDetailView, SubmitQuizView


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('module/<int:pk>/', ModuleDetailView.as_view(), name='module_detail'),
    path('lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),


 # Quiz detail view (to display the quiz and questions)
    path('quiz/<int:quiz_id>/', QuizDetailView.as_view(), name='quiz_detail'),

    # Submit quiz view (when the student submits their answers)
    path('quiz/<int:quiz_id>/submit/', SubmitQuizView.as_view(), name='submit_quiz'),
]
