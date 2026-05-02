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
        parser.add_argument(
            "--no-ai",
            action="store_true",
            help="Pas d'appel Gemini sur le scraper (competences via heuristique NLP seule).",
        )
        parser.add_argument(
            "--ai-chunk-size",
            type=int,
            default=None,
            help="Offres par requete Gemini (defaut: env GEMINI_SCRAPER_CHUNK ou 8, max 12).",
        )

    def handle(self, *args, **options):
        chunk = options["ai_chunk_size"]
        if chunk is not None:
            chunk = max(2, min(chunk, 12))
        stats = fetch_moroccan_internships(
            use_scraper_ai=not options["no_ai"],
            scraper_ai_chunk_size=chunk,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Scraping termine: {stats['created']} creees, "
                f"{stats['updated']} mises a jour, {stats['skipped']} ignorees."
            )
        )
        if not options["no_ai"]:
            self.stdout.write(
                f"  IA scraper: {stats.get('ai_batches', 0)} lots Gemini, "
                f"{stats.get('offers_ai_enriched', 0)} offres enrichies IA, "
                f"{stats.get('offers_heuristic_only', 0)} heuristique seule, "
                f"{stats.get('ai_chunks_failed', 0)} lots en echec."
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
