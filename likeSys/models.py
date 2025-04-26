from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings
def user_directory_path(instance, filename):
    # 文件将上传到 MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.id}/{filename}'


class CustomUser(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    groups = models.ManyToManyField(
    'auth.Group',
    related_name='customuser_set',
    blank=True,
    verbose_name='groups',
    help_text='The groups this user belongs to. A user will get allpermissions granted to each of their groups.',
)
    user_permissions = models.ManyToManyField(
    'auth.Permission',
    related_name='customuser_set',
    blank=True,
    help_text='Specific permissions for this user.',
    verbose_name='user permissions',
)
    def __str__(self):
        return f"{self.username}"

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    # file = models.FileField(upload_to=user_directory_path,storage=DocumentStorage())
    file = models.FileField(upload_to=user_directory_path)
    upload_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    public = models.BooleanField(default=False)

    fact_positive = models.PositiveIntegerField(default=0)
    fact_negative = models.PositiveIntegerField(default=0)
    style_positive = models.PositiveIntegerField(default=0)
    style_negative = models.PositiveIntegerField(default=0)
    background_positive = models.PositiveIntegerField(default=0)
    background_negative = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.id}"
    

class Vote_Document(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    fact_choice = models.BooleanField()  # True=积极，False=消极
    style_choice = models.BooleanField()
    background_choice = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """ 保存前记录旧值 """
        if self.pk:  # 仅限更新操作
            old_instance = Vote_Document.objects.get(pk=self.pk)
            self._old_values = {
                'fact': old_instance.fact_choice,
                'style': old_instance.style_choice,
                'background': old_instance.background_choice
            }
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'document')  # 确保唯一评价

    def __str__(self):
        return f"Vote by {self.user.username} on {self.document.name}"