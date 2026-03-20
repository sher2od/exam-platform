from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractUser):
    # Role Choices
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    EMPLOYEE = 'EMPLOYEE'

    ROLE_CHOICES = (
        (ADMIN, 'Admin (SuperAdmin)'),
        (MANAGER, 'Manager (Bo\'lim boshlig\'i)'),
        (EMPLOYEE, 'Employee (Xodim)'),
    )

    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default=EMPLOYEE
    )
    
    description = models.TextField(blank=True, null=True)

    # Department bog'lanishi
    department = models.ForeignKey(
        'departments.Department', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='users'
    )

    assigned_exam = models.ForeignKey(
        'exams.Exam',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_employees'
    )

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return f"{self.phone_number} ({self.role})"
