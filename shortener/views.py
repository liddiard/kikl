from datetime import timedelta

from django.http import JsonResponse, HttpResponseNotFound
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.generic.base import View, TemplateView
from django.middleware.csrf import get_token
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie

from ipware import get_client_ip

from .models import Adjective, Noun, Link
from .mixins import ValidationMixin


# maximum number of links per user
MAX_USER_LINKS = 10
# maximum duration of a link (hours)
MAX_LINK_DURATION = 24 * 7 # 1 week

# pages

class FrontPageView(TemplateView):
    
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get absolute URI for Open Graph tags
        context['page_uri'] = self.request.build_absolute_uri()
        return context


# redirect to link
def target_view(request, adjective, noun):
    a = get_object_or_404(Adjective, word=adjective)
    n = get_object_or_404(Noun, word=noun)
    link = get_object_or_404(Link, is_active=True, adjective=a, noun=n)
    link.update_is_active()
    if link.is_active:
        return redirect(link.target)
    else:
        return HttpResponseNotFound()


# API

@ensure_csrf_cookie
def set_csrf_token(request):
    """
    Sets the CSRF cookie for the current user session and returns a JSON
    response with a success message.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response with a success message indicating that
        the CSRF cookie has been set.
    """
    return JsonResponse({'message': "CSRF cookie set"})


class LinkView(ValidationMixin, View):

    def get(self, request):
        """
        A method that retrieves an array of links' metadata based on the
        provided UUIDs.
        
        Parameters:
            request (HttpRequest): The HTTP request object containing an array
            of UUIDs.
            
        Returns:
            JsonResponse: A JSON response containing the metadata of the
            requested links.
        """
        uuids = request.GET.get('uuids')
        
        if uuids is None:
            return JsonResponse(
                {'error': "Missing 'links' key in query params"},
                status=400
            )

        uuids = uuids.split(',')
        
        if len(uuids) > MAX_USER_LINKS:
            return JsonResponse(
                {'error': f"Cannot query for more than {MAX_USER_LINKS} "
                 "links"}, status=400
            )

        for uuid in uuids:
            if not self.validate_uuid(uuid):
                return JsonResponse(
                    {'error': f"'{uuid}' is not a valid UUID"},
                    status=400
                )
        
        links = Link.objects.filter(uuid__in=uuids).order_by('-time_added')
        for link in links:
            link.update_is_active()

        links_json = [link.to_json() for link in links]
        return JsonResponse({'links': links_json}, status=200)

    # add a new link
    def post(self, request):
        """
        Create a new link for the user with this IP.

        This function handles the HTTP POST request to create a new link for
        the current user. It expects a JSON payload with a "target" key
        containing the target URL. The function validates the URL format,
        checks if the user has reached the maximum number of active links
        allowed, and picks a random adjective and noun combination that is
        not already in use. If successful, it creates a new Link object and
        returns a JSON response with the created link's metadata.

        Parameters:
            request (HttpRequest): The HTTP request object containing a target URL.

        Returns:
            JsonResponse: A JSON response containing the metadata of the created link.

        Raises:
            ValidationError: If the URL format is invalid.
            IndexError: If there are no unused adjective/noun combinations available.
        """
        # http://stackoverflow.com/a/16203978
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
          return JsonResponse({'error': 'Missing IP address from request'},
                              status=401)
        
        body, error = self.parse_json_body(request)
        if error is not None:
            return error
        
        # Validate that "url" key exists in JSON
        if "target" not in body:
            return JsonResponse(
                {'error': "Missing 'target' key in JSON payload"},
                status=400
            )

        # Validate the URL format
        target = body["target"]
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
            return JsonResponse({'error': f"You have reached the maximum "
                                 f"limit of {MAX_USER_LINKS} links."},
                                 status=400)
        
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
            return JsonResponse({'error': "Temporarily at capacity. No "
                                 "unused adjective/noun combinations are "
                                 "available. Please try again later."},
                                 status=503)
        link = Link.objects.get_or_create(adjective=adjective, noun=noun,
                                          target=target, ip_added=client_ip)[0]
        return JsonResponse(link.to_json(), status=201)
    
    # update the duration (time to live) of an existing link from its UUID
    def patch(self, request):
        """
        Updates the duration of a link identified by its UUID.

        Parameters:
            request (HttpRequest): The HTTP request object containing a UUID.

        Returns:
            JsonResponse: The JSON response containing the updated link data
            or an error message.

        Raises:
            Http404: If the link with the given UUID is not found.
        """
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

        if duration > MAX_LINK_DURATION or duration < 1:
            return JsonResponse(
                {'error': f"'duration' cannot be greater than "
                 f"{MAX_LINK_DURATION} or less than 1 hour"}, status=400
            )

        link = get_object_or_404(Link, uuid=uuid)
        link.update_is_active()
        if not link.is_active:
            return JsonResponse(
                {'error': "Link is has expired"}, status=400
            )

        link.duration = timedelta(hours=duration)
        link.save()
        link.update_is_active()
        return JsonResponse(link.to_json(), status=200)
    
    # delete an existing link given its UUID
    def delete(self, request):
        """
        Delete an existing link based on the provided UUID.

        Parameters:
            request (HttpRequest): The HTTP request object containing a UUID.

        Returns:
            - JsonResponse: JSON response indicating the success or failure of
            the deletion operation
        """
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
