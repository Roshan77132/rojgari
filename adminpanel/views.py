from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.views.decorators.http import require_POST

from applications.models import Application
from companies.models import CompanyProfile
from jobs.models import Job
from notifications.services import notify

User = get_user_model()


def staff_required(view):
    """Staff only. Everyone else gets a 404 so the /manage/ URL is not revealed."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            raise Http404
        return view(request, *args, **kwargs)
    return wrapper


def _back(request, default):
    nxt = request.POST.get('next', '')
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect(default)


def _paginate(request, qs, per_page=20):
    return Paginator(qs, per_page).get_page(request.GET.get('page'))


@staff_required
def dashboard(request):
    stats = {
        'users': User.objects.count(),
        'companies': CompanyProfile.objects.count(),
        'pending': CompanyProfile.objects.filter(is_verified=False).count(),
        'jobs': Job.objects.count(),
        'open_jobs': Job.objects.open().count(),
        'applications': Application.objects.count(),
    }
    pending = (CompanyProfile.objects.filter(is_verified=False)
               .select_related('user').order_by('created_at')[:10])
    recent_applications = (Application.objects
                           .select_related('applicant__user', 'job__company')
                           .order_by('-applied_at')[:8])
    return render(request, 'adminpanel/dashboard.html', {
        'stats': stats,
        'pending': pending,
        'recent_applications': recent_applications,
    })


@staff_required
def companies(request):
    status = request.GET.get('status', 'pending')
    q = request.GET.get('q', '').strip()
    qs = CompanyProfile.objects.select_related('user').order_by('-created_at')
    if status == 'pending':
        qs = qs.filter(is_verified=False)
    elif status == 'verified':
        qs = qs.filter(is_verified=True)
    if q:
        qs = qs.filter(Q(company_name__icontains=q) | Q(user__username__icontains=q)
                       | Q(user__email__icontains=q) | Q(pan_number__icontains=q))
    return render(request, 'adminpanel/companies.html', {
        'page_obj': _paginate(request, qs), 'status': status, 'q': q,
    })


@staff_required
@require_POST
def company_verify(request, pk):
    company = get_object_or_404(CompanyProfile, pk=pk)
    if not company.is_verified:
        company.is_verified = True
        company.verified_at = timezone.now()
        company.save(update_fields=['is_verified', 'verified_at'])
        notify(
            company.user,
            "Your company has been verified. You can now post jobs.",
            link=reverse('jobs:create'),
        )
        messages.success(request, f"{company.company_name} verified.")
    return _back(request, 'adminpanel:companies')


@staff_required
@require_POST
def company_reject(request, pk):
    company = get_object_or_404(CompanyProfile, pk=pk)
    company.is_verified = False
    company.verified_at = None
    company.save(update_fields=['is_verified', 'verified_at'])
    reason = request.POST.get('reason', '').strip()
    msg = "Your company verification was rejected."
    if reason:
        msg += f" Reason: {reason}"
    msg += " Please correct your profile and document, then submit again."
    notify(company.user, msg, link=reverse('dashboard:company_edit'))
    messages.warning(request, f"{company.company_name} rejected.")
    return _back(request, 'adminpanel:companies')


@staff_required
def users(request):
    q = request.GET.get('q', '').strip()
    role = request.GET.get('role', '')
    qs = User.objects.order_by('-date_joined')
    if role in ('company', 'jobseeker'):
        qs = qs.filter(role=role)
    elif role == 'staff':
        qs = qs.filter(is_staff=True)
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q))
    return render(request, 'adminpanel/users.html', {
        'page_obj': _paginate(request, qs), 'q': q, 'role': role,
    })


@staff_required
@require_POST
def user_toggle(request, pk):
    target = get_object_or_404(User, pk=pk)
    if target == request.user or target.is_superuser:
        messages.error(request, "This user cannot be blocked.")
    else:
        target.is_active = not target.is_active
        target.save(update_fields=['is_active'])
        state = 'active' if target.is_active else 'blocked'
        messages.success(request, f"{target.username} is now {state}.")
    return _back(request, 'adminpanel:users')


@staff_required
def jobs(request):
    q = request.GET.get('q', '').strip()
    state = request.GET.get('state', '')
    qs = Job.objects.select_related('company').order_by('-pk')
    if state == 'active':
        qs = qs.filter(is_active=True)
    elif state == 'inactive':
        qs = qs.filter(is_active=False)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(company__company_name__icontains=q)
                       | Q(location__icontains=q))
    return render(request, 'adminpanel/jobs.html', {
        'page_obj': _paginate(request, qs), 'q': q, 'state': state,
    })


@staff_required
@require_POST
def job_toggle(request, pk):
    job = get_object_or_404(Job, pk=pk)
    job.is_active = not job.is_active
    job.save(update_fields=['is_active'])
    messages.success(request, f"'{job.title}' {'activated' if job.is_active else 'deactivated'}.")
    return _back(request, 'adminpanel:jobs')
