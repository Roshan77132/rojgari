from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from companies.models import CompanyProfile
from companies.forms import CompanyProfileForm
from jobseeker.models import JobSeekerProfile
from jobseeker.forms import JobSeekerProfileForm


def role_required(role):
    """Check both login and role. Redirect to the home page if the role does not match."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.role != role:
                return redirect('core:home')
            return view(request, *args, **kwargs)
        return login_required(wrapper)
    return decorator


def _company_profile(user):
    profile, _ = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={'company_name': user.username},
    )
    return profile


def _jobseeker_profile(user):
    profile, _ = JobSeekerProfile.objects.get_or_create(user=user)
    return profile


@login_required
def dashboard_redirect(request):
    if request.user.role == 'company':
        return redirect('dashboard:company')
    return redirect('dashboard:jobseeker')


@role_required('company')
def company_dashboard(request):
    profile = _company_profile(request.user)
    return render(request, 'dashboard/company_dashboard.html', {'profile': profile})


@role_required('jobseeker')
def jobseeker_dashboard(request):
    profile = _jobseeker_profile(request.user)
    return render(request, 'dashboard/jobseeker_dashboard.html', {'profile': profile})


@role_required('jobseeker')
def jobseeker_edit(request):
    profile = _jobseeker_profile(request.user)

    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard:jobseeker')
    else:
        form = JobSeekerProfileForm(instance=profile)

    return render(request, 'dashboard/jobseeker_edit.html', {'form': form})


@role_required('company')
def company_edit(request):
    profile = _company_profile(request.user)

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard:company')
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, 'dashboard/company_edit.html', {'form': form})