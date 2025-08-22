from django.urls import path
from .views import (
    LectureListCreateView,
    LectureDetailView,
    CompleteReadingLectureView,
    SubmitQuizLectureView,
    InstructorCourseLecturesView
)

urlpatterns = [
    path('courses/<int:course_pk>/lectures/', LectureListCreateView.as_view(), name='lecture-list-create'),
    path('courses/<int:course_pk>/lectures/<int:pk>/', LectureDetailView.as_view(), name='lecture-detail'),
    path('lectures/<int:lecture_pk>/complete/', CompleteReadingLectureView.as_view(), name='complete-reading-lecture'),
    path('lectures/<int:lecture_pk>/submit/', SubmitQuizLectureView.as_view(), name='submit-quiz-lecture'),
    path('instructor/courses/<int:course_pk>/lectures/', InstructorCourseLecturesView.as_view(), name='instructor-course-lectures'),
]
