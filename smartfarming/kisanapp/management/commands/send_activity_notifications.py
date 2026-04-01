from django.core.management.base import BaseCommand
from django.utils import timezone
from kisanapp.models import CropActivity, Notification


class Command(BaseCommand):
    help = "Send notifications for today's and tomorrow's crop activities"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        tomorrow = today + timezone.timedelta(days=1)

        # Activities due today or tomorrow that are still pending
        activities = CropActivity.objects.filter(
            status="pending",
            due_date__in=[today, tomorrow],
        ).select_related("farmer", "land")

        count = 0
        for activity in activities:
            # Avoid duplicate notifications for same activity on same day
            already_notified = Notification.objects.filter(
                farmer=activity.farmer,
                land=activity.land,
                crop_name=activity.crop_name,
                title=activity.title,
                created_at__date=today,
            ).exists()

            if already_notified:
                continue

            due_label = "Aaj" if activity.due_date == today else "Kal"

            Notification.objects.create(
                farmer=activity.farmer,
                land=activity.land,
                crop_name=activity.crop_name,
                notif_type=activity.activity_type,
                title=f"⏰ {due_label}: {activity.title}",
                message=f"{activity.land.land_name} – {activity.crop_name}: {activity.message}",
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} notifications sent."))
