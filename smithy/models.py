# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from requests import Request as HTTPRequest, Session
from requests.cookies import create_cookie, RequestsCookieJar
from urllib.parse import parse_qs, urlparse, urlencode
from requests_toolbelt.utils import dump

from model_utils.models import TimeStampedModel

from smithy.helpers import render_with_context, parse_dump_result


class NameValueModel(TimeStampedModel):
    name = models.CharField(max_length = 200)
    value = models.TextField(blank = True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Request(TimeStampedModel):
    """
    A base model shared by RequestBlueprint and
    RequestRecord. Used solely to reduce
    """
    METHODS = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('OPTIONS', 'OPTIONS'),
        ('HEAD', 'HEAD'),
    )
    BODY_TYPES = (
        ('', 'Other'),
        ('application/x-www-form-urlencoded', 'x-www-form-urlencoded'),
        ('application/json', 'JSON'),
        ('text/plain', 'Text'),
        ('application/javascript', 'JavaScript'),
        ('application/xml', 'XML (application/xml)'),
        ('text/xml', 'XML (text/xml)'),
        ('text/html', 'HTML'),
    )
    method = models.CharField(
        max_length = 7, choices = METHODS,
        blank = False, null = False)
    name = models.CharField(max_length = 500, blank = False)
    url = models.CharField(max_length = 2083)
    body = models.TextField(blank = True)
    content_type = models.CharField(
        default = BODY_TYPES[0][0],
        blank = True, null = True,
        max_length = 100, choices = BODY_TYPES)

    def __str__(self):
        if self.name:
            return self.name
        return "{} {}".format(
            self.method,
            self.url,
        )


class RequestBlueprint(Request):
    """
    A blueprint for HTTP requests. This model will be
    used to generate and send HTTP requests. Once sent,
    a RequestRecord will be created for that request.
    """
    follow_redirects = models.BooleanField(
        default = False, blank = False, null = False)

    @property
    def name_value_related(self):
        return [
            self.headers,
            self.query_parameters,
            self.cookies
        ]

    def send(self, context = None):

        context = context or {}
        for variable in self.variables.all():
            context[variable.name] = variable.value

        request = HTTPRequest(
            url = render_with_context(self.url, context),
            method = self.method)

        session = Session()
        record = RequestRecord.objects.create(blueprint = self)

        # Copy RequestBlueprint values to RequestRecord
        for qs in self.name_value_related:
            for obj in qs.all():
                obj.pk = 0
                obj.name = render_with_context(obj.name, context)
                obj.value = render_with_context(obj.value, context)
                obj.add_to(request)
                obj.request = record
                obj.save()

        if self.content_type == self.BODY_TYPES[0][0]:
            data = render_with_context(self.body, context)
        else:
            data = {}
            for param in self.body_parameters.all():
                param.add_to(data, context)

        request.data = data
        prepared_request = request.prepare()

        response = session.send(prepared_request, stream = True)
        # TODO: follow redirects

        RequestRecord.objects.filter(pk = record.pk).update(
            raw_request = parse_dump_result(dump._dump_request_data, prepared_request),
            raw_response = parse_dump_result(dump._dump_response_data, response),
            status = response.status_code,
            **RequestRecord.get_clone_args(self, context)
        )

        # Return fresh copy after update
        return RequestRecord.objects.get(pk = record.pk)


class RequestRecord(Request):
    """
    A record of a Request that has been sent.
    Contains response and diagnostic information
    about the request.
    """
    raw_request = models.TextField()
    raw_response = models.TextField()
    status = models.PositiveIntegerField(null = True)
    blueprint = models.ForeignKey(
        'smithy.RequestBlueprint',
        on_delete = models.SET_NULL,
        null = True)

    @property
    def is_success(self):
        return self.status and self.status < 400

    @staticmethod
    def of_blueprint(blueprint):
        return RequestRecord.objects.filter(
            blueprint = blueprint)

    @classmethod
    def get_clone_args(cls, obj, context : dict):
        return dict([
            (
                render_with_context(fld.name, context),
                render_with_context(getattr(obj, fld.name), context)
            )
            for fld \
            in cls._meta.fields \
            if fld.name != obj._meta.pk \
            and fld in obj._meta.fields \
            and fld.name not in [
                   'request', 'id', 'created', 'updated'
               ]])


class Variable(NameValueModel):
    """
    A static variable for this request. Will be added
    directly to the request's context. Use this to
    add custom context to this request that may be
    used in several places.
    """
    request = models.ForeignKey(
        'smithy.RequestBlueprint',
        on_delete = models.CASCADE,
        related_name = 'variables')


class BodyParameter(NameValueModel):
    """
    A x-www-form-urlencoded parameter. Will be properly
    urlencoded and added to the body when the request is
    sent.
    """
    request = models.ForeignKey(
        'smithy.RequestBlueprint',
        on_delete = models.CASCADE,
        related_name = 'body_parameters')

    def add_to(self, payload : dict, context: dict):
        if self.name and self.value:
            payload[
                render_with_context(self.name, context)
            ] = render_with_context(self.value, context)
        else:
            pass # TODO: warn


class Header(NameValueModel):
    """
    An HTTP header. HTTP headers are case insensitive,
    but to ensure consistent behaviour, header names
    will be converted to uppercase before rqeuests
    are sent.
    """
    request = models.ForeignKey(
        'smithy.Request',
        on_delete = models.CASCADE,
        related_name = 'headers')

    def add_to(self, request : HTTPRequest):
        if self.name and self.value:
            request.headers[self.name] = self.value
        else:
            pass # TODO: warn


class QueryParameter(NameValueModel):
    """
    A query parameter. Static query parameters can be
    set in the RequestBlueprint's URL field, but it may
    be easier to manage large or complex sets of query
    parameters separately.
    """
    request = models.ForeignKey(
        'smithy.Request',
        on_delete = models.CASCADE,
        related_name = 'query_parameters')

    def add_to(self, request : HTTPRequest):
        existing_param_str = urlparse(request.url).query
        param_dict = parse_qs(existing_param_str)

        param_dict[self.name] = self.value

        base_url = request.url.rstrip(existing_param_str)
        param_str = urlencode(param_dict, doseq=True)
        request.url = base_url.rstrip("?") + "?" + param_str


class Cookie(NameValueModel):
    """
    A convenience method to avoid needing to define the
    Cookie header and follow correct syntax. If a request
    has both a Cookie defined and a Header with the name
    "Cookie", the Header will used and the Cookie(s) will
    be ignored.
    """
    request = models.ForeignKey(
        'smithy.Request',
        on_delete = models.CASCADE,
        related_name = 'cookies')

    def add_to(self, request : HTTPRequest):
        request.cookies = request.cookies or RequestsCookieJar()
        request.cookies.set_cookie(
            create_cookie(self.name, self.value)
        )


@receiver(post_save, sender = RequestBlueprint)
def add_content_type(sender, instance : RequestBlueprint, created, **kwargs):
    if created and not instance.headers.filter(name__iexact = 'content-type').exists():
        instance.content_type and Header.objects.create(
            name = 'Content-Type',
            value = instance.content_type,
            request = instance.request_ptr
        )
