from django.core.management.base import BaseCommand

from ai.services import NLPService
from offers.scraper import fetch_moroccan_internships


class Command(BaseCommand):
    help = "Scrape les offres de stage marocaines puis recalcule les recommandations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-refresh",
            action="store_true",
            help="N'actualise pas les recommandations etudiantes apres le scraping.",
        )

    def handle(self, *args, **options):
        stats = fetch_moroccan_internships()
        self.stdout.write(
            self.style.SUCCESS(
                f"Scraping termine: {stats['created']} creees, "
                f"{stats['updated']} mises a jour, {stats['skipped']} ignorees."
            )
        )

        if options["skip_refresh"]:
            self.stdout.write("Recalcul des recommandations ignore.")
            return

        stats = NLPService().refresh_all_students()
        self.stdout.write(
            self.style.SUCCESS(
                "Recommandations mises a jour: "
                f"{stats['students_processed']} etudiants, "
                f"{stats['recommendations_updated']} scores recalcules."
            )
        )
