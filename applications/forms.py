from django import forms

from .models import Application

INPUT = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
    "focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
)


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 6, 'class': INPUT}),
            'resume': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }
        labels = {'cover_letter': 'Cover letter (optional)', 'resume': 'Resume'}

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = profile
        self.fields['resume'].required = False
        if profile and profile.resume:
            self.fields['resume'].help_text = (
                "If left empty, your profile resume will be used."
            )

    def clean(self):
        cleaned = super().clean()
        has_upload = bool(cleaned.get('resume'))
        has_profile_resume = bool(self.profile and self.profile.resume)
        if not has_upload and not has_profile_resume:
            self.add_error('resume', "Please upload a resume (PDF/DOC) or add one to your profile.")
        return cleaned