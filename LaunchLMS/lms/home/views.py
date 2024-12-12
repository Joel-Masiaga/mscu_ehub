from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator  # Importing method_decorator here
from django.views.generic import TemplateView, View
from django.contrib import messages
from courses.models import Course, Lesson, Module, Enrollment
from quiz.models import Quiz, Question, Answer, QuizAttempt
from django.db.models import F

# Home page view for enrolled and other courses
@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Fetch enrolled courses using prefetch_related to minimize queries
        enrolled_courses = Course.objects.filter(enrollment__user=user)
        
        # Fetch other courses excluding the ones the user is enrolled in
        other_courses = Course.objects.exclude(id__in=enrolled_courses.values('id'))

        context.update({'enrolled_courses': enrolled_courses, 'other_courses': other_courses})
        return context

# Course details view with enrollment functionality
class CourseDetailView(View):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        modules = course.modules.all()
        enrolled = course.enrolled_students.filter(id=request.user.id).exists()  # Check if the user is enrolled
        return render(request, 'home/course_detail.html', {'course': course, 'modules': modules, 'enrolled': enrolled})

    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        action = request.POST.get('action', 'enroll')  # Default action is "enroll"

        if action == 'enroll':
            # Enroll the user in the course
            if not Enrollment.objects.filter(user=request.user, course=course).exists():
                Enrollment.objects.create(user=request.user, course=course)
                messages.success(request, f'You have successfully enrolled in {course.title}!')
            else:
                messages.info(request, f'You are already enrolled in {course.title}.')

            # Redirect to the first lesson if available
            first_lesson = course.modules.first().lessons.first() if course.modules.exists() else None
            if first_lesson:
                return redirect('lesson_detail', pk=first_lesson.pk)

            messages.warning(request, "This course doesn't have any lessons yet.")
            return HttpResponseRedirect(reverse('course_detail', args=[pk]))

        elif action == 'unenroll':
            # Unenroll the user from the course
            enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
            if enrollment:
                # Remove progress (lessons marked as read) for this course
                lessons = Lesson.objects.filter(module__course=course)
                for lesson in lessons:
                    lesson.read_by_users.remove(request.user)
                
                # Delete enrollment
                enrollment.delete()
                messages.success(request, f'You have successfully unenrolled from {course.title} and your progress has been cleared.')
            else:
                messages.warning(request, f'You are not enrolled in {course.title}.')

            return HttpResponseRedirect(reverse('course_detail', args=[pk]))

        # Fallback for invalid actions
        messages.error(request, "Invalid action.")
        return HttpResponseRedirect(reverse('course_detail', args=[pk]))



# Module details view
class ModuleDetailView(View):
    def get(self, request, pk):
        module = get_object_or_404(Module, pk=pk)
        lessons = module.lessons.all()
        return render(request, 'home/module_detail.html', {'module': module, 'lessons': lessons})

