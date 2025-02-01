from .forms import CustomUserCreationForm, StudentProfileForm
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.contrib import messages
from django.http import Http404

# فرض بر این است که مدل‌های زیر از adminViews import شده‌اند.
from .models import (
    Course, Student, StudentCourse, Professor,
    Department, Classroom, CustomUser, UserLevel,
    Major, Prerequisite, CoRequisite
)

User = get_user_model()


####################################
#           ADMIN TESTS            #
####################################


class AdminViewsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # ایجاد کاربر admin برای تست
        cls.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        # ایجاد برخی نمونه‌های مدل‌ها برای تست:
        cls.test_student = Student.objects.create(
            student_id='stu123',
            name='Test Student'
        )
        cls.test_course = Course.objects.create(
            course_id='c101',
            name='Test Course'
        )
        cls.test_student_course = StudentCourse.objects.create(
            student_course_id='sc101',
            student=cls.test_student,
            course=cls.test_course
        )
        cls.test_professor = Professor.objects.create(
            professor_id='prof1',
            name='Test Professor'
        )
        cls.test_department = Department.objects.create(
            department_id='dept1',
            name='Test Department'
        )
        cls.test_classroom = Classroom.objects.create(
            classroom_id='room1',
            name='Test Classroom'
        )
        cls.test_major = Major.objects.create(
            major_id='major1',
            name='Test Major'
        )
        cls.test_prerequisite = Prerequisite.objects.create(
            prerequisite_id='pre1',
            course=cls.test_course
        )
        cls.test_corequisite = CoRequisite.objects.create(
            corequisite_id='core1',
            course=cls.test_course
        )

    def setUp(self):
        self.client = Client()
        # ورود به سیستم با کاربر admin
        self.client.login(username='admin', password='adminpass')

    # ------------------- تست مدیریت کاربران -------------------
    def test_manage_users_view_get(self):
        url = reverse('manage_users_view')  # نام url باید مطابق تعریف شما باشد!
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.context)

    def test_make_admin_post(self):
        # قبل از تست، ایجاد یک کاربر عادی
        normal_user = User.objects.create_user(
            username='user1',
            password='userpass',
            is_staff=False
        )
        url = reverse('manage_users_view')
        post_data = {
            'user_id': normal_user.student_id if hasattr(normal_user, 'student_id') else normal_user.pk,
            'action': 'make_admin'
        }
        response = self.client.post(url, post_data, follow=True)
        normal_user.refresh_from_db()
        self.assertTrue(normal_user.is_staff)

    # ------------------- تست مدیریت دانش‌آموزان -------------------
    def test_manage_students_view_get(self):
        url = reverse('manage_students_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('students', response.context)

    def test_delete_student(self):
        url = reverse('manage_students_view')
        post_data = {
            'student_id': self.test_student.student_id,
            'action': 'delete'
        }
        response = self.client.post(url, post_data, follow=True)
        # اطمینان از حذف دانش‌آموز
        with self.assertRaises(Student.DoesNotExist):
            Student.objects.get(pk=self.test_student.pk)

    # ------------------- تست مدیریت دروس -------------------
    def test_manage_courses_view_get(self):
        url = reverse('manage_courses_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('courses', response.context)

    def test_delete_course(self):
        url = reverse('manage_courses_view')
        post_data = {
            'course_id': self.test_course.course_id,
            'action': 'delete'
        }
        response = self.client.post(url, post_data, follow=True)
        with self.assertRaises(Course.DoesNotExist):
            Course.objects.get(pk=self.test_course.pk)

    # ------------------- تست مدیریت ثبت‌نام دانش‌آموزان در دروس -------------------
    def test_manage_student_course_view_get(self):
        url = reverse('manage_student_course_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('student_courses', response.context)

    def test_delete_student_course(self):
        url = reverse('manage_student_course_view')
        post_data = {
            'student_course_id': self.test_student_course.student_course_id,
            'action': 'delete'
        }
        response = self.client.post(url, post_data, follow=True)
        with self.assertRaises(StudentCourse.DoesNotExist):
            StudentCourse.objects.get(pk=self.test_student_course.pk)

    # ------------------- تست مدیریت استادان -------------------
    def test_manage_professors_view_get(self):
        url = reverse('manage_professors_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('professors', response.context)

    def test_delete_professor(self):
        url = reverse('manage_professors_view')
        post_data = {
            'professor_id': self.test_professor.professor_id,
            'action': 'delete'
        }
        response = self.client.post(url, post_data, follow=True)
        with self.assertRaises(Professor.DoesNotExist):
            Professor.objects.get(pk=self.test_professor.pk)

    # ------------------- تست مدیریت واحدهای دانشگاهی -------------------
    def test_manage_departments_view_get(self):
        url = reverse('manage_departments_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('departments', response.context)

    def test_delete_department(self):
        url = reverse('manage_departments_view')
        post_data = {
            'department_id': self.test_department.department_id,
            'action': 'delete'
        }
        response = self.client.post(url, post_data, follow=True)
        with self.assertRaises(Department.DoesNotExist):
            Department.objects.get(pk=self.test_department.pk)

    # ------------------- تست مدیریت کلاس‌ها -------------------
    def test_manage_classrooms_view_get(self):
        url = reverse('manage_classrooms_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('classrooms', response.context)

    def test_delete_classroom(self):
        url = reverse('manage_classrooms_view')
        post_data = {
            'classroom_id': self.test_classroom.classroom_id,
            'action': 'delete'
        }
        response = self.client.post(url, post_data, follow=True)
        with self.assertRaises(Classroom.DoesNotExist):
            Classroom.objects.get(pk=self.test_classroom.pk)

    # ------------------- تست مدیریت رشته‌ها -------------------
    def test_manage_majors_view_get(self):
        url = reverse('manage_majors_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('majors', response.context)

    def test_delete_major(self):
        url = reverse('manage_majors_view')
        post_data = {
            'major_id': self.test_major.major_id,
            'action': 'delete'
        }
        response = self.client.post(url, post_data, follow=True)
        with self.assertRaises(Major.DoesNotExist):
            Major.objects.get(pk=self.test_major.pk)

    # ------------------- تست مدیریت پیش‌نیازها -------------------
    def test_manage_prerequisites_view_get(self):
        url = reverse('manage_prerequisites_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('prerequisites', response.context)

    def test_delete_prerequisite(self):
        url = reverse('manage_prerequisites_view')
        post_data = {
            'prerequisite_id': self.test_prerequisite.prerequisite_id,
            'action': 'delete'
        }
        response = self.client.post(url, post_data, follow=True)
        with self.assertRaises(Prerequisite.DoesNotExist):
            Prerequisite.objects.get(pk=self.test_prerequisite.pk)

    # ------------------- تست مدیریت هم‌نیازها -------------------
    def test_manage_corequisites_view_get(self):
        url = reverse('manage_corequisites_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('corequisites', response.context)

    def test_delete_corequisite(self):
        url = reverse('manage_corequisites_view')
        post_data = {
            'corequisite_id': self.test_corequisite.corequisite_id,
            'action': 'delete'
        }
        response = self.client.post(url, post_data, follow=True)
        with self.assertRaises(CoRequisite.DoesNotExist):
            CoRequisite.objects.get(pk=self.test_corequisite.pk)

    # ------------------- تست‌های امنیتی -------------------
    def test_non_staff_access(self):
        # خروج از حساب کاربری admin و ایجاد کاربر غیر ادمین
        self.client.logout()
        non_staff_user = User.objects.create_user(
            username='nonadmin',
            password='nonadminpass',
            is_staff=False
        )
        self.client.login(username='nonadmin', password='nonadminpass')
        url = reverse('manage_courses_view')
        response = self.client.get(url)
        # درصورتی که کاربر غیر ادمین باشد معمولا باید ریدایرکت شود یا خطای دسترسی دریافت کند
        self.assertNotEqual(response.status_code, 200)

    # ------------------- تست خطا هنگام ارسال آیتم نادرست -------------------
    def test_delete_invalid_student(self):
        url = reverse('manage_students_view')
        post_data = {
            'student_id': 'invalid_id',
            'action': 'delete'
        }
        response = self.client.post(url, post_data)
        # استفاده از get_object_or_404 باعث برگرداندن 404 می‌شود.
        self.assertEqual(response.status_code, 404)

####################################
#           MODEL TESTS            #
####################################

class UserModelTests(TestCase):
    def test_create_user_with_valid_student_id(self):
        """
        Test that a user with a valid student ID can be created.
        """
        user = User.objects.create_user(student_id='123456789', password='testpass')
        self.assertEqual(user.student_id, '123456789')

    def test_invalid_student_id(self):
        """
        Test that an invalid student ID triggers an error.
        Adjust the expected exception to match how you handle invalid IDs.
        """
        with self.assertRaises(ValueError):
            User.objects.create_user(student_id='12345678', password='testpass')


class StudentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(student_id='123456789', password='testpass')
        # Creating a Major instance for tests; ensure that Major is imported correctly.
        self.major = Major.objects.create(major_name='Computer Science')

    def test_create_student_with_valid_data(self):
        """
        Test that a Student instance is created properly with expected attributes.
        """
        student = Student.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            national_id='1234567890',
            phone_number='+9812345678901',
            gpa=15.5,
            email='john@example.com',
            major=self.major
        )
        self.assertEqual(student.first_name, 'John')
        self.assertEqual(student.major, self.major)

    def test_student_gpa_sets_max_units(self):
        """
        This test checks that the student's GPA correctly results in the calculation 
        of 'max_units'. Adjust the expected value based on your business logic.
        """
        student = Student.objects.create(
            user=self.user,
            first_name='Jane',
            last_name='Doe',
            national_id='0987654321',
            phone_number='+989876543210',
            email='jane@example.com',
            gpa=18,
            major=self.major
        )
        # Here the assumption is that a GPA of 18 gives max_units of 24.
        self.assertEqual(student.max_units, 24)


class CourseModelTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(department_name='Mathematics')
        self.professor = Professor.objects.create(
            first_name='Prof', 
            last_name='Test', 
            email='prof@test.com', 
            department=self.department
        )

    def test_create_course(self):
        """
        Test the creation of a Course instance along with its relationships.
        """
        course = Course.objects.create(
            course_name='Calculus',
            capacity=30,
            department=self.department,
            professor=self.professor
            # Include any other required fields based on your model definition.
        )
        # The initial remaining_capacity should be the same as capacity if not altered.
        self.assertEqual(course.remaining_capacity, 30)


#####################################
#           VIEWS TESTS             #
#####################################

class ViewsTests(TestCase):
    def test_register_view(self):
        """
        Test that the registration view creates a user and redirects upon successful registration.
        """
        register_url = reverse('register')  # Ensure this URL name matches your URL configuration.
        response = self.client.post(register_url, {
            'student_id': '123456789',
            'password1': 'testpass',
            'password2': 'testpass',
        })
        # Check for HTTP 302 redirect after registration.
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(student_id='123456789').exists())

    def test_create_student_profile_view(self):
        """
        Test the student profile creation view, ensuring logged in user can create their profile.
        """
        # Create a user and log in.
        user = User.objects.create_user(student_id='123456789', password='testpass')
        self.client.login(username='123456789', password='testpass')

        # Create a Major instance for the profile
        major_instance = Major.objects.create(major_name='CS')

        create_profile_url = reverse('create_student_profile')  # Adjust URL name if necessary.
        response = self.client.post(create_profile_url, {
            'first_name': 'John',
            'last_name': 'Doe',
            'national_id': '1234567890',
            'email': 'john@example.com',
            'gpa': 16,
            'major': major_instance.major_id
        })
        # Expect a redirect to another page after a successful POST.
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Student.objects.filter(user=user).exists())

    def test_admin_operations(self):
        """
        Test admin operations such as accessing the student list view.
        """
        # Create an admin user and login.
        admin_user = User.objects.create_user(
            student_id='123456789', 
            password='adminpass', 
            is_staff=True
        )
        self.client.login(username='admin123456789', password='adminpass')
        
        student_list_url = reverse('student_list_view')  # Ensure the URL name is correct.
        response = self.client.get(student_list_url)
        self.assertEqual(response.status_code, 200)
        # Additional tests can include editing and deletion functionalities by asserting database changes.


#####################################
#           FORMS TESTS             #
#####################################

class FormTests(TestCase):
    def test_valid_user_creation_form(self):
        """
        Test that the CustomUserCreationForm is valid with proper data.
        """
        form = CustomUserCreationForm(data={
            'student_id': '123456789',
            'password1': 'testpass',
            'password2': 'testpass',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_user_creation_form(self):
        """
        Test that the form is invalid when using an invalid student_id.
        """
        form = CustomUserCreationForm(data={
            'student_id': '12345678',  # Assuming this is invalid
            'password1': 'testpass',
            'password2': 'testpass',
        })
        self.assertFalse(form.is_valid())

    def test_student_profile_form(self):
        """
        Test that the StudentProfileForm validates data correctly.
        """
        major_instance = Major.objects.create(major_name='CS')
        form = StudentProfileForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'national_id': '1234567890',
            'email': 'john@example.com',
            'gpa': 16,
            'major': major_instance.major_id
        })
        self.assertTrue(form.is_valid())
