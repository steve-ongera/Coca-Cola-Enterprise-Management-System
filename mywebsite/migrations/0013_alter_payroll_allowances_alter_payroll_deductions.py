# Generated by Django 5.1.2 on 2025-04-11 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mywebsite', '0012_alter_payroll_allowances_alter_payroll_basic_salary_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payroll',
            name='allowances',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='deductions',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
