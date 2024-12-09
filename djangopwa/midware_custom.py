from django.utils.deprecation import MiddlewareMixin


class CustomAdminMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith('/admin/'):
            script_tag = f'<script src="{request.build_absolute_uri("/static/js/re_positions.js")}" type="text/javascript"></script>'
            response.content += script_tag.encode('utf-8')
        return response
