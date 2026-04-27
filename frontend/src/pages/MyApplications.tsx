/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface Application {
  id: number;
  status: 'pending' | 'accepted' | 'rejected' | 'withdrawn';
  applied_at: string;
  cover_letter: string | null;
  offer_info: {
    id: number;
    title: string;
    location: string | null;
    is_paid: boolean;
    salary: number | null;
    company_info: {
      company_name: string;
    };
  };
}

interface PaginatedApplicationsResponse {
  results: Application[];
}

const MyApplications = () => {
  const { user } = useAuth();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  async function fetchApplications() {
    try {
      const response = await api.get<PaginatedApplicationsResponse>('/offers/my-applications/');
      setApplications(response.data.results ?? []);
    } catch (error) {
      console.error('Erreur lors du chargement des candidatures:', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (user?.role === 'student') {
      void fetchApplications();
    }
  }, [user]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'accepted':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'withdrawn':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending':
        return 'En attente';
      case 'accepted':
        return 'Acceptee';
      case 'rejected':
        return 'Refusee';
      case 'withdrawn':
        return 'Retiree';
      default:
        return status;
    }
  };

  const handleWithdraw = async (applicationId: number) => {
    if (!window.confirm('Etes-vous sur de vouloir retirer cette candidature ?')) return;

    try {
      await api.patch(`/offers/applications/${applicationId}/withdraw/`);
      window.alert('Candidature retiree avec succes.');
      await fetchApplications();
    } catch (error) {
      console.error('Erreur lors du retrait de la candidature:', error);
      window.alert('Erreur lors du retrait de la candidature.');
    }
  };

  if (!user || user.role !== 'student') {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Cette page est reservee aux etudiants.</p>
      </div>
    );
  }

  if (loading) {
    return <div className="text-center py-8">Chargement de vos candidatures...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Mes Candidatures</h1>

      {applications.length === 0 ? (
        <div className="text-center py-12">
          <div className="bg-gray-50 rounded-lg p-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Aucune candidature
            </h3>
            <p className="text-gray-600 mb-4">
              Vous n&apos;avez pas encore postule a des offres de stage.
            </p>
            <Link
              to="/offers"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 inline-block"
            >
              Decouvrir les offres
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {applications.map((application) => (
            <div key={application.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4 gap-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {application.offer_info.title}
                  </h3>
                  <p className="text-blue-600 font-medium mb-2">
                    {application.offer_info.company_info.company_name}
                  </p>
                  <div className="flex items-center text-sm text-gray-600 space-x-4 mb-4 flex-wrap">
                    <span>{application.offer_info.location || 'Non specifie'}</span>
                    {application.offer_info.is_paid && application.offer_info.salary ? (
                      <span>{application.offer_info.salary} MAD/mois</span>
                    ) : null}
                    <span>Postule le {new Date(application.applied_at).toLocaleDateString('fr-FR')}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(application.status)}`}>
                    {getStatusLabel(application.status)}
                  </span>
                  {application.status === 'pending' ? (
                    <button
                      onClick={() => void handleWithdraw(application.id)}
                      className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 text-sm"
                    >
                      Retirer
                    </button>
                  ) : null}
                </div>
              </div>

              {application.cover_letter ? (
                <div className="border-t pt-4">
                  <h4 className="font-medium text-gray-900 mb-2">Lettre de motivation :</h4>
                  <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                    {application.cover_letter}
                  </p>
                </div>
              ) : null}

              <div className="mt-4 text-sm text-gray-500">
                ID de candidature: #{application.id}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyApplications;
