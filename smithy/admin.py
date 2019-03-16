## -*- coding: utf-8 -*-
from django.contrib import admin, messages
from django.db import models
from django.forms.widgets import TextInput
from django.conf import settings
from smithy.models import RequestBlueprint, RequestRecord, Header, QueryParameter, Cookie, Variable

CODEMIRROR_PATH = getattr(settings, 'SMITHY_CODEMIRROR_PATH', "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.44.0/").rstrip('/')


def send(modeladmin, request, queryset):
    for obj in queryset:
        obj.send()
    messages.success(request, "Sent {} request{}".format(
        queryset.count(),
        's' if queryset.count() != 1 else ''
    ))

send.short_description = "Send"


def ObjectInline(m, readonly = False):
    class Inline(admin.TabularInline):
        extra = 0
        max_num = 0 if readonly else None
        model = m
        can_delete = not readonly
        fields = ['name', 'value']
        formfield_overrides = {
            models.TextField: {'widget': TextInput},
        }
        def get_readonly_fields(self, request, obj = None):
            if obj and readonly:
                self.readonly_fields = self.fields
            return self.readonly_fields

    return Inline


class RequestAdmin(admin.ModelAdmin):
    list_display = ['url', 'method', 'created', 'modified']
    exclude = ['request_ptr', 'id']
    fields = [
        'name',
        'method',
        #'follow_redirects',
        'url',
        'body',
    ]
    inlines = [
        ObjectInline(Header),
        ObjectInline(QueryParameter),
        ObjectInline(Cookie),
        ObjectInline(Variable)
    ]


class RequestBlueprintAdmin(RequestAdmin):
    actions = [
        send
    ]

    class Media:
        css = {
            'all': (CODEMIRROR_PATH + '/codemirror.css',)
        }

        js = (
            CODEMIRROR_PATH + '/codemirror.js',
            CODEMIRROR_PATH + '/addon/mode/overlay.js',
            CODEMIRROR_PATH + '/mode/xml/xml.js',
            CODEMIRROR_PATH + '/mode/htmlmixed/htmlmixed.js',
            CODEMIRROR_PATH + '/mode/django/django.js',
            'js/smithy.js',
        )


class RequestRecordAdmin(RequestAdmin):
    inlines = [
        ObjectInline(Header, True),
        ObjectInline(QueryParameter, True),
        ObjectInline(Cookie, True),
    ]

    fields = RequestAdmin.fields + ['response']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.readonly_fields = [
                field.name for field in obj.__class__._meta.fields
                if field.name not in self.exclude]
        return self.readonly_fields

    class Media:
        css = {
            'all': ('css/smithy.css',)
        }


admin.site.register(RequestBlueprint, RequestBlueprintAdmin)
admin.site.register(RequestRecord, RequestRecordAdmin)
