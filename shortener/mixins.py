import json
from uuid import UUID

from django.http import JsonResponse


class ValidationMixin:
    def parse_json_body(self, request):
        try:
            return json.loads(request.body), None
        except json.JSONDecodeError:
            return None, JsonResponse({'error': "Invalid JSON payload"},
                                      status=400)
        
    def validate_uuid(self, val):
        # https://stackoverflow.com/a/33245493/2487925
        try:
            uuid_obj = UUID(val, version=4)
        except:
            return False
        return str(uuid_obj) == val