# Lesson details view with progress tracking and next/previous navigation
@method_decorator(login_required, name='dispatch')
class LessonDetailView(View):
    def get(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        user = request.user

        # Fetch the course associated with the lesson, along with enrolled students
        course = lesson.module.course
        enrolled_students = course.enrolled_students.all()

        # Check if the user is enrolled in the course
        if user not in enrolled_students:
            return redirect('course_detail', pk=course.pk)

        # Efficiently calculate progress and retrieve next/previous lesson
        modules = course.modules.all().order_by('created_at').prefetch_related('lessons')
        total_lessons = course.modules.all().prefetch_related('lessons').values_list('lessons', flat=True).count()
        completed_lessons = course.modules.all().prefetch_related('lessons').filter(lessons__read_by_users=user).count()
        progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons else 0

        read = lesson.read_by_users.filter(id=user.id).exists()
        previous_lesson = lesson.module.lessons.filter(id__lt=lesson.id).last()
        next_lesson = lesson.module.lessons.filter(id__gt=lesson.id).first()

        # Check if quiz attempt exists
        quiz = lesson.module.quizzes.first() if lesson.module.quizzes.exists() else None
        quiz_attempt = None
        if quiz:
            quiz_attempt = QuizAttempt.objects.filter(student=user, quiz=quiz).first()

        # If no next lesson, check for next module's lesson
        if not next_lesson:
            next_module = lesson.module.course.modules.filter(id__gt=lesson.module.id).first()
            if next_module:
                next_lesson = next_module.lessons.first()

        return render(request, 'home/lesson.html', {
            'lesson': lesson,
            'previous_lesson': previous_lesson,
            'next_lesson': next_lesson,
            'progress_percentage': progress_percentage,
            'read': read,
            'quiz_attempt': quiz_attempt,  # Pass quiz attempt data to the template
        })

    def post(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        user = request.user

        course = lesson.module.course
        enrolled_students = course.enrolled_students.all()

        if user not in enrolled_students:
            return HttpResponse("You are not enrolled in this course.", status=403)

        # Handle mark/unmark as read actions
        if 'mark_read' in request.POST:
            if not lesson.read_by_users.filter(id=user.id).exists():
                lesson.read_by_users.add(user)
        elif 'unmark_read' in request.POST:
            if lesson.read_by_users.filter(id=user.id).exists():
                lesson.read_by_users.remove(user)

        # Efficient progress calculation
        total_lessons = course.modules.all().prefetch_related('lessons').values_list('lessons', flat=True).count()
        completed_lessons = course.modules.all().prefetch_related('lessons').filter(lessons__read_by_users=user).count()
        progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons else 0

        next_lesson = lesson.module.lessons.filter(id__gt=lesson.id).first()

        if not next_lesson:
            next_module = lesson.module.course.modules.filter(id__gt=lesson.module.id).first()
            if next_module:
                next_lesson = next_module.lessons.first()

        return redirect('lesson_detail', pk=next_lesson.id if next_lesson else lesson.id)

    
class QuizDetailView(View):
    @method_decorator(login_required)
    def get(self, request, quiz_id):
        # Get the quiz object
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Ensure the quiz is associated with a module, then access the module and course
        module = quiz.module  # Quiz is linked to a module, not a lesson
        lesson = module.lessons.last() 
        course = module.course
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()

        # Check if the user is enrolled in the course and has completed the module
        # Here we are checking if the user has read any lesson in the module
        if not enrollment or request.user not in module.lessons.first().read_by_users.all():
            return HttpResponse("You must complete the module and be enrolled in the course to take this quiz.", status=403)

        # Fetch all the questions for this quiz
        questions = quiz.questions.all()

        # Render the quiz template
        return render(request, 'quiz/quiz.html', {
            'quiz': quiz,
            'questions': questions,
            'lesson': lesson,  # Pass the lesson to the template
        })


class SubmitQuizView(View):
    @method_decorator(login_required)
    def post(self, request, quiz_id):
        # Get the quiz object
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Ensure the quiz is associated with a module, then access the module and course
        module = quiz.module  # Quiz is linked to a module, not a lesson
        course = module.course
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()

        # Check if the user is enrolled in the course and has completed the module
        if not enrollment or request.user not in module.lessons.first().read_by_users.all():
            return HttpResponse("You must complete the module and be enrolled in the course to take this quiz.", status=403)

        # Initialize the score
        score = 0
        total_questions = quiz.questions.count()

        # Process each question
        for question in quiz.questions.all():
            # Get the selected answer from the POST data
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = get_object_or_404(Answer, id=selected_answer_id)
                if selected_answer.is_correct:
                    score += 1

        # Calculate percentage score
        if total_questions > 0:
            score_percentage = (score / total_questions) * 100
        else:
            score_percentage = 0

        # Store the quiz attempt result
        quiz_attempt, created = QuizAttempt.objects.get_or_create(student=request.user, quiz=quiz)
        quiz_attempt.score = score_percentage
        quiz_attempt.completed = True
        quiz_attempt.save()

        # Provide feedback to the user
        if score_percentage >= 75:
            message = "Congratulations! You passed the quiz. You can now proceed to the next module."
        else:
            message = f"You scored {score_percentage:.2f}%. You need at least 75% to proceed."

        # Redirect or render a result page with feedback
        return render(request, 'quiz/quiz_result.html', {
            'quiz': quiz,
            'score': score,
            'total_questions': total_questions,
            'score_percentage': score_percentage,
            'message': message
        })
