import os

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count, Sum
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render

from applications.models import Application
from companies.models import CompanyProfile
from jobs.models import Job
from jobseeker.models import JobSeekerProfile


def home_view(request):
    live = Job.objects.open()

    # Hero ko counts: 5 minute cache (database query har page load ma hudaina)
    stats = cache.get('home_stats')
    if stats is None:
        stats = {
            'jobs': live.count(),
            'vacancies': live.aggregate(total=Sum('vacancies'))['total'] or 0,
            'companies': live.values('company').distinct().count(),
        }
        cache.set('home_stats', stats, 300)

    # Top employers: sabai bhanda dherai open job bhako company pahile
    top_companies = (
        CompanyProfile.objects.filter(jobs__in=live)
        .exclude(logo='')
        .exclude(logo__isnull=True)
        .annotate(open_jobs=Count('jobs'))
        .order_by('-open_jobs', 'company_name')[:12]
    )

    return render(request, 'core/home.html', {
        'stats': stats,
        'top_companies': top_companies,
        'latest_jobs': live.select_related('company')[:12],
    })


def _send(field, filename):
    if not field:
        raise Http404
    ext = os.path.splitext(field.name)[1]
    return FileResponse(field.open('rb'), as_attachment=True, filename=f"{filename}{ext}")


@login_required
def profile_resume(request, pk):
    """Jobseeker ko resume: afai, staff, ya tyo jobseeker le apply gareko company le matra."""
    profile = get_object_or_404(JobSeekerProfile.objects.select_related('user'), pk=pk)
    uid = request.user.id
    allowed = (
        profile.user_id == uid
        or request.user.is_staff
        or Application.objects.filter(
            applicant=profile, job__company__user_id=uid,
        ).exists()
    )
    if not allowed:
        raise Http404
    return _send(profile.resume, f"{profile.user.username}_resume")


@login_required
def company_document(request, pk):
    """Registration document: company afai, ya admin matra."""
    company = get_object_or_404(CompanyProfile, pk=pk)
    if not (company.user_id == request.user.id or request.user.is_staff):
        raise Http404
    return _send(company.registration_document, f"{company.company_name}_document")

def about_view(request):
    live = Job.objects.open()

    stats = cache.get('about_stats')
    if stats is None:
        stats = {
            'jobs': live.count(),
            'companies': CompanyProfile.objects.count(),
            'jobseekers': JobSeekerProfile.objects.count(),
        }
        cache.set('about_stats', stats, 300)

    return render(request, 'core/about.html', {'stats': stats})