from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.shortcuts import get_object_or_404, redirect, render
from courses.models import Course
from lectures.models import Lecture, ReadingLecture, QuizLecture
from quizzes.models import Question
from enrollments.models import Enrollment
from progress.models import Progress
from .serializers import LectureSerializer, ReadingLectureSerializer, QuestionSerializer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from .forms import LectureForm, ReadingLectureForm, QuestionForm
from courses.decorators import student_required
from .models import Lecture, ReadingLecture, QuizLecture
from enrollments.models import Enrollment
from progress.models import Progress # Import the Progress model
from quizzes.forms import QuizAttemptForm # Assuming you'll create this later
from quizzes.models import QuizSubmission, Answer # Import QuizSubmission and Answer models


class IsInstructorForLecture(permissions.BasePermission):
    """
    Custom permission to only allow instructors to edit their own lectures.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'INSTRUCTOR'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.course.instructor == request.user

class IsEnrolledStudent(permissions.BasePermission):
    """
    Custom permission to only allow enrolled students to view and interact with lectures.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'STUDENT':
            course_id = view.kwargs.get('course_pk') or request.parser_context['kwargs']['course_pk']
            if course_id:
                return Enrollment.objects.filter(student=request.user, course_id=course_id).exists()
        return False

class LectureListCreateView(generics.ListCreateAPIView):
    serializer_class = LectureSerializer
    permission_classes = [IsInstructorForLecture]

    def get_queryset(self):
        course_id = self.kwargs['course_pk']
        return Lecture.objects.filter(course_id=course_id)

    def perform_create(self, serializer):
        course_id = self.kwargs['course_pk']
        course = get_object_or_404(Course, pk=course_id, instructor=self.request.user)
        order_index = Lecture.objects.filter(course=course).count() + 1
        lecture = serializer.save(course=course, order_index=order_index)
        
        # Create associated ReadingLecture or QuizLecture based on type
        if lecture.type == 'READING':
            ReadingLecture.objects.create(lecture=lecture)
        elif lecture.type == 'QUIZ':
            QuizLecture.objects.create(lecture=lecture)


class LectureAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsInstructorForLecture]
    authentication_classes = [SessionAuthentication] # Add SessionAuthentication
    lookup_url_kwarg = 'pk' # This is the default, but explicitly setting it.


class CompleteReadingLectureView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsEnrolledStudent]

    def post(self, request, lecture_pk):
        lecture = get_object_or_404(Lecture, pk=lecture_pk, type__in=['READING', 'VIDEO', 'PDF']) # Allow VIDEO and PDF
        enrollment = get_object_or_404(Enrollment, student=request.user, course=lecture.course)
        progress, created = Progress.objects.get_or_create(enrollment=enrollment)

        if lecture.id not in progress.completed_lecture_ids:
            progress.completed_lecture_ids.append(lecture.id)
            progress.save()
        return Response({'detail': 'Reading lecture marked as complete.'}, status=status.HTTP_200_OK)


class SubmitQuizLectureView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsEnrolledStudent]

    def post(self, request, lecture_pk):
        quiz_lecture = get_object_or_404(QuizLecture, lecture__pk=lecture_pk)
        enrollment = get_object_or_404(Enrollment, student=request.user, course=quiz_lecture.lecture.course)
        progress, created = Progress.objects.get_or_create(enrollment=enrollment)

        answers = request.data.get('answers', {})
        score = 0
        total_questions = quiz_lecture.questions.count()

        for question in quiz_lecture.questions.all():
            user_answer_index = answers.get(str(question.id))
            if user_answer_index is not None and int(user_answer_index) == question.correct_index:
                score += 1
        
        percentage_score = (score / total_questions) * 100 if total_questions > 0 else 0
        passed = percentage_score >= 70

        progress.scores[str(quiz_lecture.lecture.id)] = percentage_score
        if passed and quiz_lecture.lecture.id not in progress.completed_lecture_ids:
            progress.completed_lecture_ids.append(quiz_lecture.lecture.id)
        progress.save()

        return Response({
            'detail': 'Quiz submitted and graded.',
            'score': percentage_score,
            'passed': passed
        }, status=status.HTTP_200_OK)


class InstructorCourseLecturesView(generics.ListAPIView):
    serializer_class = LectureSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructorForLecture]

    def get_queryset(self):
        course_id = self.kwargs['course_pk']
        course = get_object_or_404(Course, pk=course_id, instructor=self.request.user)
        return course.lectures.all()

