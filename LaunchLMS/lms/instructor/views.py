from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView
from django.contrib import messages
from courses.models import Course, Module, Lesson
from django.db.models import F

# Decorator to restrict access to instructors only
def instructor_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.role != "instructor":
            return HttpResponse("Access denied. This section is for instructors only.", status=403)
        return view_func(request, *args, **kwargs)

    return _wrapped_view_func

# Course Management Views
@method_decorator([login_required, instructor_required], name='dispatch')
class CourseListView(TemplateView):
    template_name = "instructor/instructor_course_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.filter(created_by=self.request.user)
        return context

@method_decorator([login_required, instructor_required], name='dispatch')
class CourseDetailView(TemplateView):
    template_name = "instructor/instructor_course_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        context['course'] = course
        context['modules'] = course.modules.all()  # Assuming related_name='modules'
        return context


@method_decorator([login_required, instructor_required], name='dispatch')
class CourseCreateView(View):
    def get(self, request):
        return render(request, 'instructor/course_form.html')

    def post(self, request):
        title = request.POST['title']
        description = request.POST['description']
        objectives = request.POST['objectives']
        image = request.FILES.get('image')

        Course.objects.create(
            title=title,
            description=description,
            objectives=objectives,
            image=image,
            created_by=request.user
        )

        messages.success(request, "Course created successfully!")
        return redirect('instructor_courses')

@method_decorator([login_required, instructor_required], name='dispatch')
class CourseEditView(View):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk, created_by=request.user)
        return render(request, 'instructor/course_form.html', {'course': course})

    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, created_by=request.user)

        course.title = request.POST['title']
        course.description = request.POST['description']
        course.objectives = request.POST['objectives']
        if 'image' in request.FILES:
            course.image = request.FILES['image']
        course.save()

        messages.success(request, "Course updated successfully!")
        return redirect('instructor_courses')

# Module Management Views
@method_decorator([login_required, instructor_required], name='dispatch')
class ModuleCreateView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, created_by=request.user)
        return render(request, 'instructor/module_form.html', {'course': course})

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, created_by=request.user)

        title = request.POST['title']
        description = request.POST['description']

        Module.objects.create(
            course=course,
            title=title,
            description=description
        )

        messages.success(request, "Module created successfully!")
        return redirect('instructor_courses')

@method_decorator([login_required, instructor_required], name='dispatch')
class ModuleEditView(View):
    def get(self, request, pk):
        module = get_object_or_404(Module, pk=pk, course__creator=request.user)
        return render(request, 'instructor/module_form.html', {'module': module})

    def post(self, request, pk):
        module = get_object_or_404(Module, pk=pk, course__creator=request.user)

        module.title = request.POST['title']
        module.description = request.POST['description']
        module.save()

        messages.success(request, "Module updated successfully!")
        return redirect('instructor_courses')

# Lesson Management Views
@method_decorator([login_required, instructor_required], name='dispatch')
class LessonCreateView(View):
    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__creator=request.user)
        return render(request, 'instructor/lesson_form.html', {'module': module})

    def post(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__creator=request.user)

        title = request.POST['title']
        content = request.POST['content']
        video = request.FILES.get('video')

        Lesson.objects.create(
            module=module,
            title=title,
            content=content,
            video=video
        )

        messages.success(request, "Lesson created successfully!")
        return redirect('instructor_courses')

@method_decorator([login_required, instructor_required], name='dispatch')
class LessonEditView(View):
    def get(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk, module__course__creator=request.user)
        return render(request, 'instructor/lesson_form.html', {'lesson': lesson})

    def post(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk, module__course__creator=request.user)

        lesson.title = request.POST['title']
        lesson.content = request.POST['content']
        if 'video' in request.FILES:
            lesson.video = request.FILES['video']
        lesson.save()

        messages.success(request, "Lesson updated successfully!")
        return redirect('instructor_courses')