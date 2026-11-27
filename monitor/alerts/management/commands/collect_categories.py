from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from alerts.models import Campaign, Deal
from alerts.category_import import candidates
from alerts.live_fetch import fetch_category

class Command(BaseCommand):
    help = "Collect saved, authorized category sources for active campaigns once."

    def handle(self, *args, **options):
        today = timezone.localdate()
        failed = 0
        for campaign in Campaign.objects.filter(enabled=True, starts_on__lte=today, ends_on__gte=today).order_by("pk").iterator():
            if not campaign.category_source:
                continue
            try:
                data = dict(campaign.category_source)
                data["html"] = fetch_category(data["listing_url"])
                rows = list(candidates(data))
                with transaction.atomic():
                    for row in rows:
                        Deal.objects.update_or_create(campaign=campaign, url=row["url"], defaults={**row, "observed_at": timezone.now()})
                self.stdout.write(f"Campaign {campaign.pk}: {len(rows)} observations")
            except Exception:
                failed += 1
                self.stderr.write(f"Campaign {campaign.pk}: collection failed")
        if failed:
            raise CommandError(f"{failed} campaign collections failed")
