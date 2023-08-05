import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField


class Dataset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_public = models.BooleanField()

    class Meta:
        managed = False
        db_table = "dataset"

    def __str__(self):
        return str(self.id)


class Published(models.Model):

    # pk is a reserved word in django, hence the underscore _pk
    _pk = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='pk')

    id = models.ForeignKey(Dataset, on_delete=models.CASCADE, db_column='id')
    version = models.PositiveIntegerField()
    name = models.TextField()
    original_data_storage_path = models.TextField()
    schema = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    metadata = JSONField()

    class Meta:
        managed = False
        db_table = "published"
        verbose_name = "published dataset"

    def __str__(self):
        return '{} - {}'.format(self.id, self.version)


class InProgress(models.Model):
    id = models.OneToOneField(Dataset, primary_key=True, on_delete=models.CASCADE, db_column='id')
    name = models.TextField()
    original_data_storage_path = models.TextField()
    schema = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    metadata = JSONField()

    class Meta:
        managed = False
        db_table = "in_progress"
        verbose_name = "in progress dataset"

    def __str__(self):
        return str(self.id)


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    class Meta:
        managed = False
        db_table = "auth_user"

    def __str__(self):
        return self.email


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    users = models.ManyToManyField(User, db_table="auth_group_user", blank=True)

    class Meta:
        managed = False
        db_table = "auth_group"

    def __str__(self):
        return self.name


class UserDataset(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    can_write = models.BooleanField()

    class Meta:
        managed = False
        db_table = "auth_user_dataset"
        unique_together = ['user', 'dataset']


class GroupDataset(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    can_write = models.BooleanField()

    class Meta:
        managed = False
        db_table = "auth_group_dataset"
        unique_together = ['group', 'dataset']
