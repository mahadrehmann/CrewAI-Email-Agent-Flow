from django.core.management.base import BaseCommand, CommandError
from emailcrew.main import run_crew_and_send_mail

class Command(BaseCommand):
    help = "Download from OneDrive and send email via CrewAI"

    def add_arguments(self, parser):
        parser.add_argument(
            "--receiver", "-r",
            default="i220792@nu.edu.pk",
            help="Recipient email address"
        )
        parser.add_argument(
            "--file", "-f",
            required=True,
            help="OneDrive share‑link URL or API path"
        )

    def handle(self, *args, **options):
        receiver = options["receiver"]
        file_arg = options["file"]
        self.stdout.write(f"🚀 Running crew for {receiver} using file {file_arg}")

        try:
            # This calls your existing function
            run_crew_and_send_mail(receiver, file_arg)
            self.stdout.write(self.style.SUCCESS("✅ Email sent successfully"))
        except Exception as e:
            raise CommandError(f"❌ Crew failed: {e}")
