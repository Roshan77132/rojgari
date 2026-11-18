from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'requirements', 'skills',
            'location', 'job_type', 'level', 'vacancies',
            'salary_min', 'salary_max', 'deadline', 'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'deadline': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        labels = {'is_active': 'Active (visible to job seekers)'}

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters.")
        return title

    def clean_description(self):
        description = self.cleaned_data['description'].strip()
        if len(description) < 30:
            raise forms.ValidationError(
                "Description must be at least 30 characters so candidates can understand the job."
            )
        return description

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        today = timezone.localdate()
        changed = not self.instance.pk or deadline != self.instance.deadline
        if changed and deadline < today:
            raise forms.ValidationError("Deadline must be today or later.")
        if deadline > today + timedelta(days=365):
            raise forms.ValidationError("Deadline must be within 1 year.")
        return deadline

    def clean_vacancies(self):
        vacancies = self.cleaned_data['vacancies']
        if vacancies < 1:
            raise forms.ValidationError("There must be at least 1 vacancy.")
        return vacancies

    def clean(self):
        cleaned = super().clean()

        # 1) Max salary, min salary bhanda kam hunu hudaina
        low, high = cleaned.get('salary_min'), cleaned.get('salary_max')
        if low and high and low > high:
            self.add_error('salary_max', "Max salary, min salary bhanda kam hunu hudaina.")

        # 2) Internship cannot be Senior level
        if cleaned.get('job_type') == 'internship' and cleaned.get('level') == 'senior':
            self.add_error('level', "Internship cannot be Senior level. Choose Entry or Mid level.")

        return cleaned