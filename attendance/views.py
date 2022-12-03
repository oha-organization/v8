import datetime

from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import School, Bus, Student, AbsentStudent, Attendance, Grade


def home(request):
    return render(request, "attendance/home.html")


def attendance_select(request):
    bus_list = Bus.objects.filter(school=request.user.school)
    context = {"bus_list": bus_list, "today": datetime.date.today()}
    return render(request, "attendance/attendance_select.html", context)


def attendance_get_or_create(request):
    bus = get_object_or_404(Bus.objects.all(), id=request.POST.get("bus"))
    check_date = request.POST.get("check_date")
    if request.POST["direction"] in ["COMING", "LEAVING"]:
        direction = request.POST["direction"]
    else:
        raise ValueError("Don't tamper post direction data!")

    student_list = Student.objects.filter(bus=bus)

    # Get or create new attendance
    attendance, created = Attendance.objects.get_or_create(
        school=request.user.school,
        bus=bus,
        direction=direction,
        check_date=check_date,
        defaults={"teacher": request.user},
    )

    request.session["attendance_id"] = attendance.id
    request.session["bus_id"] = bus.id

    # If attendance is already exist get unattended student list
    student_already_absent_list = []
    if not created:
        student_already_absent_list = Student.objects.filter(
            absent_student__attendance=attendance
        )

    context = {
        "student_list": student_list,
        "student_already_absent_list": student_already_absent_list,
        "attendance": attendance,
    }
    return render(request, "attendance/attendance_get_or_create.html", context)


def attendance_save(request):
    """Save attendance logic"""
    if request.method == "POST":
        # For security reason check absent_students are in bus student_list
        student_list = Student.objects.filter(bus=request.session["bus_id"])
        student_list = [str(student.id) for student in student_list]
        student_absent_list = request.POST.getlist("student_absent_list")

        check_all_absent_student_in_student_list = all(
            item in student_list for item in student_absent_list
        )
        if not check_all_absent_student_in_student_list:
            raise Http404("TAMPERED STUDENT DATA...")

        # Delete all attendance for attendance
        attendance = Attendance.objects.get(id=request.session["attendance_id"])
        AbsentStudent.objects.filter(attendance=attendance).delete()

        # Add absent students to Attendance
        for student in student_absent_list:
            AbsentStudent.objects.create(attendance=attendance, student_id=student)

        # Touch Attendance Model for update to signed_at field
        attendance.is_signed = True
        attendance.teacher = request.user
        attendance.save()

        # return redirect("attendance:attendance-detail", attendance.id)
        return redirect("attendance:attendance-save-done")


def attendance_save_done(request):
    attendance = get_object_or_404(
        Attendance.objects.all(), id=request.session.get("attendance_id")
    )
    del request.session["attendance_id"]
    context = {"attendance": attendance}
    return render(request, "attendance/attendance_save_done.html", context)


def attendance_detail(request, attendance_id):
    attendance = get_object_or_404(Attendance.objects.all(), id=attendance_id)
    context = {"attendance": attendance}
    return render(request, "attendance/attendance_detail.html", context)


def attendance_list_view(request):
    attendance_list = Attendance.objects.filter(school=request.user.school)
    context = {
        "attendance_list": attendance_list,
    }
    return render(request, "attendance/attendance_list.html", context)


def grade_list_view(request):
    grade_list = Grade.objects.filter(school=request.user.school)
    context = {
        "grade_list": grade_list,
    }
    return render(request, "attendance/grade_list.html", context)


def grade_add(request):
    if request.method == "POST":
        school = request.user.school
        level = request.POST["level"]
        branch = request.POST["branch"]

        grade = Grade(school=school, level=level, branch=branch)
        try:
            grade.save()
        except Exception as e:
            print("Error is: ", e)
            raise Http404("The Grade has already exist.")

        return redirect("attendance:home")

    return render(request, "attendance/grade_add.html")


def grade_change(request, grade_id):
    grade = get_object_or_404(
        Grade.objects.filter(school=request.user.school), id=grade_id
    )

    if request.method == "POST":
        level = request.POST["level"]
        branch = request.POST["branch"]

        # If nothing change doesn't touch database
        if not (grade.level == level and grade.branch == branch):
            grade.level = level
            grade.branch = branch
            try:
                grade.save()
            except Exception as e:
                raise Http404("Update error.")

        return redirect("attendance:grade-list")

    context = {"grade": grade}
    return render(request, "attendance/grade_change.html", context)


def driver_list_view(request):
    driver_list = get_user_model().objects.filter(
        school=request.user.school, role="DRIVER"
    )
    context = {
        "driver_list": driver_list,
    }
    return render(request, "attendance/driver_list.html", context)


def teacher_list_view(request):
    teacher_list = get_user_model().objects.filter(
        school=request.user.school, role="TEACHER"
    )
    context = {
        "teacher_list": teacher_list,
    }
    return render(request, "attendance/teacher_list.html", context)


def teacher_add(request):
    if request.method == "POST":
        school = request.user.school
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            teacher = get_user_model().objects.create_user(
                school=school,
                role="TEACHER",
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )
        except Exception as e:
            raise Http404("User creation error.")

        return redirect("attendance:teacher-list")

    return render(request, "attendance/teacher_add.html")


def teacher_change(request, teacher_id):
    teacher = get_object_or_404(
        get_user_model().objects.filter(school=request.user.school), id=teacher_id
    )

    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]

        teacher.username = username
        teacher.first_name = first_name
        teacher.last_name = last_name
        teacher.email = email

        try:
            teacher.save()
        except Exception as e:
            raise Http404("Teacher update error.")

        return redirect("attendance:teacher-list")

    context = {
        "teacher": teacher,
    }
    return render(request, "attendance/teacher_change.html", context)


def teacher_change_password(request, teacher_id):
    teacher = get_object_or_404(
        get_user_model().objects.filter(school=request.user.school), id=teacher_id
    )
    context = {
        "teacher": teacher,
    }

    if request.method == "POST":
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 == password2:
            teacher.set_password(password1)
            try:
                teacher.save()
            except Exception as e:
                raise Http404("Teacher password update error.")

            return redirect("attendance:teacher-list")

        context["error_message"] = "Password does not match!"

    return render(request, "attendance/teacher_change_password.html", context)
