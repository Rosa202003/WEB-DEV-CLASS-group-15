from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from .models import Complaint, ComplaintComment, ComplaintHistory, Department, UserProfile
from .forms import (
    UserRegistrationForm, ComplaintForm, ComplaintUpdateForm, 
    CommentForm, UserProfileForm, UserUpdateForm
)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            # FIXED: Added 'complaints:' namespace
            return redirect('complaints:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'complaints/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # FIXED: Added 'complaints:' namespace
            return redirect('complaints:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'complaints/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    # FIXED: Added 'complaints:' namespace
    return redirect('complaints:login')

@login_required
def dashboard(request):
    total_complaints = Complaint.objects.filter(created_by=request.user).count()
    pending_complaints = Complaint.objects.filter(created_by=request.user, status='pending').count()
    resolved_complaints = Complaint.objects.filter(created_by=request.user, status='resolved').count()
    in_progress_complaints = Complaint.objects.filter(created_by=request.user, status='in_progress').count()
    rejected_complaints = total_complaints - pending_complaints - in_progress_complaints - resolved_complaints
    
    recent_complaints = Complaint.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    assigned_complaints = []
    if hasattr(request.user, 'profile') and request.user.profile.is_staff_member:
        assigned_complaints = Complaint.objects.filter(assigned_to=request.user).order_by('-created_at')[:5]
    
    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'in_progress_complaints': in_progress_complaints,
        'rejected_complaints': rejected_complaints,
        'recent_complaints': recent_complaints,
        'assigned_complaints': assigned_complaints,
        'is_staff': hasattr(request.user, 'profile') and request.user.profile.is_staff_member,
    }
    return render(request, 'complaints/dashboard.html', context)

@login_required
def complaint_list(request):
    complaints = Complaint.objects.filter(created_by=request.user)
    
    status_filter = request.GET.get('status')
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        complaints = complaints.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    paginator = Paginator(complaints, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'complaints': page_obj,
        'status_choices': Complaint.STATUS_CHOICES,
    }
    return render(request, 'complaints/complaint_list.html', context)

@login_required
def complaint_create(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.created_by = request.user
            complaint.save()
            messages.success(request, 'Complaint created successfully!')
            # FIXED: Added 'complaints:' namespace
            return redirect('complaints:complaint_detail', complaint.id)
    else:
        form = ComplaintForm()
    
    return render(request, 'complaints/complaint_form.html', {
        'form': form,
        'is_edit': False,
        'form_title': 'Create Complaint'
    })

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk, created_by=request.user)
    comments = complaint.comments.all()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.complaint = complaint
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            # FIXED: Added 'complaints:' namespace
            return redirect('complaints:complaint_detail', pk=pk)
    else:
        comment_form = CommentForm()
    
    context = {
        'complaint': complaint,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'complaints/complaint_detail.html', context)

@login_required
def complaint_update(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = ComplaintUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            old_status = complaint.status
            form.save()
            
            if old_status != complaint.status:
                ComplaintHistory.objects.create(
                    complaint=complaint,
                    changed_by=request.user,
                    field_changed='status',
                    old_value=old_status,
                    new_value=complaint.status
                )
            
            messages.success(request, 'Complaint updated successfully!')
            # FIXED: Added 'complaints:' namespace
            return redirect('complaints:complaint_detail', pk=pk)
    else:
        form = ComplaintUpdateForm(instance=complaint)
    
    return render(request, 'complaints/complaint_update.html', {'form': form, 'complaint': complaint})

@login_required
def complaint_delete(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk, created_by=request.user)
    if request.method == 'POST':
        complaint.delete()
        messages.success(request, 'Complaint deleted successfully!')
        # FIXED: Added 'complaints:' namespace
        return redirect('complaints:complaint_list')
    
    return render(request, 'complaints/complaint_confirm_delete.html', {'complaint': complaint})

@login_required
def staff_dashboard(request):
    if not request.user.profile.is_staff_member:
        messages.error(request, 'You do not have permission to view this page.')
        # FIXED: Added 'complaints:' namespace
        return redirect('complaints:dashboard')
    
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status='pending').count()
    in_progress_complaints = Complaint.objects.filter(status='in_progress').count()
    resolved_complaints = Complaint.objects.filter(status='resolved').count()
    
    priority_counts = {key: 0 for key, _ in Complaint.PRIORITY_CHOICES}
    for item in Complaint.objects.values('priority').annotate(count=Count('id')):
        priority_counts[item['priority']] = item['count']

    priority_stats = [
        {'label': label, 'count': priority_counts.get(key, 0)}
        for key, label in Complaint.PRIORITY_CHOICES
    ]
    
    department_counts = []
    for item in Complaint.objects.values('department__name').annotate(count=Count('id')).order_by('-count'):
        department_counts.append({
            'name': item['department__name'] or 'Unassigned',
            'count': item['count']
        })
    top_departments = department_counts[:5]
    
    pending_percent = round(pending_complaints / total_complaints * 100) if total_complaints else 0
    in_progress_percent = round(in_progress_complaints / total_complaints * 100) if total_complaints else 0
    resolved_percent = round(resolved_complaints / total_complaints * 100) if total_complaints else 0
    
    week_ago = timezone.now() - timedelta(days=7)
    new_this_week = Complaint.objects.filter(created_at__gte=week_ago).count()
    overdue_complaints = Complaint.objects.filter(
        status__in=['pending', 'in_progress'],
        created_at__lt=week_ago
    ).count()
    
    recent_complaints = Complaint.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'resolved_complaints': resolved_complaints,
        'priority_stats': priority_stats,
        'priority_counts': priority_counts,
        'top_departments': top_departments,
        'pending_percent': pending_percent,
        'in_progress_percent': in_progress_percent,
        'resolved_percent': resolved_percent,
        'new_this_week': new_this_week,
        'overdue_complaints': overdue_complaints,
        'recent_complaints': recent_complaints,
    }
    return render(request, 'complaints/staff_dashboard.html', context)

