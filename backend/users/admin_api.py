from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.management import call_command
from users.models import User, StudentProfile, CompanyProfile
from offers.models import InternshipOffer, Application
from users.permissions import IsAdminUserRole
import threading

class AdminStatsView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        stats = {
            'total_students': StudentProfile.objects.count(),
            'total_companies': CompanyProfile.objects.count(),
            'total_offers': InternshipOffer.objects.count(),
            'active_offers': InternshipOffer.objects.filter(status='open').count(),
            'total_applications': Application.objects.count(),
        }
        return Response(stats, status=status.HTTP_200_OK)


class AdminUserListView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'date_joined': user.date_joined,
                'is_active': user.is_active,
            })
        return Response(data, status=status.HTTP_200_OK)


class AdminUserDeleteView(APIView):
    permission_classes = [IsAdminUserRole]

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            # Empêcher l'administrateur de se supprimer lui-même
            if user == request.user:
                return Response({"error": "Vous ne pouvez pas supprimer votre propre compte."}, status=status.HTTP_400_BAD_REQUEST)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AdminTriggerScrapeView(APIView):
    permission_classes = [IsAdminUserRole]

    def post(self, request):
        # Lancer le scraping en asynchrone pour ne pas bloquer l'API
        def run_scrape():
            call_command('scrape_morocco_offers')

        thread = threading.Thread(target=run_scrape)
        thread.start()

        return Response({"message": "Scraping démarré en arrière-plan."}, status=status.HTTP_202_ACCEPTED)

class AdminOfferListView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        offers = InternshipOffer.objects.select_related('company__user').all().order_by('-created_at')
        data = []
        for offer in offers:
            company_name = offer.company.company_name if offer.company else 'Scrapée / Inconnue'
            data.append({
                'id': offer.id,
                'title': offer.title,
                'company_name': company_name,
                'status': offer.status,
                'created_at': offer.created_at,
            })
        return Response(data, status=status.HTTP_200_OK)


class AdminOfferDeleteView(APIView):
    permission_classes = [IsAdminUserRole]

    def delete(self, request, pk):
        try:
            offer = InternshipOffer.objects.get(pk=pk)
            offer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except InternshipOffer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
