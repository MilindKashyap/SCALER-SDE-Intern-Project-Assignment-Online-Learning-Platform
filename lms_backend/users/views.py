from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, MessageForm
from courses.models import Course
from lectures.models import Lecture
from enrollments.models import Enrollment
from progress.models import Progress
from .models import Message
from django.db.models import Q

# For API Views (ensure these are imported early)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserLoginSerializer

User = get_user_model()


# API Views
class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'role': user.role
                }, status=status.HTTP_200_OK)
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Template-based Views
def home_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'STUDENT':
            return redirect('student_dashboard')
        elif request.user.role == 'INSTRUCTOR':
            return redirect('instructor_dashboard')
    return redirect('course-list-public') # Public course list for unauthenticated users

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. Please log in.')
            if user.role == 'INSTRUCTOR':
                return redirect('/instructor/dashboard')
            else:
                return redirect('/student/dashboard')
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                if user.role == 'INSTRUCTOR':
                    return redirect('/instructor/dashboard')
                else:
                    return redirect('/student/dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('/auth/login')

def student_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'STUDENT':
        messages.warning(request, "You do not have permission to view the student dashboard.")
        return redirect('/auth/login') # Or redirect to instructor dashboard if applicable
    
    # Fetch enrolled courses and progress for the student
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    student_progress = []
    for enrollment in enrollments:
        progress, created = Progress.objects.get_or_create(enrollment=enrollment)
        # Calculate progress percentage
        total_lectures = Lecture.objects.filter(course=enrollment.course).count()
        completed_lectures = len(progress.completed_lecture_ids)
        progress_percentage = (completed_lectures / total_lectures) * 100 if total_lectures > 0 else 0
        student_progress.append({
            'enrollment': enrollment,
            'progress': progress,
            'progress_percentage': round(progress_percentage),
            'total_lectures': total_lectures,
            'completed_lectures': completed_lectures
        })

    # Fetch quiz grades information
    from quizzes.models import QuizSubmission, Grade
    quiz_submissions = QuizSubmission.objects.filter(student=request.user).count()
    graded_quizzes = Grade.objects.filter(submission__student=request.user).count()
    average_grade = 0
    if graded_quizzes > 0:
        total_score = sum(grade.score for grade in Grade.objects.filter(submission__student=request.user))
        average_grade = round(total_score / graded_quizzes, 1)

    context = {
        'student_progress': student_progress,
        'enrolled_courses': [p['enrollment'].course for p in student_progress], # List of actual Course objects
        'quiz_submissions': quiz_submissions,
        'graded_quizzes': graded_quizzes,
        'average_grade': average_grade,
    }
    return render(request, 'users/student_dashboard.html', context)

def instructor_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'INSTRUCTOR':
        messages.warning(request, "You do not have permission to view the instructor dashboard.")
        return redirect('/auth/login') # Or redirect to student dashboard if applicable

    # Fetch courses created by the instructor
    instructor_courses = Course.objects.filter(instructor=request.user).order_by('-created_at')

    context = {
        'instructor_courses': instructor_courses,
    }
    return render(request, 'users/instructor_dashboard.html', context)

@login_required
def profile_view(request):
    """View user profile"""
    user = request.user
    received_messages = Message.objects.filter(receiver=user, is_read=False).count()
    
    context = {
        'user': user,
        'unread_messages': received_messages,
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_view')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'users/profile_edit.html', context)

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile_view')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'users/change_password.html', context)

@login_required
def messages_list(request):
    """View all messages"""
    user = request.user
    received_messages = Message.objects.filter(receiver=user)
    sent_messages = Message.objects.filter(sender=user)
    
    # Mark messages as read
    received_messages.update(is_read=True)
    
    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
    }
    return render(request, 'users/messages.html', context)

@login_required
def send_message(request):
    """Send a new message"""
    users = User.objects.exclude(id=request.user.id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = User.objects.get(pk=request.POST.get('receiver'))
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('messages_list')
    else:
        form = MessageForm()
    
    context = {
        'form': form,
        'users': users,
    }
    return render(request, 'users/send_message.html', context)

@login_required
def message_detail(request, message_id):
    """View message detail"""
    message = get_object_or_404(Message, id=message_id)
    
    # Ensure user can only view their own messages
    if message.sender != request.user and message.receiver != request.user:
        messages.error(request, 'You do not have permission to view this message.')
        return redirect('messages_list')
    
    # Mark as read if receiver is viewing
    if message.receiver == request.user:
        message.is_read = True
        message.save()
    
    context = {
        'message': message,
    }
    return render(request, 'users/message_detail.html', context)

@login_required
def get_users_for_messaging(request):
    """Get users for messaging dropdown (AJAX)"""
    users = User.objects.exclude(id=request.user.id).values('id', 'username', 'first_name', 'last_name', 'role')
    return JsonResponse({'users': list(users)})
