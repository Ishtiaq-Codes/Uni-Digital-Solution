"""
Management command to seed the database with demo data.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import uuid


class Command(BaseCommand):
    help = 'Seed the database with demo data for all modules'

    def handle(self, *args, **options):
        self.stdout.write('[*] Seeding database...\n')

        # 1. Create departments
        from apps.university.models import Department, Announcement, AcademicEvent
        departments = []
        dept_data = [
            ('CS', 'Computer Science', 'Department of Computer Science and Information Technology'),
            ('AGR', 'Agriculture', 'Department of Agronomy and Agricultural Sciences'),
            ('VET', 'Veterinary Sciences', 'Department of Veterinary and Animal Sciences'),
        ]
        for code, name, desc in dept_data:
            dept, _ = Department.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': desc}
            )
            departments.append(dept)
        self.stdout.write(f'  [OK] Created {len(departments)} departments')

        # 2. Create users
        from apps.accounts.models import User

        users = {}
        user_data = [
            ('admin@uaf.edu.pk', 'Admin', 'User', 'super_admin', None, None),
            ('uadmin@uaf.edu.pk', 'University', 'Admin', 'university_admin', None, None),
            ('dadmin@uaf.edu.pk', 'Department', 'Admin', 'department_admin', None, departments[0]),
            ('faculty1@uaf.edu.pk', 'Dr. Ahmad', 'Khan', 'faculty', '2020-FAC-001', departments[0]),
            ('faculty2@uaf.edu.pk', 'Dr. Sara', 'Ali', 'faculty', '2020-FAC-002', departments[1]),
            ('ug1@uaf.edu.pk', 'Ali', 'Hassan', 'ug_student', '2021-ag-1234', departments[0]),
            ('ug2@uaf.edu.pk', 'Fatima', 'Zahra', 'ug_student', '2021-ag-5678', departments[1]),
            ('pg1@uaf.edu.pk', 'Usman', 'Ghani', 'pg_student', '2022-MS-001', departments[0]),
            ('pg2@uaf.edu.pk', 'Ayesha', 'Siddiqui', 'pg_student', '2022-MS-002', departments[2]),
            ('qec@uaf.edu.pk', 'QEC', 'Officer', 'qec_officer', None, None),
        ]

        for email, first, last, role, reg_num, dept in user_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'role': role,
                    'registration_number': reg_num,
                    'is_active': True,
                    'is_staff': role in ['super_admin', 'university_admin'],
                    'is_superuser': role == 'super_admin',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                if dept:
                    user.profile.department = dept
                    user.profile.save()
            users[email] = user

        self.stdout.write(f'  [OK] Created {len(user_data)} users (password: password123)')

        # 3. Create courses
        from apps.courses.models import Course, CourseEnrollment
        courses_created = []
        course_data = [
            ('CS-301', 'Data Structures', departments[0], users['faculty1@uaf.edu.pk'], 5, 'ug'),
            ('CS-401', 'Machine Learning', departments[0], users['faculty1@uaf.edu.pk'], 7, 'ug'),
            ('CS-501', 'Advanced Algorithms', departments[0], users['faculty1@uaf.edu.pk'], 1, 'pg'),
            ('AGR-201', 'Soil Science', departments[1], users['faculty2@uaf.edu.pk'], 3, 'ug'),
            ('AGR-301', 'Crop Production', departments[1], users['faculty2@uaf.edu.pk'], 5, 'ug'),
            ('AGR-501', 'Precision Agriculture', departments[1], users['faculty2@uaf.edu.pk'], 1, 'pg'),
            ('VET-201', 'Animal Anatomy', departments[2], None, 3, 'ug'),
            ('VET-301', 'Livestock Management', departments[2], None, 5, 'ug'),
            ('VET-501', 'Advanced Pathology', departments[2], None, 1, 'pg'),
        ]
        for code, title, dept, instructor, sem, level in course_data:
            course, _ = Course.objects.get_or_create(
                code=code,
                defaults={
                    'title': title, 'department': dept,
                    'instructor': instructor, 'semester': sem,
                    'level': level, 'credit_hours': 3,
                    'description': f'Comprehensive course on {title.lower()} covering theory and practice.',
                }
            )
            courses_created.append(course)

        # Enroll students
        for student_email in ['ug1@uaf.edu.pk', 'ug2@uaf.edu.pk']:
            for course in courses_created[:3]:
                CourseEnrollment.objects.get_or_create(
                    student=users[student_email], course=course
                )
        for student_email in ['pg1@uaf.edu.pk', 'pg2@uaf.edu.pk']:
            for course in [c for c in courses_created if c.level == 'pg']:
                CourseEnrollment.objects.get_or_create(
                    student=users[student_email], course=course
                )

        self.stdout.write(f'  [OK] Created {len(courses_created)} courses with enrollments')

        # 4. Create fee vouchers
        from apps.fees.models import FeeVoucher
        for i, student_email in enumerate(['ug1@uaf.edu.pk', 'ug2@uaf.edu.pk', 'pg1@uaf.edu.pk']):
            FeeVoucher.objects.get_or_create(
                voucher_number=f'UAF-2025-DEMO-{i+1:04d}',
                defaults={
                    'student': users[student_email],
                    'amount': 45000 + (i * 5000),
                    'semester': 'Semester 5',
                    'academic_year': '2024-2025',
                    'due_date': timezone.now().date() + timedelta(days=30),
                    'status': ['pending', 'paid', 'approved'][i],
                    'created_by': users['admin@uaf.edu.pk'],
                }
            )
        self.stdout.write('  [OK] Created sample fee vouchers')

        # 5. Create form templates
        from apps.form_manager.models import FormTemplate, FormSubmission
        ug_template, _ = FormTemplate.objects.get_or_create(
            title='Admission Form',
            defaults={
                'form_type': 'ug',
                'description': 'Undergraduate admission form for new students.',
                'fields_schema': [
                    {'name': 'father_name', 'label': 'Father Name', 'type': 'text', 'required': True},
                    {'name': 'dob', 'label': 'Date of Birth', 'type': 'date', 'required': True},
                    {'name': 'address', 'label': 'Address', 'type': 'text', 'required': True},
                ],
                'created_by': users['admin@uaf.edu.pk'],
            }
        )
        pg_template, _ = FormTemplate.objects.get_or_create(
            title='GS-10 Progress Report',
            defaults={
                'form_type': 'pg',
                'description': 'Postgraduate GS-10 research progress report.',
                'requires_supervisor': True,
                'requires_hod': True,
                'fields_schema': [
                    {'name': 'research_title', 'label': 'Research Title', 'type': 'text', 'required': True},
                    {'name': 'progress', 'label': 'Progress Summary', 'type': 'text', 'required': True},
                ],
                'created_by': users['admin@uaf.edu.pk'],
            }
        )

        FormSubmission.objects.get_or_create(
            template=ug_template, student=users['ug1@uaf.edu.pk'],
            defaults={'form_data': {'father_name': 'Muhammad Hassan', 'dob': '2002-05-15', 'address': 'Faisalabad'}, 'status': 'pending'}
        )
        FormSubmission.objects.get_or_create(
            template=pg_template, student=users['pg1@uaf.edu.pk'],
            defaults={'form_data': {'research_title': 'AI in Agriculture', 'progress': 'Literature review completed'}, 'status': 'approved'}
        )
        self.stdout.write('  [OK] Created form templates and submissions')

        # 6. Create QEC feedback
        from apps.qec.models import QECFeedback
        for course in courses_created[:4]:
            for rating in [4, 5, 3]:
                QECFeedback.objects.create(
                    course=course,
                    teaching_rating=rating,
                    content_rating=rating,
                    assessment_rating=max(1, rating - 1),
                    overall_rating=rating,
                    comments=f'Good course on {course.title}.',
                    is_anonymous=True,
                )
        self.stdout.write('  [OK] Created QEC feedback')

        # 7. Create announcements
        Announcement.objects.get_or_create(
            title='Welcome to UAF Smart Dashboard',
            defaults={
                'content': 'We are excited to launch the new UAF Smart Dashboard System. This platform will revolutionize how we manage academic and administrative operations.',
                'priority': 'high',
                'target_audience': 'all',
                'is_active': True,
                'is_pinned': True,
                'publish_date': timezone.now(),
                'created_by': users['admin@uaf.edu.pk'],
            }
        )
        Announcement.objects.get_or_create(
            title='Mid-Term Examinations Schedule',
            defaults={
                'content': 'Mid-term examinations will begin from next week. All students are advised to prepare accordingly and check the academic calendar for detailed schedule.',
                'priority': 'urgent',
                'target_audience': 'students',
                'is_active': True,
                'publish_date': timezone.now() - timedelta(days=2),
                'created_by': users['admin@uaf.edu.pk'],
            }
        )
        Announcement.objects.get_or_create(
            title='Faculty Meeting - Department Heads',
            defaults={
                'content': 'A faculty meeting is scheduled for all department heads to discuss curriculum updates and research initiatives.',
                'priority': 'medium',
                'target_audience': 'faculty',
                'is_active': True,
                'publish_date': timezone.now() - timedelta(days=5),
                'created_by': users['admin@uaf.edu.pk'],
            }
        )
        self.stdout.write('  [OK] Created announcements')

        # 8. Create academic events
        AcademicEvent.objects.get_or_create(
            title='Spring Semester Begins',
            defaults={'event_type': 'academic', 'start_date': timezone.now().date()}
        )
        AcademicEvent.objects.get_or_create(
            title='Mid-Term Examinations',
            defaults={'event_type': 'exam', 'start_date': timezone.now().date() + timedelta(days=30), 'end_date': timezone.now().date() + timedelta(days=37)}
        )
        self.stdout.write('  [OK] Created academic events')

        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))
        self.stdout.write('\nDemo Accounts:')
        self.stdout.write('  Admin:    admin@uaf.edu.pk / password123')
        self.stdout.write('  Faculty:  faculty1@uaf.edu.pk / password123')
        self.stdout.write('  UG:       ug1@uaf.edu.pk / password123')
        self.stdout.write('  PG:       pg1@uaf.edu.pk / password123')
        self.stdout.write('  QEC:      qec@uaf.edu.pk / password123')
