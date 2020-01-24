from __future__ import annotations

import datetime
import logging
from typing import Any, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.utils.functional import cached_property
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy
from waffle.models import Flag

logger = logging.getLogger(__name__)


def get_or_create_flag_group(flag_name: str) -> Group:
    flag = Flag.objects.get(name=flag_name)
    group, _ = Group.objects.get_or_create(name=f"WAFFLE_{flag_name}")
    flag.groups.add(group)
    return group


def sync_flag_membership(flag_name: str) -> int:
    """
    Update the flag group with all members of the queryset.

    Returns the number of members added to the Flag.
    """
    active_members = FlagMember.objects.filter(flag__name=flag_name).active()
    active_members_count = active_members.count()
    if active_members_count > 1000:
        logger.warning(
            "Attempting to sync flag group with %i members.", active_members_count
        )
    group = get_or_create_flag_group(flag_name)
    group.user_set.clear()
    group.user_set.add(  # this won't scale for large querysets
        *[m.user for m in active_members]
    )
    return active_members_count


class FlagMemberQuerySet(models.query.QuerySet):
    def active(self) -> FlagMemberQuerySet:
        """Fetch all members that are live today."""
        today = datetime.date.today()
        return self.filter(start_date__lte=today, end_date__gte=today)


class FlagMember(models.Model):

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="flags",
        help_text=_lazy("User to add to waffle flag group."),
    )
    flag = models.ForeignKey(
        Flag,
        on_delete=models.CASCADE,
        related_name="members",
        help_text=_lazy("Waffle flag to add the user to."),
    )
    start_date = models.DateField(
        help_text=_lazy("Date on which to add user to Flag group.")
    )
    end_date = models.DateField(
        help_text=_lazy("Date on which to remove user from Flag group.")
    )
    created_at = models.DateTimeField()

    objects = FlagMemberQuerySet.as_manager()

    def __repr__(self) -> str:
        return (
            f"<FlagMember user={self.user.pk} flag='{self.flag_name}' "
            f"start_date='{self.start_date}' end_date='{self.end_date}'>"
        )

    def save(self, *args: Any, **kwargs: Any) -> FlagMember:
        self.created_at = self.created_at or tz_now()
        super().save(*args, **kwargs)
        return self

    @cached_property
    def flag_name(self) -> str:
        return self.flag.name

    @cached_property
    def group(self) -> Group:
        # get_or_create returns (group, created) tuple - we only want the group obj.
        return Group.objects.get_or_create(name=self.group_name)[0]

    @property
    def group_name(self) -> str:
        return f"WAFFLE_{self.flag_name}"

    @property
    def window(self) -> str:
        return f"{self.start_date} to {self.end_date}"

    @property
    def is_active(self) -> Optional[bool]:
        """Return True if today is in the active window."""
        if not self.start_date:
            return None
        if not self.end_date:
            return None
        return self.start_date <= datetime.date.today() <= self.end_date

    def sync(self) -> bool:
        """
        Add or remove user from group, as appropriate.

        Returns True if the user was added to the group, else False.

        """
        if self.is_active:
            self.group.user_set.add(self.user)
            return True
        self.group.user_set.remove(self.user)
        return False
