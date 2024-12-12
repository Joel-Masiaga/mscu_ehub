from django.db import models
from users.models import User
from ckeditor.fields import RichTextField

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = RichTextField(blank=True, null=True)
    objectives = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})
    enrolled_students = models.ManyToManyField(User, related_name='enrolled_courses', through='Enrollment', blank=True)  # Use Enrollment through model
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created_at']

    def progress(self, user):
        # Calculate lesson progress
        total_lessons = self.modules.all().prefetch_related('lessons').count()
        completed_lessons = self.modules.all().prefetch_related('lessons').filter(lessons__read=True, lessons__enrollment__user=user).count()
        lesson_progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0

        # Calculate quiz progress
        total_quizzes = self.quizzes.count()
        completed_quizzes = self.quizzes.filter(attempts__student=user, attempts__completed=True).distinct().count()
        quiz_progress = (completed_quizzes / total_quizzes) * 100 if total_quizzes > 0 else 0

        # Combine lesson and quiz progress
        return (lesson_progress + quiz_progress) / 2 

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = RichTextField(blank=True, null=True)
    image_content = models.ImageField(upload_to='module_images/', blank=True, null=True)
    objectives = models.TextField(blank=True, null=True)
    content = RichTextField(blank=True, null=True)
    video_content = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['created_at']

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = RichTextField(blank=True, null=True)
    objectives = models.TextField(blank=True, null=True)
    image_content = models.ImageField(upload_to='lesson_images/', blank=True, null=True)
    content = RichTextField(blank=True, null=True)
    video_content = models.URLField(blank=True, null=True)
    additional_material = models.URLField(blank=True, null=True)
    read_by_users = models.ManyToManyField(User, related_name='read_lessons', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.module.course.title} - {self.module.title} - {self.title}"
    
    class Meta:
        ordering = ['created_at']

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} enrolled in {self.course.title}"
