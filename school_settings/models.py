from django.db import models


class SchoolProfile(models.Model):
    name = models.CharField(max_length=150, default='My School')
    slogan = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=250, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='logo/', blank=True)

    class Meta:
        verbose_name = 'school profile'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        profile, _ = cls.objects.get_or_create(pk=1)
        return profile