@login_required
def staff_complaint_list(request):
    if not request.user.profile.is_staff_member:
        messages.error(request, 'You do not have permission to view this page.')
        # FIXED: Added 'complaints:' namespace
        return redirect('complaints:dashboard')
    
    complaints = Complaint.objects.all()
    
    status_filter = request.GET.get('status')
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        complaints = complaints.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(complaints, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'complaints': page_obj,
        'status_choices': Complaint.STATUS_CHOICES,
    }
    return render(request, 'complaints/staff_complaint_list.html', context)

@login_required
def staff_complaint_detail(request, pk):
    if not request.user.profile.is_staff_member:
        messages.error(request, 'You do not have permission to view this page.')
        # FIXED: Added 'complaints:' namespace
        return redirect('complaints:dashboard')
    
    complaint = get_object_or_404(Complaint, pk=pk)
    comments = complaint.comments.all()
    
    if request.method == 'POST':
        if 'update_status' in request.POST:
            form = ComplaintUpdateForm(request.POST, instance=complaint)
            if form.is_valid():
                old_status = complaint.status
                form.save()
                
                ComplaintHistory.objects.create(
                    complaint=complaint,
                    changed_by=request.user,
                    field_changed='status',
                    old_value=old_status,
                    new_value=complaint.status
                )
                
                messages.success(request, 'Complaint status updated successfully!')
                # FIXED: Added 'complaints:' namespace
                return redirect('complaints:staff_complaint_detail', pk=pk)
        else:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.complaint = complaint
                comment.user = request.user
                comment.save()
                messages.success(request, 'Comment added successfully!')
                # FIXED: Added 'complaints:' namespace
                return redirect('complaints:staff_complaint_detail', pk=pk)
    else:
        form = ComplaintUpdateForm(instance=complaint)
        comment_form = CommentForm()
    
    context = {
        'complaint': complaint,
        'comments': comments,
        'form': form,
        'comment_form': comment_form,
    }
    return render(request, 'complaints/staff_complaint_detail.html', context)

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            # FIXED: Added 'complaints:' namespace
            return redirect('complaints:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'complaints/profile.html', context)