def lecture_detail_view(request, course_pk, lecture_pk):
    lecture = get_object_or_404(Lecture, course__pk=course_pk, pk=lecture_pk)
    course = lecture.course
    user = request.user

    if not user.is_authenticated or user.role != 'STUDENT':
        messages.warning(request, "You must be an enrolled student to view lectures.")
        return redirect('/auth/login')

    enrollment = get_object_or_404(Enrollment, student=user, course=course)
    progress, created = Progress.objects.get_or_create(enrollment=enrollment)

    # Check if previous lecture is completed (gated navigation)
    lectures_in_course = Lecture.objects.filter(course=course).order_by('order_index')
    previous_lecture = None
    for i, lec in enumerate(lectures_in_course):
        if lec.pk == lecture.pk and i > 0:
            previous_lecture = lectures_in_course[i-1]
            break

    if previous_lecture and previous_lecture.id not in progress.completed_lecture_ids:
        messages.warning(request, "Please complete the previous lecture first.")
        return redirect('course-detail-public', pk=course_pk) # Redirect to course detail or previous lecture

    context = {
        'course': course,
        'lecture': lecture,
        'is_completed': lecture.id in progress.completed_lecture_ids,
        'progress': progress,
    }

    if lecture.type == 'READING':
        reading_lecture = get_object_or_404(ReadingLecture, lecture=lecture)
        context['reading_lecture'] = reading_lecture
        # Auto-complete reading lecture on view
        if lecture.id not in progress.completed_lecture_ids:
            progress.completed_lecture_ids.append(lecture.id)
            progress.save()
            messages.success(request, 'Reading lecture marked as complete!')
            # After completing, check for the next lecture
            next_lecture = Lecture.objects.filter(course=course, order_index__gt=lecture.order_index).order_by('order_index').first()
            if next_lecture:
                context['next_lecture_id'] = next_lecture.id

    elif lecture.type == 'QUIZ':
        quiz_lecture = get_object_or_404(QuizLecture, lecture=lecture)
        questions = quiz_lecture.questions.all()
        context['quiz_lecture'] = quiz_lecture
        context['questions'] = questions
        context['quiz_score'] = progress.scores.get(str(lecture.id), 0)
        context['quiz_passed'] = progress.scores.get(str(lecture.id), 0) >= 70

    return render(request, 'lectures/lecture_detail.html', context)

@login_required
@student_required
def lecture_detail_view(request, lecture_pk):
    lecture = get_object_or_404(Lecture, pk=lecture_pk)
    course = lecture.course
    user = request.user

    # Check if student is enrolled in the course
    is_enrolled = Enrollment.objects.filter(student=user, course=course).exists()
    if not is_enrolled:
        messages.warning(request, "You must be enrolled in this course to view lectures.")
        return redirect('course-detail-public', pk=course.pk)

    # Get student's progress for this enrollment
    enrollment = get_object_or_404(Enrollment, student=user, course=course)
    progress, created = Progress.objects.get_or_create(enrollment=enrollment)

    # Determine if the lecture is accessible (e.g., if previous lectures are completed)
    lectures_in_course = Lecture.objects.filter(course=course).order_by('order_index')
    accessible = True
    for l in lectures_in_course:
        if l.order_index < lecture.order_index and l.id not in progress.completed_lecture_ids:
            accessible = False
            break

    if not accessible and lecture.order_index != 1: # First lecture is always accessible
        messages.warning(request, "Please complete previous lectures to access this one.")
        return redirect('course-detail-public', pk=course.pk)

    context = {
        'lecture': lecture,
        'course': course,
        'is_enrolled': is_enrolled,
        'progress': progress,
        'reading_lecture': None,
        'quiz_lecture': None,
        'quiz_form': None, # Initialize quiz_form
        'is_completed': lecture.id in progress.completed_lecture_ids,
    }

    if lecture.type == 'READING' or lecture.type == 'PDF':
        context['reading_lecture'] = get_object_or_404(ReadingLecture, lecture=lecture)
    elif lecture.type == 'QUIZ':
        quiz_lecture = get_object_or_404(QuizLecture, lecture=lecture)
        context['quiz_lecture'] = quiz_lecture

        if request.method == 'POST':
            form = QuizAttemptForm(request.POST, quiz_lecture=quiz_lecture)
            if form.is_valid():
                submission = QuizSubmission.objects.create(
                    quiz_lecture=quiz_lecture,
                    student=user
                )
                for question in quiz_lecture.questions.all():
                    selected_option_index = form.cleaned_data[f'question_{question.pk}']
                    Answer.objects.create(
                        submission=submission,
                        question=question,
                        selected_option_index=int(selected_option_index)
                    )
                messages.success(request, "Quiz submitted successfully! Your results will be graded by the instructor.")
                return redirect('lecture_detail', lecture_pk=lecture.pk) # Redirect back to lecture detail or next lecture
            else:
                messages.error(request, "Error submitting quiz. Please check your answers.")
        else:
            form = QuizAttemptForm(quiz_lecture=quiz_lecture)
        context['quiz_form'] = form

    return render(request, 'lectures/lecture_detail.html', context)

