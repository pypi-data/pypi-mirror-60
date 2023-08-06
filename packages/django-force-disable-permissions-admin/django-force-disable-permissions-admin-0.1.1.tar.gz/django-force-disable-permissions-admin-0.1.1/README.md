# django-force-disable-permissions-admin

Force disable permissions in admin site.

## Install

```shell
pip install django-force-disable-permissions-admin
```

## Usage


**pro/settings.py**

```python
INSTALLED_APPS = [
    ...
    'force_disable_permissions',
    ...
]
```

**app/admin.py**

```python
from django.contrib import admin
from .models import Category
from .models import Book
from force_disable_permissions.admin import ForceDisablePermissionsAdminMixin

class BookInline(admin.TabularInline):
    model = Book

class CategoryAdmin(ForceDisablePermissionsAdminMixin, admin.ModelAdmin):
    delete_permission_enable_for_superuser = True
    view_permission_enable_for_superuser = True
    force_disable_delete_permission = True
    force_disable_change_permission = True

    list_display = ["name"]
    inlines = [
        BookInline,
    ]

admin.site.register(Category, CategoryAdmin)

```

## Control Variables

- add_permission_enable_for_superuser = False
- delete_permission_enable_for_superuser = False
- change_permission_enable_for_superuser = False
- view_permission_enable_for_superuser = False
- force_disable_add_permission = False
- force_disable_delete_permission = False
- force_disable_change_permission = False
- force_disable_view_permission = False

*Note:*

- By default, ForceDisablePermissionsAdminMixin doesn't change anything.
- Use the control-variabl to disable permissions.

## Releases

### v0.1.1 2020.02.05

- Fix usage document.

### v0.1.0 2020.02.05

- First release.
