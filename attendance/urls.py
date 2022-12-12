from django.urls import path
from . import views


app_name = "attendance"
urlpatterns = [
    path("", views.home, name="home"),
    path("select/", views.attendance_select, name="attendance-select"),
    path("display/", views.attendance_display, name="attendance-display"),
    path("save/", views.attendance_save, name="attendance-save"),
    path("save-done/", views.attendance_save_done, name="attendance-save-done"),
    path(
        "attendance/<int:attendance_id>/",
        views.attendance_detail,
        name="attendance-detail",
    ),
    path("attendance/", views.attendance_list_view, name="attendance-list"),
    path("grade/", views.grade_list_view, name="grade-list"),
    path("grade/add/", views.grade_add, name="grade-add"),
    path("grade/<int:grade_id>/change/", views.grade_change, name="grade-change"),
    path("teacher/", views.teacher_list_view, name="teacher-list"),
    path("teacher/add/", views.teacher_add, name="teacher-add"),
    path("driver/", views.driver_list_view, name="driver-list"),
    path("driver/add/", views.driver_add, name="driver-add"),
    path(
        "teacher/<int:teacher_id>/change/", views.teacher_change, name="teacher-change"
    ),
    path(
        "teacher/<int:teacher_id>/password/",
        views.teacher_change_password,
        name="teacher-change-password",
    ),
    path("bus/", views.bus_list_view, name="bus-list"),
    path(
        "bus/<int:bus_id>/busmember/", views.busmember_list_view, name="busmember-list"
    ),
    path(
        "bus/<int:bus_id>/busmember/change/",
        views.busmember_change,
        name="busmember-change",
    ),
    path(
        "bus/<int:bus_id>/grade/<int:grade_id>/",
        views.busmember_add,
        name="busmember-add-by-grade",
    ),
]