@login_required
@student_required
def mark_lecture_as_done(request, lecture_pk):
    lecture = get_object_or_404(Lecture, pk=lecture_pk)
    course = lecture.course
    user = request.user

    enrollment = get_object_or_404(Enrollment, student=user, course=course)
    progress, created = Progress.objects.get_or_create(enrollment=enrollment)

    if lecture.id not in progress.completed_lecture_ids:
        progress.completed_lecture_ids.append(lecture.id)
        progress.save()
        messages.success(request, f"Lecture '{lecture.title}' marked as done!")
    else:
        messages.info(request, f"Lecture '{lecture.title}' was already marked as done.")

    # Find the next lecture to redirect to
    next_lecture = Lecture.objects.filter(course=course, order_index__gt=lecture.order_index).order_by('order_index').first()
    if next_lecture:
        return redirect('lecture_detail', lecture_pk=next_lecture.pk)
    else:
        messages.info(request, "You have completed all lectures in this course!")
        return redirect('course-detail-public', pk=course.pk)


@login_required
def lecture_edit_view(request, course_pk, lecture_pk):
    lecture = get_object_or_404(Lecture, course__pk=course_pk, pk=lecture_pk, course__instructor=request.user)
    course = lecture.course

    # Ensure only instructor of the course can edit
    if request.user.role != 'INSTRUCTOR' or request.user != course.instructor:
        messages.warning(request, "You do not have permission to edit this lecture.")
        return redirect('/auth/login')

    # Initialize forms based on lecture type
    lecture_form = LectureForm(instance=lecture)
    reading_lecture_form = ReadingLectureForm()
    question_formset = modelformset_factory(Question, form=QuestionForm, extra=0)(queryset=Question.objects.none())

    if lecture.type in ['READING', 'VIDEO', 'PDF']:
        reading_lecture, created = ReadingLecture.objects.get_or_create(lecture=lecture)
        reading_lecture_form = ReadingLectureForm(instance=reading_lecture)
    elif lecture.type == 'QUIZ':
        quiz_lecture, created = QuizLecture.objects.get_or_create(lecture=lecture)
        QuestionFormSet = modelformset_factory(Question, form=QuestionForm, extra=0, can_delete=True)
        question_formset = QuestionFormSet(queryset=quiz_lecture.questions.all())

    if request.method == 'POST':
        if 'lecture_form' in request.POST:
            lecture_form = LectureForm(request.POST, request.FILES, instance=lecture) # Pass request.FILES
            if lecture_form.is_valid():
                lecture = lecture_form.save()
                messages.success(request, 'Lecture updated successfully!')
                return redirect('instructor_course_manage', pk=course.pk)
            else:
                messages.error(request, f'Error updating lecture: {lecture_form.errors}')

        elif 'reading_lecture_form' in request.POST:
            reading_lecture, created = ReadingLecture.objects.get_or_create(lecture=lecture)
            reading_lecture_form = ReadingLectureForm(request.POST, request.FILES, instance=reading_lecture) # Pass request.FILES
            if reading_lecture_form.is_valid():
                reading_lecture_form.save()
                messages.success(request, 'Lecture content updated successfully!')
                return redirect('lecture_edit', course_pk=course.pk, lecture_pk=lecture.pk)
            else:
                messages.error(request, f'Error updating reading content: {reading_lecture_form.errors}')

        elif 'question_formset' in request.POST:
            quiz_lecture, created = QuizLecture.objects.get_or_create(lecture=lecture)
            QuestionFormSet = modelformset_factory(Question, form=QuestionForm, extra=0, can_delete=True)
            question_formset = QuestionFormSet(request.POST, queryset=quiz_lecture.questions.all())
            if question_formset.is_valid():
                for form in question_formset:
                    if form.instance.pk and form.cleaned_data.get('DELETE'):
                        form.instance.delete()
                    else:
                        question = form.save(commit=False)
                        question.quiz = quiz_lecture
                        question.save()
                messages.success(request, 'Quiz questions updated successfully!')
                return redirect('lecture_edit', course_pk=course.pk, lecture_pk=lecture.pk)
            else:
                messages.error(request, f'Error updating quiz questions: {question_formset.errors}')

    context = {
        'course': course,
        'lecture': lecture,
        'lecture_form': lecture_form,
        'reading_lecture_form': reading_lecture_form,
        'question_formset': question_formset,
    }
    return render(request, 'lectures/lecture_edit.html', context)
