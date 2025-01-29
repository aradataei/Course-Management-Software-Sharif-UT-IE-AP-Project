# Generated by Django 5.1.5 on 2025-01-29 06:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appCourseWare', '0004_alter_student_admission_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='admission_year',
            field=models.PositiveIntegerField(choices=[('1403', 1403), ('1402', 1402), ('1401', 1401), ('1400', 1400), ('1399', 1399), ('1398', 1388)], default=1403),
        ),
        migrations.AlterField(
            model_name='student',
            name='first_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='student',
            name='gpa',
            field=models.DecimalField(decimal_places=2, max_digits=4, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(20.0)]),
        ),
        migrations.AlterField(
            model_name='student',
            name='last_name',
            field=models.CharField(max_length=100),
        ),
    ]
