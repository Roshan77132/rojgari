from datetime import date

from django import forms
from .models import CompanyProfile

INPUT = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
    "focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
)


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'logo', 'company_name', 'tagline', 'description',
            'industry', 'company_size', 'established_year',
            'location', 'website', 'contact_email', 'contact_phone',
            'pan_number', 'registration_document',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'logo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'registration_document': forms.ClearableFileInput(
                attrs={'accept': '.pdf,.doc,.docx'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('logo', 'registration_document'):
                field.widget.attrs['class'] = INPUT

    def clean_established_year(self):
        year = self.cleaned_data['established_year']
        if year is not None and not (1900 <= year <= date.today().year):
            raise forms.ValidationError(
                f"Year must be between 1900 and {date.today().year}."
            )
        return year