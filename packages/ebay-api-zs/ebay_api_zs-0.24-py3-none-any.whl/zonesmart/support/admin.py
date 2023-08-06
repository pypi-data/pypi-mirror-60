from django.contrib import admin

import nested_admin

from . import models


class SupportRequestMessageFileInline(nested_admin.NestedTabularInline):
    model = models.SupportRequestMessageFile
    extra = 1
    inlines = []


class SupportRequestMessageInline(nested_admin.NestedTabularInline):
    model = models.SupportRequestMessage
    extra = 1
    inlines = [SupportRequestMessageFileInline]


@admin.register(models.SupportRequest)
class SupportRequestAdmin(nested_admin.NestedModelAdmin):
    model = models.SupportRequest
    inlines = [SupportRequestMessageInline]
