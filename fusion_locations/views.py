# from django.core.urlresolvers import reverse
import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .fusion_tables import clear_fusion_table
from .models import GoogleMapLocation, GoogleFusionTable
from .utils import get_google_api_key


def clear_fusion_table_view(request):
    """ Simple functional view for clearing data out of the fusion table"""
    clear_fusion_table()

    # empty local location data
    GoogleMapLocation.objects.all().delete()

    return HttpResponse('ok')


class GoogleFusionTableMapView(TemplateView):
    template_name = 'fusion_locations/spa.html'

    def get_context_data(self, **kwargs):
        context = super(GoogleFusionTableMapView, self).get_context_data(**kwargs)
        api_key = get_google_api_key()
        context['GOOGLE_API_KEY'] = api_key

        fusion_table = GoogleFusionTable.objects.get_fusion_table()
        context['google_fusion_table'] = fusion_table.table_id

        return context


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class GoogleMapLocationCreate(AjaxableResponseMixin, CreateView):
    """ Simple model create CBV for local map locations """
    model = GoogleMapLocation
    fields = ['lat', 'lng', 'address', ]

    def get_success_url(self):
        """ required by CBV limitations, but not used """
        return reverse('save-map-location')
