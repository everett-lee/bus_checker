from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.urls import reverse

class BusUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        creates and saves a user with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.staff =  False
        user.admin = False
        user.active = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = False
        user.active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.active = True
        user.save(using=self._db)
        return user

class BusUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    active = models.BooleanField(default=True)
    admin = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)

    objects = BusUserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

class Buses(models.Model):
    bus = models.CharField(max_length=10)
    user = models.ForeignKey(BusUser, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('manage', kwargs={'pk': self.pk})

    def __str__(self):
        return self.bus
