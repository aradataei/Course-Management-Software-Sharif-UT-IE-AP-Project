# Generated by Django 5.0.6 on 2025-01-29 18:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appCourseWare', '0006_alter_student_major_alter_studentcourse_status'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Instructor',
            new_name='Professor',
        ),
        migrations.RenameField(
            model_name='course',
            old_name='instructor',
            new_name='professor',
        ),
    ]
