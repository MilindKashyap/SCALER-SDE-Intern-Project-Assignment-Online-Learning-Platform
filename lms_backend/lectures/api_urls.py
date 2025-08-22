from django.urls import path
from lectures import views

urlpatterns = [
    path('<int:course_pk>/<int:pk>/', views.LectureAPIView.as_view(), name='lecture-detail'),
]
