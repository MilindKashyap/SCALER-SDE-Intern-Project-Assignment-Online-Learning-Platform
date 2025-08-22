from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.forms import modelformset_factory
from django.db import models # For Max aggregation
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .decorators import instructor_required

from .models import Course
from .forms import CourseForm
from lectures.models import Lecture, ReadingLecture, QuizLecture
from lectures.forms import LectureForm, ReadingLectureForm, QuestionForm
from quizzes.models import Question
from enrollments.models import Enrollment
from progress.models import Progress
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication # Import SessionAuthentication


class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True)
        
        # Add search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(instructor__username__icontains=search_query) |
                Q(instructor__first_name__icontains=search_query) |
                Q(instructor__last_name__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        user = self.request.user

        is_enrolled = False
        progress = None
        completed_lectures_count = 0
        total_lectures_count = Lecture.objects.filter(course=course).count()
        progress_percentage = 0

        if user.is_authenticated and user.role == 'STUDENT':
            is_enrolled = Enrollment.objects.filter(student=user, course=course).exists()
            if is_enrolled:
                enrollment = Enrollment.objects.get(student=user, course=course)
                progress, created = Progress.objects.get_or_create(enrollment=enrollment)
                completed_lectures_count = len(progress.completed_lecture_ids)
                progress_percentage = (completed_lectures_count / total_lectures_count) * 100 if total_lectures_count > 0 else 0
        
        context['is_enrolled'] = is_enrolled
        context['lectures'] = Lecture.objects.filter(course=course).order_by('order_index')
        context['progress'] = progress
        context['completed_lectures_count'] = completed_lectures_count
        context['total_lectures_count'] = total_lectures_count
        context['progress_percentage'] = round(progress_percentage)

        return context

class CourseDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication] # Add SessionAuthentication

    def get_object(self, pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        course = self.get_object(pk)
        # Ensure only instructor of the course can update
        if request.user != course.instructor:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        # Handle partial updates, specifically for is_published
        is_published_str = request.data.get('is_published')
        if is_published_str is not None:
            course.is_published = is_published_str # Directly assign the boolean value
            course.save()
            return Response({"status": "success", "is_published": course.is_published})
        
        # If other fields are to be updated, a serializer would be used here
        return Response({"detail": "Invalid update request."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        course = self.get_object(pk)
        # Ensure only instructor of the course can delete
        if request.user != course.instructor:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def course_create_view(request):
    if not request.user.is_authenticated or request.user.role != 'INSTRUCTOR':
        messages.warning(request, "You do not have permission to create courses.")
        return redirect('/auth/login')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('instructor_course_manage', pk=course.pk)
        else:
            messages.error(request, 'Error creating course.')
    else:
        form = CourseForm()
    return render(request, 'courses/instructor/course_new.html', {'form': form})

def course_manage_view(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)

    if request.user.role != 'INSTRUCTOR':
        messages.warning(request, "You do not have permission to manage this course.")
        return redirect('/auth/login')

    lectures = Lecture.objects.filter(course=course).order_by('order_index')
    quizzes = QuizLecture.objects.filter(lecture__course=course).order_by('lecture__order_index')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_lecture':
            # Handle lecture creation
            lecture_title = request.POST.get('lecture_title')
            lecture_description = request.POST.get('lecture_description', '')
            lecture_file = request.FILES.get('lecture_file')
            
            if not lecture_title or not lecture_file:
                messages.error(request, 'Lecture title and PDF file are required.')
            else:
                try:
                    # Create lecture
                    latest_order_index = Lecture.objects.filter(course=course).aggregate(models.Max('order_index'))['order_index__max'] or 0
                    lecture = Lecture.objects.create(
                        course=course,
                        title=lecture_title,
                        type='PDF',
                        order_index=latest_order_index + 1
                    )
                    
                    # Create reading lecture with file
                    reading_lecture = ReadingLecture.objects.create(
                        lecture=lecture,
                        file=lecture_file
                    )
                    
                    messages.success(request, 'Lecture added successfully!')
                    return redirect('instructor_course_manage', pk=course.pk)
                    
                except Exception as e:
                    messages.error(request, f'Error adding lecture: {str(e)}')
        
        elif action == 'add_quiz':
            # Handle quiz creation with questions in one step
            quiz_title = request.POST.get('quiz_title')
            quiz_description = request.POST.get('quiz_description', '')
            quiz_start_date = request.POST.get('quiz_start_date')
            quiz_end_date = request.POST.get('quiz_end_date')
            quiz_duration = request.POST.get('quiz_duration')
            quiz_questions_count = request.POST.get('quiz_questions_count')
            
            print(f"DEBUG: Quiz creation data:")
            print(f"Title: {quiz_title}")
            print(f"Start Date: {quiz_start_date}")
            print(f"End Date: {quiz_end_date}")
            print(f"Duration: {quiz_duration}")
            print(f"Questions Count: {quiz_questions_count}")
            
            if not all([quiz_title, quiz_start_date, quiz_end_date, quiz_duration, quiz_questions_count]):
                messages.error(request, 'All quiz fields are required.')
            else:
                try:
                    # Parse datetime strings to datetime objects
                    from datetime import datetime
                    from django.utils import timezone
                    import pytz
                    
                    # Parse the datetime strings and make them timezone-aware
                    start_date = datetime.fromisoformat(quiz_start_date.replace('T', ' '))
                    end_date = datetime.fromisoformat(quiz_end_date.replace('T', ' '))
                    
                    # Make them timezone-aware
                    start_date = timezone.make_aware(start_date)
                    end_date = timezone.make_aware(end_date)
                    
                    # Create lecture for quiz
                    latest_order_index = Lecture.objects.filter(course=course).aggregate(models.Max('order_index'))['order_index__max'] or 0
                    lecture = Lecture.objects.create(
                        course=course,
                        title=quiz_title,
                        type='QUIZ',
                        order_index=latest_order_index + 1
                    )
                    
                    # Create quiz lecture with time constraints
                    quiz_lecture = QuizLecture.objects.create(
                        lecture=lecture,
                        start_date=start_date,
                        end_date=end_date,
                        duration=int(quiz_duration)
                    )
                    
                    print(f"DEBUG: Quiz lecture created with ID: {quiz_lecture.pk}")
                    
                    # Process questions
                    question_count = 0
                    while f'question_{question_count}_text' in request.POST:
                        question_text = request.POST.get(f'question_{question_count}_text')
                        options = [
                            request.POST.get(f'question_{question_count}_option_0'),
                            request.POST.get(f'question_{question_count}_option_1'),
                            request.POST.get(f'question_{question_count}_option_2'),
                            request.POST.get(f'question_{question_count}_option_3')
                        ]
                        correct_index = request.POST.get(f'question_{question_count}_correct')
                        
                        print(f"DEBUG: Question {question_count}: {question_text}")
                        print(f"DEBUG: Options: {options}")
                        print(f"DEBUG: Correct: {correct_index}")
                        
                        if question_text and all(options) and correct_index is not None:
                            Question.objects.create(
                                quiz=quiz_lecture,
                                text=question_text,
                                options=options,
                                correct_index=int(correct_index)
                            )
                            print(f"DEBUG: Question {question_count} created successfully")
                        
                        question_count += 1
                    
                    messages.success(request, 'Quiz created successfully!')
                    return redirect('instructor_course_manage', pk=course.pk)
                    
                except Exception as e:
                    print(f"DEBUG: Error creating quiz: {str(e)}")
                    messages.error(request, f'Error creating quiz: {str(e)}')
        
        elif action == 'save_quiz':
            # This action is no longer needed as we handle everything in add_quiz
            messages.error(request, 'Invalid action.')

    context = {
        'course': course,
        'lectures': lectures,
        'quizzes': quizzes,
    }
    return render(request, 'courses/instructor/course_manage.html', context)

@login_required
@instructor_required
def delete_course_view(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('instructor_dashboard') # Redirect to instructor dashboard or course list
    return redirect('instructor_course_manage', pk=pk) # Redirect back if not a POST request
