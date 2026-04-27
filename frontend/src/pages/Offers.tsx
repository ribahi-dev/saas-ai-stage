/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface Offer {
  id: number;
  title: string;
  description: string;
  required_skills: string;
  location: string | null;
  duration_months: number | null;
  is_paid: boolean;
  salary: number | null;
  company_info: {
    company_name: string;
    city: string | null;
    industry: string | null;
  };
  created_at: string;
}

interface PaginatedOffersResponse {
  results: Offer[];
}

const Offers = () => {
  const { user } = useAuth();
  const [offers, setOffers] = useState<Offer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [locationFilter, setLocationFilter] = useState('');

  async function fetchOffers() {
    try {
      const response = await api.get<PaginatedOffersResponse>('/offers/');
      setOffers(response.data.results ?? []);
    } catch (error) {
      console.error('Erreur lors du chargement des offres:', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void fetchOffers();
  }, []);

  const filteredOffers = offers
    .filter((offer) =>
      offer.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      offer.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      offer.required_skills.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .filter((offer) =>
      !locationFilter ||
      (offer.location ?? offer.company_info.city ?? '').toLowerCase().includes(locationFilter.toLowerCase())
    );

  const handleApply = async (offerId: number) => {
    if (!user || user.role !== 'student') return;

    try {
      await api.post(`/offers/${offerId}/apply/`, {});
      window.alert('Candidature envoyee avec succes.');
    } catch (error) {
      console.error('Erreur lors de la candidature:', error);
      window.alert("Erreur lors de l'envoi de la candidature.");
    }
  };

  if (loading) {
    return <div className="text-center py-8">Chargement des offres...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Offres de Stage</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Rechercher
            </label>
            <input
              type="text"
              placeholder="Titre, description, competences..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lieu
            </label>
            <input
              type="text"
              placeholder="Ville ou region"
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {filteredOffers.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Aucune offre trouvee
          </div>
        ) : (
          filteredOffers.map((offer) => (
            <div key={offer.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4 gap-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {offer.title}
                  </h3>
                  <p className="text-blue-600 font-medium mb-2">
                    {offer.company_info.company_name}
                  </p>
                  <div className="flex items-center text-sm text-gray-600 space-x-4 flex-wrap">
                    <span>{offer.location || offer.company_info.city || 'Non specifie'}</span>
                    {offer.duration_months ? <span>{offer.duration_months} mois</span> : null}
                    {offer.is_paid && offer.salary ? <span>{offer.salary} MAD/mois</span> : null}
                  </div>
                </div>
                <button
                  onClick={() => void handleApply(offer.id)}
                  disabled={!user || user.role !== 'student'}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {user?.role === 'student' ? 'Postuler' : 'Connexion requise'}
                </button>
              </div>

              <p className="text-gray-700 mb-4">{offer.description}</p>

              <div className="border-t pt-4">
                <h4 className="font-medium text-gray-900 mb-2">Competences requises :</h4>
                <div className="flex flex-wrap gap-2">
                  {offer.required_skills.split(',').map((skill, index) => (
                    <span
                      key={index}
                      className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm"
                    >
                      {skill.trim()}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Offers;
