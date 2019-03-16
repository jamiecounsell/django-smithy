from django.test import TestCase

from smithy.models import RequestBlueprint, QueryParameter


class RequestBlueprintTestCase(TestCase):

    def setUp(self):
        self.request = RequestBlueprint()
        self.request.url = "https://postman-echo.com/get"
        self.request.method = RequestBlueprint.METHODS[0][0]
        self.request.save()

    def test_query_params_get_added(self):
        QueryParameter.objects.create(
            name = "test-name",
            value = "text-value",
            request = self.request
        )
        self.request.send()

    def test_query_params_preserves_params_in_original_url(self):
        self.request.url += "?persist=true"
        self.request.save()
        QueryParameter.objects.create(
            name = "test-name",
            value = "text-value",
            request = self.request
        )
        self.request.send()

