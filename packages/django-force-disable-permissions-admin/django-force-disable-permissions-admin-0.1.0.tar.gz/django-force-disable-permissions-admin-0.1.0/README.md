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
from force_disable_permissions.admin import ForceDisablePermissionsAdminMixin
from .models import Category
from .models import Book

class BookInline(admin.TabularInline):
    model = Book

class CategoryAdmin(ForceDisablePermissionsAdminMixin, admin.ModelAdmin):
    DELETE_PERMISSION_ENABLE_FOR_SUPERUSER = True
    VIEW_PERMISSION_ENABLE_FOR_SUPERUSER = True
    FORCE_DISABLE_DELETE_PERMISSION = True
    FORCE_DISABLE_CHANGE_PERMISSION = True
    FORCE_DISABLE_VIEW_PERMISSION = True

    list_display = ["name"]
    inlines = [
        BookInline,
    ]

admin.site.register(Category, CategoryAdmin)
```

## Releases

### v0.1.0 2020.02.05

- First release.
