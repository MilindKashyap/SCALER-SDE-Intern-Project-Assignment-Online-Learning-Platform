from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course
from lectures.models import Lecture, ReadingLecture, QuizLecture
from quizzes.models import Question
from enrollments.models import Enrollment
from progress.models import Progress

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample data for demonstration.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding database...'))

        # Clear existing data
        User.objects.filter(is_superuser=False).delete()
        Course.objects.all().delete()
        Lecture.objects.all().delete()
        ReadingLecture.objects.all().delete()
        QuizLecture.objects.all().delete()
        Question.objects.all().delete()
        Enrollment.objects.all().delete()
        Progress.objects.all().delete()

        # 1. Create Users
        instructor = User.objects.create_user(
            username='instructor1',
            email='instructor@example.com',
            password='testpassword',
            role='INSTRUCTOR'
        )
        student1 = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='testpassword',
            role='STUDENT'
        )
        student2 = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='testpassword',
            role='STUDENT'
        )
        self.stdout.write(self.style.SUCCESS('Created 1 instructor and 2 students.'))

        # 2. Create Courses
        course1 = Course.objects.create(
            title='Introduction to Python',
            description='A beginner-friendly introduction to Python programming.',
            instructor=instructor,
            is_published=True
        )
        course2 = Course.objects.create(
            title='Web Development with Django',
            description='Learn to build web applications using Django and Python.',
            instructor=instructor,
            is_published=True
        )
        course3 = Course.objects.create(
            title='Advanced Data Science',
            description='Deep dive into machine learning and data analysis techniques.',
            instructor=instructor,
            is_published=False # Unpublished course
        )
        self.stdout.write(self.style.SUCCESS('Created 3 sample courses.'))

        # 3. Create Lectures for Course 1 (Python)
        lecture1_1 = Lecture.objects.create(course=course1, title='Welcome to Python', type='READING', order_index=1)
        ReadingLecture.objects.create(lecture=lecture1_1, content_text='This is the first reading lecture content.')

        lecture1_2 = Lecture.objects.create(course=course1, title='Python Basics Quiz', type='QUIZ', order_index=2)
        quiz1_2 = QuizLecture.objects.create(lecture=lecture1_2)
        Question.objects.create(quiz=quiz1_2, text='What is Python?', options=['A snake', 'A programming language', 'A type of food'], correct_index=1)
        Question.objects.create(quiz=quiz1_2, text='Which of these is a Python data type?', options=['Array', 'List', 'Hash'], correct_index=1)

        lecture1_3 = Lecture.objects.create(course=course1, title='Control Flow', type='READING', order_index=3)
        ReadingLecture.objects.create(lecture=lecture1_3, content_text='Understanding if/else and loops.')

        # 4. Create Lectures for Course 2 (Django)
        lecture2_1 = Lecture.objects.create(course=course2, title='Introduction to Django', type='READING', order_index=1)
        ReadingLecture.objects.create(lecture=lecture2_1, content_text='Overview of Django framework.')

        lecture2_2 = Lecture.objects.create(course=course2, title='Django Models Quiz', type='QUIZ', order_index=2)
        quiz2_2 = QuizLecture.objects.create(lecture=lecture2_2)
        Question.objects.create(quiz=quiz2_2, text='What does ORM stand for?', options=['Object-Relational Mapping', 'Ordered-Replicated Modules', 'Optimal-Resource Management'], correct_index=0)
        
        self.stdout.write(self.style.SUCCESS('Created sample lectures and quizzes.'))

        # 5. Enroll Students
        enrollment1 = Enrollment.objects.create(student=student1, course=course1)
        enrollment2 = Enrollment.objects.create(student=student2, course=course1)
        enrollment3 = Enrollment.objects.create(student=student1, course=course2)
        self.stdout.write(self.style.SUCCESS('Enrolled students in courses.'))

        # 6. Create some progress for student1 in course1
        progress1, created = Progress.objects.get_or_create(enrollment=enrollment1)
        progress1.completed_lecture_ids = [lecture1_1.id]
        progress1.scores[str(lecture1_2.id)] = 80 # Assume student1 got 80% on quiz1_2
        progress1.save()
        self.stdout.write(self.style.SUCCESS('Created sample progress data.'))

        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
