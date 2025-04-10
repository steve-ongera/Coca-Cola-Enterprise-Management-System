from django import forms
from .models import Leave, Timesheet

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['week_starting', 'hours_worked', 'tasks_completed']
        widgets = {
            'week_starting': forms.DateInput(attrs={'type': 'date'}),
        }