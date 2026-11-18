from django import forms
from .models import JobSeekerProfile

INPUT = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
    "focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
)


class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = [
            'photo', 'headline', 'bio', 'phone', 'location',
            'education_level', 'skills', 'experience_years',
            'expected_salary', 'preferred_job_type', 'resume',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'resume': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('photo', 'resume'):
                field.widget.attrs['class'] = INPUT

    def clean_experience_years(self):
        years = self.cleaned_data['experience_years']
        if years is not None and years > 50:
            raise forms.ValidationError("Experience 50 years bhanda badhi hunu hudaina.")
        return years