import datetime
import json
import re

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from django_weasyprint import WeasyTemplateResponseMixin

from .models import Meeting, MeetingType, Region
from .utils import get_region_tree


@method_decorator(
    cache_page(3600 * 24 * 7, key_prefix="wagtail_meeting_guide_api_cache"),
    name='dispatch',
)
class MeetingsBaseView(TemplateView):
    DAY_OF_WEEK = (
        (0, "Sunday"),
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
    )

    def get_meetings(self):
        return (
            Meeting.objects.live().filter(status=1)
            .select_related("meeting_location", "group")
            .prefetch_related(
                "meeting_location__region",
                # 'types',  # ParentalManyToManyField instead of ManyToManyField causes Django to throw up on this
            )
            .order_by("day_of_week", "start_time")
        )


class MeetingsReactJSView(TemplateView):
    """
    List all meetings in the Meeting Guide ReactJS plugin.
    """

    template_name = "meeting_guide/meetings_list_react.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "mapbox_key"
        ] = "pk.eyJ1IjoiZmxpcHBlcnBhIiwiYSI6ImNqcHZhbjZwdDBldDA0MXBveTlrZG9uaGIifQ.WpB5eRUcUnQh0-P_CX3nKg"  # noqa
        return context


class MeetingsDataTablesView(MeetingsBaseView):
    """
    List all meetings in a jQuery datatable.
    """

    template_name = "meeting_guide/meetings_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meetings"] = self.get_meetings()

        return context


class MeetingsPrintView(TemplateView):
    """
    List all meetings in an HTML printable format.
    """

    template_name = "meeting_guide/meetings_list_print.html"

    def get_meetings(self):
        return (
            Meeting.objects.live().select_related(
                "meeting_location__region__parent", "group",
            ).filter(status=1)
            .order_by(
                "day_of_week",
                "meeting_location__region__parent__name",
                "meeting_location__postal_code",
                "start_time",
            )
        )  # [0:10]

    def get_context_data(self, **kwargs):
        meetings = self.get_meetings()
        meeting_dict = {}

        slice_address = re.compile(r"(.*), PA [0-9]+, USA")

        for m in meetings:
            day = m.get_day_of_week_display()
            region = m.meeting_location.region.parent.name
            postal_code = m.meeting_location.postal_code
            types = list(m.types.values_list("intergroup_code", flat=True))

            if None in types:
                print(m.types.values_list("meeting_guide_code", flat=True))

            if region not in meeting_dict:
                meeting_dict[region] = {}
            if day not in meeting_dict[region]:
                meeting_dict[region][day] = {}
            if postal_code not in meeting_dict[region][day]:
                meeting_dict[region][day][postal_code] = []

            group_address = re.match(
                slice_address, m.meeting_location.formatted_address
            )

            if group_address:
                formatted_address = group_address.group(1).split(",")[0]
            else:
                formatted_address = m.meeting_location.formatted_address

            meeting_dict[region][day][postal_code].append(
                {
                    "name": m.title,
                    "time_formatted": f"{m.start_time:%I:%M%p}",
                    "day": day,
                    "types": types,
                    "location": m.meeting_location.title,
                    "formatted_address": formatted_address,
                    "group": getattr(m.group, "name", None),
                    "district": m.district,
                    "gso_number": getattr(m.group, "gso_number", None),
                    "meeting_details": m.details,
                    "location_details": m.meeting_location.details,
                }
            )

        context = super().get_context_data(**kwargs)
        context["meetings"] = meeting_dict
        context["meeting_types"] = (
            MeetingType.objects.values("type_name", "intergroup_code")
            .filter(intergroup_code__isnull=False)
            .order_by("display_order", "intergroup_code")
        )

        return context


class MeetingsPrintDownloadView(WeasyTemplateResponseMixin, MeetingsPrintView):
    """
    Provide a PDF download of all active meetings, sourcing
    the HTML printable format.

    SEPIA WIDTH: 3.75" x 5.5" papersize (0.25" margin)
    """

    from django.contrib.staticfiles import finders

    meeting_guide_css_file = finders.find("meeting_guide/print.css")

    pdf_stylesheets = [meeting_guide_css_file]
    pdf_presentational_hints = True


class MeetingsAPIView(MeetingsBaseView):
    """
    Return a JSON response of the meeting list.
    """

    def get(self, request, *args, **kwargs):
        url = f"""{request.META["wsgi.url_scheme"]}://{request.META["SERVER_NAME"]}"""

        meetings = self.get_meetings()
        meetings_dict = []

        # Eager load all regions to reference below.
        regions = Region.objects.all().prefetch_related("children")

        for meeting in meetings:
            district = meeting.district
            if len(district):
                district = f"D{district}"

            gso_number = getattr(meeting.group, "gso_number", "")
            if len(gso_number):
                gso_number = f" / GSO #{gso_number}"

            group_info = f"{district}{gso_number}"

            location = (
                f"{meeting.meeting_location.title}, "
                f"{meeting.meeting_location.region.name}"
            )
            if len(group_info):
                location = f"{location} ({group_info})"

            region_ancestors = list(
                regions.get(id=meeting.meeting_location.region.id)
                .get_ancestors(include_self=True)
                .values_list("name", flat=True)
            )

            meetings_dict.append(
                {
                    "id": meeting.id,
                    "name": meeting.title,
                    "slug": meeting.slug,
                    "notes": meeting.details,
                    "updated": f"{meeting.last_published_at if meeting.last_published_at else datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
                    "location_id": meeting.meeting_location.id,
                    "url": f"{url}{meeting.url_path}",
                    "time": f"{meeting.start_time:%H:%M}",
                    "end_time": f"{meeting.end_time:%H:%M}",
                    "time_formatted": f"{meeting.start_time:%H:%M %P}",
                    "distance": "",
                    "day": str(meeting.day_of_week),
                    "types": list(
                        meeting.types.values_list("meeting_guide_code", flat=True)
                    ),
                    "location": location,
                    "location_notes": "",
                    "location_url": f"{url}{meeting.meeting_location.url_path}",
                    "formatted_address": meeting.meeting_location.formatted_address,
                    "latitude": str(meeting.meeting_location.lat),
                    "longitude": str(meeting.meeting_location.lng),
                    "region_id": meeting.meeting_location.region.id,
                    # "region": f"{meeting.meeting_location.region.parent.name}: {meeting.meeting_location.region.name}",
                    "region": f"{meeting.meeting_location.region.parent.name}",  # Let's try with just parent region
                    "regions": region_ancestors,
                    "group": group_info,
                    "image": "",
                }
            )

        if settings.DEBUG:
            meetings_dict = json.dumps(meetings_dict, indent=4)
        else:
            meetings_dict = json.dumps(meetings_dict)

        return HttpResponse(meetings_dict, content_type="application/json")


class RegionAPIView(MeetingsBaseView):
    """
    Return a JSON response of the meeting list.
    """

    def get(self, request, *args, **kwargs):
        tree = get_region_tree()
        return HttpResponse(json.dumps(tree), content_type="application/json")


from django.views.generic.edit import UpdateView

from .models import Location


class LocationUpdate(UpdateView):
    model = Location
    fields = ["title", "address1", "address2", "city", "state", "postal_code"]
