import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.decorators import role_required
from jobs.models import Job
from jobseeker.models import JobSeekerProfile
from notifications.services import notify

from .forms import ApplicationForm
from .models import Application


# ---------- Jobseeker ----------

@role_required('jobseeker')
def apply(request, job_pk):
    job = get_object_or_404(Job.objects.select_related('company__user'), pk=job_pk)
    if not job.is_open:
        messages.error(request, "This job is no longer open.")
        return redirect('jobs:list')

    profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

    if Application.objects.filter(job=job, applicant=profile).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect('applications:mine')

    form = ApplicationForm(
        request.POST or None, request.FILES or None, profile=profile,
    )
    if request.method == 'POST' and form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.applicant = profile
        if not application.resume:
            application.resume = profile.resume.name  # use the profile resume
        try:
            with transaction.atomic():
                application.save()
        except IntegrityError:  # double-click / same request from two tabs
            messages.info(request, "You have already applied for this job.")
            return redirect('applications:mine')

        # Company lai notification
        notify(
            job.company.user,
            f"{request.user.username} applied for '{job.title}'.",
            link=reverse('applications:applicants', args=[job.pk]),
            email_subject=f"New application: {job.title}",
        )
        # Jobseeker lai confirmation
        notify(
            request.user,
            f"Your application for '{job.title}' was submitted.",
            link=reverse('applications:mine'),
            email_subject=f"Application submitted: {job.title}",
        )
        messages.success(request, "Application submitted. Good luck!")
        return redirect('applications:mine')

    return render(request, 'applications/apply.html', {
        'form': form, 'job': job, 'profile': profile,
    })


@role_required('jobseeker')
def my_applications(request):
    applications = (
        Application.objects
        .filter(applicant__user=request.user)
        .select_related('job', 'job__company')
    )
    return render(request, 'applications/my_applications.html', {'applications': applications})


@role_required('jobseeker')
@require_POST
def withdraw(request, pk):
    application = get_object_or_404(
        Application.objects.select_related('job__company__user'),
        pk=pk, applicant__user=request.user,
    )
    if application.status != Application.Status.APPLIED:
        messages.error(
            request,
            "This application has already been reviewed by the company and can't be withdrawn.",
        )
        return redirect('applications:mine')

    # Take what we need BEFORE delete(); the row is gone afterwards.
    job = application.job
    company_user = job.company.user
    application.delete()

    # Company lai notification
    notify(
        company_user,
        f"{request.user.username} withdrew their application for '{job.title}'.",
        link=reverse('applications:applicants', args=[job.pk]),
        email_subject=f"Application withdrawn: {job.title}",
    )
    # Jobseeker (withdraw garne) lai confirmation
    notify(
        request.user,
        f"You withdrew your application for '{job.title}'.",
        link=reverse('jobs:detail', args=[job.pk]),
        email_subject=f"You withdrew: {job.title}",
    )
    messages.success(request, "Your application has been withdrawn.")
    return redirect('applications:mine')


# ---------- Company ----------

@role_required('company')
def job_applicants(request, job_pk):
    job = get_object_or_404(Job, pk=job_pk, company__user=request.user)  # ownership check

    counts = dict(
        job.applications.order_by().values_list('status').annotate(n=Count('id'))
    )
    applications = job.applications.select_related('applicant__user')

    current = request.GET.get('status', '')
    if current in Application.Status.values:
        applications = applications.filter(status=current)
    else:
        current = ''

    tabs = [('', 'All', sum(counts.values()))] + [
        (value, label, counts.get(value, 0)) for value, label in Application.Status.choices
    ]
    return render(request, 'applications/job_applicants.html', {
        'job': job,
        'applications': applications,
        'tabs': tabs,
        'current': current,
        'status_choices': Application.Status.choices,
    })


@role_required('company')
@require_POST
def update_status(request, pk):
    application = get_object_or_404(
        Application.objects.select_related('applicant__user', 'job'),
        pk=pk, job__company__user=request.user,
    )
    new_status = request.POST.get('status')
    if new_status in Application.Status.values:
        changed = application.status != new_status
        application.status = new_status
        application.save(update_fields=['status', 'updated_at'])
        if changed:
            notify(
                application.applicant.user,
                f"Your application for '{application.job.title}' is now '{application.get_status_display()}'.",
                link=reverse('applications:mine'),
                email_subject=f"Application update: {application.job.title}",
            )
        messages.success(request, f"Status changed to '{application.get_status_display()}'.")
    else:
        messages.error(request, "Invalid status.")
    return redirect('applications:applicants', job_pk=application.job_id)


# ---------- Resume (with permission check) ----------

@login_required
def resume_download(request, pk):
    application = get_object_or_404(
        Application.objects.select_related('applicant__user', 'job__company'), pk=pk,
    )
    uid = request.user.id
    allowed = (
        application.applicant.user_id == uid
        or application.job.company.user_id == uid
    )
    if not allowed or not application.resume:
        raise Http404

    ext = os.path.splitext(application.resume.name)[1]
    filename = f"{application.applicant.user.username}_resume{ext}"
    return FileResponse(application.resume.open('rb'), as_attachment=True, filename=filename)