from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from applications.models import Application
from companies.models import CompanyProfile
from core.decorators import role_required

from .forms import JobForm
from .models import Job, SavedJob


def _get_company(request):
    profile, _ = CompanyProfile.objects.get_or_create(
        user=request.user,
        defaults={'company_name': request.user.username},
    )
    return profile


# ---------- Public (visible to everyone) ----------

PER_PAGE = 10

SORT_OPTIONS = {
    'latest': ('Latest', ['-created_at', '-pk']),
    'deadline': ('Deadline (soonest)', ['deadline', '-pk']),
    'salary': ('Highest salary', [F('salary_max').desc(nulls_last=True), '-pk']),
}


def job_list(request):
    jobs = Job.objects.open().select_related('company')

    q = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    job_type = request.GET.get('job_type', '')
    level = request.GET.get('level', '')
    min_salary = request.GET.get('min_salary', '').strip()
    sort = request.GET.get('sort', 'latest')

    if q:
        jobs = jobs.filter(
            Q(title__icontains=q)
            | Q(company__company_name__icontains=q)
            | Q(skills__icontains=q)
            | Q(description__icontains=q)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type in dict(Job.JOB_TYPE_CHOICES):
        jobs = jobs.filter(job_type=job_type)
    if level in dict(Job.LEVEL_CHOICES):
        jobs = jobs.filter(level=level)
    if min_salary.isdigit():
        n = int(min_salary)
        jobs = jobs.filter(
            Q(salary_max__gte=n) | Q(salary_max__isnull=True, salary_min__gte=n)
        )

    if sort not in SORT_OPTIONS:
        sort = 'latest'
    jobs = jobs.order_by(*SORT_OPTIONS[sort][1])

    paginator = Paginator(jobs, PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    page_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=1, on_ends=1,
    )

    params = request.GET.copy()
    params.pop('page', None)

    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj,
        'page_range': list(page_range),
        'total': paginator.count,
        'querystring': params.urlencode(),
        'filters': {
            'q': q, 'location': location, 'job_type': job_type,
            'level': level, 'min_salary': min_salary, 'sort': sort,
        },
        'job_type_choices': Job.JOB_TYPE_CHOICES,
        'level_choices': Job.LEVEL_CHOICES,
        'sort_options': [(k, v[0]) for k, v in SORT_OPTIONS.items()],
        'has_filters': any([q, location, job_type, level, min_salary]),
    })


def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related('company'), pk=pk)

    is_owner = (
        request.user.is_authenticated
        and request.user.role == 'company'
        and job.company.user_id == request.user.id
    )
    if not (job.is_open and job.company.is_verified) and not is_owner:
        raise Http404

    is_jobseeker = request.user.is_authenticated and request.user.role == 'jobseeker'

    is_saved = (
        is_jobseeker
        and SavedJob.objects.filter(user=request.user, job=job).exists()
    )

    application = None
    if is_jobseeker:
        application = Application.objects.filter(
            job=job, applicant__user=request.user,
        ).first()

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'is_owner': is_owner,
        'is_saved': is_saved,
        'application': application,
        'applicant_count': job.applications.count() if is_owner else 0,
    })


# ---------- Jobseeker only: saved jobs ----------

@role_required('jobseeker')
@require_POST
def save_toggle(request, pk):
    """Job save / unsave (POST matra, jobseeker matra)."""
    existing = SavedJob.objects.filter(user=request.user, job_id=pk)
    if existing.exists():
        existing.delete()   # unsave: allowed even if the job is closed or unverified
    else:
        job = get_object_or_404(Job.objects.open(), pk=pk)   # save: open + verified matra
        SavedJob.objects.get_or_create(user=request.user, job=job)

    next_url = request.POST.get('next', '')
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()},
    ):
        return redirect(next_url)
    return redirect('jobs:detail', pk=pk)


@role_required('jobseeker')
def saved_list(request):
    saved = (
        SavedJob.objects
        .filter(user=request.user, job__in=Job.objects.open())
        .select_related('job', 'job__company')
    )
    return render(request, 'jobs/saved_list.html', {'saved_jobs': saved})


# ---------- Company only ----------

@role_required('company')
def my_jobs(request):
    profile = _get_company(request)
    jobs = profile.jobs.annotate(applicant_count=Count('applications'))
    return render(request, 'jobs/my_jobs.html', {'jobs': jobs, 'profile': profile})


@role_required('company')
def job_create(request):
    profile = _get_company(request)

    if not profile.is_verified:
        messages.warning(request, "Your company must be verified before you can post jobs.")
        return redirect('dashboard:company')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = profile
            job.save()
            messages.success(request, "Job posted.")
            return redirect('jobs:mine')
    else:
        form = JobForm(initial={'is_active': True})

    return render(request, 'jobs/job_form.html', {'form': form, 'page_title': 'Post a job'})


@role_required('company')
def job_edit(request, pk):
    profile = _get_company(request)
    job = get_object_or_404(Job, pk=pk, company=profile)   # arko company ko job edit garna mildaina

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated.")
            return redirect('jobs:mine')
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/job_form.html', {'form': form, 'page_title': 'Edit job'})


@role_required('company')
@require_POST
def job_delete(request, pk):
    profile = _get_company(request)
    job = get_object_or_404(Job, pk=pk, company=profile)
    job.delete()
    messages.success(request, "Job deleted.")
    return redirect('jobs:mine')