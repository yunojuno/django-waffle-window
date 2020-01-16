from __future__ import annotations

import logging
from typing import Any

from django.core.management.base import BaseCommand
from waffle.models import Flag

from ...models import sync_flag_membership as sync

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Syncs flag membership for all waffle flags."

    def handle(self, *args: Any, **options: Any) -> None:
        flags = Flag.objects.all()
        logger.info("Syncing %i flags", flags.count())
        for flag in flags:
            members = sync(flag)
            logger.info("Flag '%s' has %i active members.", flag.name, members)
