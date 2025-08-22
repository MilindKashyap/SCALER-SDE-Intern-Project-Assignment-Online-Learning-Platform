from django.urls import path
from . import views

urlpatterns = [
    path('<int:lecture_pk>/', views.lecture_detail_view, name='lecture_detail'), # Renamed for consistency
    path('<int:lecture_pk>/mark-done/', views.mark_lecture_as_done, name='mark_lecture_as_done'), # New URL for marking lecture as done
    path('courses/<int:course_pk>/lectures/<int:lecture_pk>/edit/', views.lecture_edit_view, name='lecture_edit'),
]
