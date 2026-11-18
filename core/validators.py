from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, FileExtensionValidator

phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message='Valid phone number halnus (7-15 digit).',
)

resume_validator = FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])
image_validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])

pan_validator = RegexValidator(
    regex=r'^\d{9}$',
    message='PAN number must be 9 digits.',
)
def validate_file_size(file):
    if file.size > 5 * 1024 * 1024:
        raise ValidationError('File must be smaller than 5MB.')