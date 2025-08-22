from django.urls import path
from courses import views

urlpatterns = [
    path('<int:pk>/manage/', views.CourseDetailUpdateDeleteAPIView.as_view(), name='course-detail-update-delete'),
]
