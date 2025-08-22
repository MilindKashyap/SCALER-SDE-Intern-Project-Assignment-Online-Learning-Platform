from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from courses.decorators import instructor_required # Assuming you have this decorator
from .models import QuizLecture, QuizSubmission, Answer, Grade
from .forms import GradeForm

# Create your views here.

@login_required
@instructor_required
def quiz_submissions_list(request, lecture_pk):
    quiz_lecture = get_object_or_404(QuizLecture, lecture__pk=lecture_pk, lecture__course__instructor=request.user)
    submissions = QuizSubmission.objects.filter(quiz_lecture=quiz_lecture).order_by('-submitted_at')
    
    context = {
        'quiz_lecture': quiz_lecture,
        'submissions': submissions,
    }
    return render(request, 'quizzes/teacher/submission_list.html', context)

@login_required
@instructor_required
def grade_submission(request, submission_pk):
    submission = get_object_or_404(QuizSubmission, pk=submission_pk, quiz_lecture__lecture__course__instructor=request.user)
    answers = Answer.objects.filter(submission=submission)
    
    try:
        grade = submission.grade
    except Grade.DoesNotExist:
        grade = None

    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            new_grade = form.save(commit=False)
            new_grade.submission = submission
            new_grade.teacher = request.user
            new_grade.save()
            messages.success(request, 'Grade assigned successfully!')
            return redirect('quiz_submissions_list', lecture_pk=submission.quiz_lecture.lecture.pk)
        else:
            messages.error(request, 'Error assigning grade.')
    else:
        form = GradeForm(instance=grade)

    context = {
        'submission': submission,
        'answers': answers,
        'form': form,
        'grade': grade,
    }
    return render(request, 'quizzes/teacher/grade_submission.html', context)

@login_required
def student_quiz_grades(request):
    """View for students to see their quiz grades"""
    if request.user.role != 'STUDENT':
        messages.warning(request, "You do not have permission to view student quiz grades.")
        return redirect('home')
    
    # Get all quiz submissions by the student
    submissions = QuizSubmission.objects.filter(student=request.user).select_related(
        'quiz_lecture__lecture__course'
    ).order_by('-submitted_at')
    
    # Get grades for these submissions
    grades = Grade.objects.filter(submission__student=request.user).select_related(
        'submission__quiz_lecture__lecture__course'
    )
    
    context = {
        'submissions': submissions,
        'grades': grades,
    }
    return render(request, 'quizzes/student/quiz_grades.html', context)

@login_required
def student_quiz_detail(request, submission_pk):
    """View for students to see detailed quiz results"""
    if request.user.role != 'STUDENT':
        messages.warning(request, "You do not have permission to view quiz details.")
        return redirect('home')
    
    submission = get_object_or_404(QuizSubmission, pk=submission_pk, student=request.user)
    answers = Answer.objects.filter(submission=submission)
    
    try:
        grade = submission.grade
    except Grade.DoesNotExist:
        grade = None
    
    context = {
        'submission': submission,
        'answers': answers,
        'grade': grade,
    }
    return render(request, 'quizzes/student/quiz_detail.html', context)
