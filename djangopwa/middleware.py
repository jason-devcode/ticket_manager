# middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
from django.urls import reverse


class RemoveNextParamMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == reverse("admin:login"):
            if "next" in request.GET:
                url = reverse("admin:login")
                return HttpResponseRedirect(url)
