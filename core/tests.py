import shutil
import tempfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from applications.models import Application
from companies.models import CompanyProfile
from jobs.models import Job
from jobseeker.models import JobSeekerProfile
from notifications.models import Notification

User = get_user_model()
TEMP_MEDIA = tempfile.mkdtemp()
BACKEND = 'django.contrib.auth.backends.ModelBackend'


def make_user(username, role, email=''):
    return User.objects.create_user(
        username=username, password='pass12345', role=role,
        email=email or f'{username}@example.com',
    )


def make_company(username, verified=True):
    user = make_user(username, 'company')
    # a profile may already be created automatically when the user is created
    profile, _ = CompanyProfile.objects.get_or_create(
        user=user, defaults={'company_name': username},
    )
    profile.company_name = username
    profile.is_verified = verified
    profile.save()
    return user, profile


def make_jobseeker(username):
    user = make_user(username, 'jobseeker')
    profile, _ = JobSeekerProfile.objects.get_or_create(user=user)
    profile.resume = SimpleUploadedFile('cv.pdf', b'%PDF-1.4 test resume')
    profile.save()
    return user, profile


def make_job(company_profile):
    return Job.objects.create(
        company=company_profile, title='Django Dev', description='desc',
        location='Kathmandu', job_type='full_time',
        deadline=timezone.localdate() + timedelta(days=30),
    )


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ProtectedFilesTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.seeker_user, self.seeker = make_jobseeker('seeker')
        self.other_user, _ = make_jobseeker('other')
        self.company_user, self.company = make_company('acme')
        self.stranger_user, _ = make_company('stranger')

    def test_anonymous_is_sent_to_login(self):
        response = self.client.get(reverse('core:profile_resume', args=[self.seeker.pk]))
        self.assertEqual(response.status_code, 302)

    def test_owner_can_download_own_resume(self):
        self.client.force_login(self.seeker_user, backend=BACKEND)
        response = self.client.get(reverse('core:profile_resume', args=[self.seeker.pk]))
        self.assertEqual(response.status_code, 200)

    def test_other_jobseeker_cannot_download_resume(self):
        self.client.force_login(self.other_user, backend=BACKEND)
        response = self.client.get(reverse('core:profile_resume', args=[self.seeker.pk]))
        self.assertEqual(response.status_code, 404)

    def test_company_without_application_cannot_download_resume(self):
        self.client.force_login(self.company_user, backend=BACKEND)
        response = self.client.get(reverse('core:profile_resume', args=[self.seeker.pk]))
        self.assertEqual(response.status_code, 404)

    def test_company_with_application_can_download_resume(self):
        job = make_job(self.company)
        Application.objects.create(job=job, applicant=self.seeker, resume='x.pdf')
        self.client.force_login(self.company_user, backend=BACKEND)
        response = self.client.get(reverse('core:profile_resume', args=[self.seeker.pk]))
        self.assertEqual(response.status_code, 200)

    def test_company_document_is_private_to_owner(self):
        self.company.registration_document = SimpleUploadedFile('reg.pdf', b'%PDF-1.4 doc')
        self.company.save()
        url = reverse('core:company_document', args=[self.company.pk])

        self.client.force_login(self.stranger_user, backend=BACKEND)
        self.assertEqual(self.client.get(url).status_code, 404)

        self.client.force_login(self.company_user, backend=BACKEND)
        self.assertEqual(self.client.get(url).status_code, 200)


class JobPostingTests(TestCase):
    def test_unverified_company_cannot_post_job(self):
        user, _ = make_company('newco', verified=False)
        self.client.force_login(user, backend=BACKEND)
        response = self.client.get(reverse('jobs:create'))
        self.assertRedirects(response, reverse('dashboard:company'))

    def test_verified_company_can_open_job_form(self):
        user, _ = make_company('verifiedco', verified=True)
        self.client.force_login(user, backend=BACKEND)
        response = self.client.get(reverse('jobs:create'))
        self.assertEqual(response.status_code, 200)

    def test_company_cannot_edit_another_companys_job(self):
        _, owner_profile = make_company('owner')
        job = make_job(owner_profile)
        intruder, _ = make_company('intruder')
        self.client.force_login(intruder, backend=BACKEND)
        response = self.client.get(reverse('jobs:edit', args=[job.pk]))
        self.assertEqual(response.status_code, 404)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class NotificationTests(TestCase):
    def setUp(self):
        self.seeker_user, self.seeker = make_jobseeker('seeker')
        self.company_user, self.company = make_company('acme')
        self.job = make_job(self.company)

    def test_apply_notifies_company(self):
        # Emails sent while creating the test users are not part of this test
        mail.outbox.clear()

        self.client.force_login(self.seeker_user, backend=BACKEND)
        response = self.client.post(
            reverse('applications:apply', args=[self.job.pk]),
            {'cover_letter': 'Hello'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Application.objects.filter(job=self.job, applicant=self.seeker).exists())
        self.assertEqual(Notification.objects.filter(user=self.company_user).count(), 1)

        # The company must receive exactly one email (the failure message lists the subjects)
        company_mails = [m for m in mail.outbox if self.company_user.email in m.to]
        self.assertEqual(len(company_mails), 1, [m.subject for m in mail.outbox])

    def test_status_change_notifies_jobseeker_once(self):
        application = Application.objects.create(
            job=self.job, applicant=self.seeker, resume='x.pdf',
        )
        self.client.force_login(self.company_user, backend=BACKEND)
        url = reverse('applications:status', args=[application.pk])

        self.client.post(url, {'status': 'shortlisted'})
        self.assertEqual(Notification.objects.filter(user=self.seeker_user).count(), 1)

        # same status again must not create a duplicate
        self.client.post(url, {'status': 'shortlisted'})
        self.assertEqual(Notification.objects.filter(user=self.seeker_user).count(), 1)

    def test_user_cannot_read_another_users_notification(self):
        note = Notification.objects.create(user=self.company_user, message='private')
        self.client.force_login(self.seeker_user, backend=BACKEND)
        response = self.client.post(reverse('notifications:read', args=[note.pk]))
        self.assertEqual(response.status_code, 404)