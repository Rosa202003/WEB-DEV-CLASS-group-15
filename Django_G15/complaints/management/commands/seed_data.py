from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from complaints.models import Department, Complaint, UserProfile

class Command(BaseCommand):
    help = 'Seed database with sample data'
    
    def handle(self, *args, **kwargs):
        # Create departments
        departments = [
            'IT Support',
            'Administration',
            'Facilities',
            'HR',
            'Finance'
        ]
        
        for dept in departments:
            Department.objects.get_or_create(name=dept)
        
        # Create staff user
        staff_user, created = User.objects.get_or_create(
            username='staff',
            defaults={
                'email': 'staff@example.com',
                'first_name': 'Staff',
                'last_name': 'User'
            }
        )
        if created:
            staff_user.set_password('staff123')
            staff_user.save()
            UserProfile.objects.create(
                user=staff_user,
                is_staff_member=True,
                department=Department.objects.first()
            )
        
        # Create regular user
        regular_user, created = User.objects.get_or_create(
            username='user',
            defaults={
                'email': 'user@example.com',
                'first_name': 'Regular',
                'last_name': 'User'
            }
        )
        if created:
            regular_user.set_password('user123')
            regular_user.save()
            UserProfile.objects.create(user=regular_user)
        
        # Create sample complaints
        if Complaint.objects.count() == 0:
            dept = Department.objects.first()
            for i in range(5):
                Complaint.objects.create(
                    title=f'Sample Complaint {i+1}',
                    description=f'This is sample complaint number {i+1}',
                    category='General',
                    department=dept,
                    created_by=regular_user,
                    status=['pending', 'in_progress', 'resolved'][i % 3],
                    priority=['low', 'medium', 'high'][i % 3]
                )
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))