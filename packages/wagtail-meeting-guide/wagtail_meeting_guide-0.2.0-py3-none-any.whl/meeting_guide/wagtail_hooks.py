from django.contrib.admin import SimpleListFilter
from django.core.cache import cache

from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail.core.signals import page_published
from .models import Group, GroupContribution, MeetingType, Region, Location, Meeting


def receiver(sender, **kwargs):
    """
    Clear the API cache whenever a Location or Meeting is published.
    """
    cache.delete("wagtail_meeting_guide_api_cache")


# Register the signal receive for Location and Meeting publishes.
page_published.connect(receiver, sender=Location)
page_published.connect(receiver, sender=Meeting)


class RegionListFilter(SimpleListFilter):
    """
    This filter will always return a subset of the instances in a Model, either
    filtering by the user choice or by a default value.
    """

    title = "Regions"
    parameter_name = "region"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        list_of_regions = []
        queryset = Region.objects.filter(parent__isnull=True).order_by("name")
        for region in queryset:
            list_of_regions.append((str(region.id), region.name))
        return list_of_regions

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            return queryset.filter(parent_id=self.value())
        return queryset


class MeetingTypeAdmin(ModelAdmin):
    model = MeetingType
    menu_label = "Meeting Types"
    menu_icon = "fa-folder-open"
    add_to_settings_menu = True
    list_display = (
        "type_name",
        "intergroup_code",
        "meeting_guide_code",
        "display_order",
    )
    ordering = ("display_order", "type_name")


class RegionAdmin(ModelAdmin):
    model = Region
    menu_icon = "doc-full-inverse"
    empty_value_display = "-----"
    list_display = ("parent", "name")
    ordering = ("parent", "name")
    list_filter = (RegionListFilter,)

    def get_root_regions(self, obj):
        return Region.objects.filter(parent=None)


class GroupAdmin(ModelAdmin):
    model = Group
    menu_label = "Groups"
    menu_icon = "fa-folder-open"
    add_to_settings_menu = False
    list_display = ("name", "gso_number")
    search_fields = ("name",)


class GroupContributionAdmin(ModelAdmin):
    model = GroupContribution
    menu_label = "Contributions"
    menu_icon = "fa-folder-open"
    add_to_settings_menu = False
    list_display = ("group", "date", "amount")
    list_filter = ("group",)
    search_fields = ("group",)


class MeetingGuideAdminGroup(ModelAdminGroup):
    menu_label = "Meeting Guide"
    menu_icon = "fa-th"
    menu_order = 1000
    items = (MeetingTypeAdmin, RegionAdmin, GroupAdmin, GroupContributionAdmin)


modeladmin_register(MeetingGuideAdminGroup)
