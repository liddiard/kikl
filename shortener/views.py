from datetime import timedelta

from django.http import JsonResponse, HttpResponseNotFound
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.generic.base import View, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404

from ipware import get_client_ip

from .models import Adjective, Noun, Link
from .mixins import ValidationMixin


# maximum number of links per user
MAX_USER_LINKS = 10
# maximum duration of a link (hours)
MAX_LINK_DURATION = 24 * 7 # 1 week

# pages

class FrontPageView(TemplateView):
    
    template_name = "front.html"

    def get_context_data(self, **kwargs):
        context = super(FrontPageView, self).get_context_data(**kwargs)
        context['sample_paths'] = ['goofy-lemur', 'fabulous-anteater', 
                                   'awkward-puffin']
        return context


class AboutPageView(TemplateView):
    pass


# redirect to link
def target_view(request, adjective, noun):
    a = get_object_or_404(Adjective, word=adjective)
    n = get_object_or_404(Noun, word=noun)
    link = get_object_or_404(Link, is_active=True, adjective=a, noun=n)
    link.deactivate_if_expired()
    if link.is_active:
        return redirect(link.target)
    else:
        return HttpResponseNotFound()


# API

@method_decorator(csrf_exempt, name='dispatch')
class LinkView(ValidationMixin, View):

    # return an array of links' metadata given their UUIDs
    def get(self, request):
        body, error = self.parse_json_body(request)
        if error is not None:
            return error
        
        if "uuids" not in body:
            return JsonResponse(
                {'error': "Missing 'links' key in JSON payload"},
                status=400
            )
        links = body["uuids"]

        if not isinstance(links, list):
            return JsonResponse(
                {'error': "'links' key in JSON payload must be an array"},
                status=400
            )
        
        if len(links) > MAX_USER_LINKS:
            return JsonResponse(
                {'error': f"Cannot query for more than {MAX_USER_LINKS} "
                 "links"}, status=400
            )

        for uuid in links:
            if not self.validate_uuid(uuid):
                return JsonResponse(
                    {'error': f"'{uuid}' is not a valid UUID"},
                    status=400
                )
        
        links = Link.objects.filter(uuid__in=links)
        for link in links:
            link.deactivate_if_expired()

        links_json = [link.to_json() for link in links]
        return JsonResponse({'links': links_json}, status=200)

    # add a new link
    def post(self, request):
        # http://stackoverflow.com/a/16203978
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
          return JsonResponse({'error': 'Could not determine IP address.'},
                              status=401)
        
        body, error = self.parse_json_body(request)
        if error is not None:
            return error
        
        # Validate that "url" key exists in JSON
        if "url" not in body:
            return JsonResponse(
                {'error': "Missing 'url' key in JSON payload"},
                status=400
            )

        # Validate the URL format
        target = body["url"]
        validator = URLValidator()
        try:
            validator(target)
        except ValidationError:
            return JsonResponse({'error': "Invalid URL format"},
                                status=400)
        
        # Validate that user has not reached max number of links
        links = Link.objects.filter(ip_added=client_ip)
        active_links = links.filter(is_active=True)
        if (active_links.count() >= MAX_USER_LINKS):
            return JsonResponse({'error': f"User has reached the maximum "
                                 "number of active links allowed "
                                 "({MAX_USER_LINKS})"})
        
        # Get a random adjective
        adjective = Adjective.objects.order_by('?')[0]
        # Get a random noun that is not already in use in combination with the
        # chosen adjective
        noun_query = f'''
            SELECT * 
            FROM shortener_noun n 
            WHERE NOT EXISTS (
                SELECT 1 
                FROM shortener_link 
                WHERE shortener_link.noun_id = n.id 
                AND shortener_link.is_active = 1 
                AND shortener_link.adjective_id = %s
            ) 
            ORDER BY RANDOM() 
            LIMIT 1;
        '''
        noun_queryset = Noun.objects.raw(noun_query, [adjective.id])
        try:
            noun = noun_queryset[0]
        except IndexError:
            return JsonResponse({'error': "Temporarily at capacity: No "
                                 "unused adjective/noun combinations are "
                                 "available. Please try again later."},
                                 status=503)
        link = Link.objects.get_or_create(adjective=adjective, noun=noun,
                                          target=target, ip_added=client_ip)[0]
        return JsonResponse(link.to_json(), status=201)
    
    # update the duration (time to live) of an existing link from its UUID
    def patch(self, request):
        body, error = self.parse_json_body(request)
        if error is not None:
            return error
        
        if "uuid" not in body:
            return JsonResponse(
                {'error': "Missing 'uuid' key in JSON payload"},
                status=400
            )
        uuid = body['uuid']

        if not self.validate_uuid(uuid):
            return JsonResponse(
                {'error': f"'{uuid}' is not a valid UUID"},
                status=400
            )
        
        if "duration" not in body:
            return JsonResponse(
                {'error': "Missing 'duration' key in JSON payload"},
                status=400
            )
        duration = body['duration']

        if not isinstance(duration, int):
            return JsonResponse(
                {'error': "'duration' key must be an integer"},
                status=400
            )

        if duration > MAX_LINK_DURATION:
            return JsonResponse(
                {'error': f"'duration' cannot be greater than "
                 f"{MAX_LINK_DURATION} hours"}, status=400
            )
        
        link = get_object_or_404(Link, uuid=uuid)
        link.duration = timedelta(hours=duration)
        link.save()
        link.deactivate_if_expired()
        return JsonResponse(link.to_json(), status=200)
    
    # delete an existing link given its UUID
    def delete(self, request):
        body, error = self.parse_json_body(request)
        if error is not None:
            return error
        
        if "uuid" not in body:
            return JsonResponse(
                {'error': "Missing 'uuid' key in JSON payload"},
                status=400
            )
        uuid = body['uuid']

        if not self.validate_uuid(uuid):
            return JsonResponse(
                {'error': f"'{uuid}' is not a valid UUID"},
                status=400
            )
        
        link = get_object_or_404(Link, uuid=uuid)
        link.delete()
        return JsonResponse({'uuid': uuid}, status=200)
