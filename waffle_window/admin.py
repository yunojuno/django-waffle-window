from django.contrib import admin

from .models import FlagMember


class FlagMemberAdmin(admin.ModelAdmin):

    list_display = ("user", "flag", "start_date", "end_date", "is_active")
    readonly_fields = ("created_at",)
    raw_id_fields = ("user", "flag")


admin.site.register(FlagMember, FlagMemberAdmin)
