from django.contrib import admin
from .models import Course, Module, Lesson, Enrollment

# Inline for Lesson within Module
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'content', 'image_content', 'video_content', 'additional_material']
    show_change_link = True

# Inline for Module within Course
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ['title', 'objectives', 'content', 'image_content', 'video_content']
    show_change_link = True
    inlines = [LessonInline]  # Nest LessonInline within ModuleInline

# Admin for Course
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at']
    search_fields = ['title', 'description']
    list_filter = ['created_by', 'created_at']  # You can filter courses by the tutor and creation date
    inlines = [ModuleInline]  # Include ModuleInline to manage modules within a course

# Admin for Enrollment
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'date_enrolled']
    search_fields = ['user__email', 'course__title']
    list_filter = ['date_enrolled', 'course__title', 'user__email']

# Register models with admin site
admin.site.register(Course, CourseAdmin)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Enrollment, EnrollmentAdmin)
