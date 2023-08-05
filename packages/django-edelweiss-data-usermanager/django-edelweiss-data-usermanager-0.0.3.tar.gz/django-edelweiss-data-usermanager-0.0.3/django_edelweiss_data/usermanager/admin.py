from django.contrib import admin
from django import forms
from django.db import models

from .models import Dataset, User, Group, Published, InProgress, UserDataset, GroupDataset

class UserDatasetInline(admin.TabularInline):
    model = UserDataset
    classes = ['collapse']
    verbose_name_plural = "Access permissions for datasets"
    raw_id_fields = ['dataset', 'user']

class DatasetUserInline(UserDatasetInline):
    verbose_name_plural = "Users with access to this dataset"

class GroupDatasetInline(admin.TabularInline):
    model = GroupDataset
    classes = ['collapse']
    verbose_name_plural = "Access permissions for datasets"
    raw_id_fields = ['dataset']

class DatasetGroupInline(GroupDatasetInline):
    verbose_name_plural = "Groups with access to this dataset"

class UserGroupInline(admin.TabularInline):
    model = Group.users.through
    classes = ['collapse']
    raw_id_fields = ['user']
    verbose_name_plural = "Membership of dataset access groups"

class GroupUserInline(UserGroupInline):
    verbose_name_plural = "Members of this group"


class ReadOnlyInline(admin.TabularInline):
    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return self.fields


class DatasetInProgressInline(ReadOnlyInline):
    model = InProgress
    fields = ['name', 'created']
    classes = ['collapse']


class DatasetPublishedInline(ReadOnlyInline):
    model = Published
    fields = ['version', 'name', 'created']
    classes = ['collapse']
    verbose_name_plural = "Versions"


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    inlines = [DatasetPublishedInline, DatasetInProgressInline, DatasetUserInline, DatasetGroupInline]
    search_fields = ['id']
    readonly_fields = ['id', 'name']
    fields = ['id', 'name', 'is_public']
    list_display = ['id', 'name', 'is_public']
    list_per_page = 20 # lower than the default because the 'name' field is a little bit expensive

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def name(self, dataset):
        latest = dataset.published_set.order_by('-version').first()
        return latest.name if latest else None


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [UserGroupInline, UserDatasetInline]
    exclude = ['datasets']
    search_fields = ['email']
    list_display = ['email', 'number_of_groups', 'number_of_datasets']
    list_per_page = 20 # lower than the default because the number_of_* fields are a little bit expensive

    def number_of_groups(self, user):
        return user.group_set.count()

    number_of_groups.short_description = 'Access group memberships'

    def number_of_datasets(self, user):
        return user.userdataset_set.count()

    number_of_datasets.short_description = 'Dataset permissions'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    inlines = [GroupDatasetInline, GroupUserInline]
    exclude = ['datasets', 'users']
    list_display = ['name', 'number_of_users', 'number_of_datasets']
    list_per_page = 20 # lower than the default because the number_of_* fields are a little bit expensive

    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput},
    }

    def number_of_users(self, group):
        return group.users.count()

    number_of_users.short_description = 'Users'

    def number_of_datasets(self, group):
        return group.groupdataset_set.count()

    number_of_datasets.short_description = 'Dataset permissions'
