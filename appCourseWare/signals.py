from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import CourseClassroom, Course, Enrollment

@receiver(post_save, sender=CourseClassroom)
def update_course_capacity_on_save(sender, instance, **kwargs):
    course = instance.course
    # Calculate total capacity from all associated classrooms
    total_capacity = course.classrooms.aggregate(total=models.Sum('capacity'))['total']
    course.capacity = total_capacity
    course.save()

@receiver(pre_delete, sender=CourseClassroom)
def update_course_capacity_on_delete(sender, instance, **kwargs):
    course = instance.course
    # Recalculate total capacity after deletion
    total_capacity = course.classrooms.exclude(id=instance.classroom.id).aggregate(total=models.Sum('capacity'))['total']
    course.capacity = total_capacity
    course.save()

@receiver(post_save, sender=Enrollment)
@receiver(pre_delete, sender=Enrollment)
def update_remaining_capacity_on_enrollment_change(sender, instance, **kwargs):
    course = instance.course
    if instance.status == 'enrolled':
        # Enrollment added or updated to 'enrolled'
        course.remaining_capacity = course.capacity - course.enrollment_set.filter(status='enrolled').count()
    else:
        # Enrollment removed or changed from 'enrolled'
        course.remaining_capacity = course.capacity - course.enrollment_set.filter(status='enrolled').count()
    course.save()