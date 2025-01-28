# Generated by Django 5.0.6 on 2025-01-28 22:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appCourseWare', '0002_alter_customuser_user_level'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classroom',
            name='capacity',
        ),
        migrations.AddField(
            model_name='course',
            name='capacity',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='course',
            name='remaining_capacity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='major',
            name='major_name',
            field=models.CharField(max_length=30),
        ),
        migrations.CreateModel(
            name='StudentCourse',
            fields=[
                ('enrollment_id', models.AutoField(primary_key=True, serialize=False)),
                ('enrollment_date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(choices=[('enrolled', 'در حال گذراندن'), ('dropped', 'افتاده'), ('withdrawn', 'حذف اضطراری'), ('completed', 'گذرانده')], max_length=20)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appCourseWare.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appCourseWare.student')),
            ],
            options={
                'unique_together': {('student', 'course')},
            },
        ),
        migrations.DeleteModel(
            name='Enrollment',
        ),
    ]
