/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useMemo, useState } from 'react';
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
  status: 'active' | 'paused' | 'archived';
  created_at: string;
  applications_count: number;
}

interface PaginatedResponse<T> {
  results: T[];
}

interface ReceivedApplication {
  id: number;
  status: 'pending' | 'accepted' | 'rejected' | 'withdrawn';
  applied_at: string;
  cover_letter: string | null;
  student_info: {
    user: {
      first_name: string;
      last_name: string;
      email: string;
    };
  };
  offer_info: {
    id: number;
  };
}

interface OfferFormState {
  title: string;
  description: string;
  required_skills: string;
  location: string;
  duration_months: number;
  is_paid: boolean;
  salary: number;
}

const emptyForm: OfferFormState = {
  title: '',
  description: '',
  required_skills: '',
  location: '',
  duration_months: 6,
  is_paid: false,
  salary: 0,
};

export default function MyOffers() {
  const { user } = useAuth();
  const [offers, setOffers] = useState<Offer[]>([]);
  const [selectedOffer, setSelectedOffer] = useState<Offer | null>(null);
  const [editingOffer, setEditingOffer] = useState<Offer | null>(null);
  const [applications, setApplications] = useState<ReceivedApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState<OfferFormState>(emptyForm);

  async function fetchOffers() {
    try {
      const response = await api.get<PaginatedResponse<Offer>>('/offers/my-offers/');
      setOffers(response.data.results ?? []);
    } catch (error) {
      console.error('Erreur lors du chargement des offres:', error);
    } finally {
      setLoading(false);
    }
  }

  async function fetchApplications(offerId: number) {
    try {
      const response = await api.get<PaginatedResponse<ReceivedApplication>>('/offers/received-applications/');
      const offerApplications = (response.data.results ?? []).filter(
        (application) => application.offer_info.id === offerId
      );
      setApplications(offerApplications);
    } catch (error) {
      console.error('Erreur lors du chargement des candidatures:', error);
    }
  }

  useEffect(() => {
    if (user?.role === 'company') {
      void fetchOffers();
    }
  }, [user]);

  const offerStats = useMemo(() => {
    const active = offers.filter((offer) => offer.status === 'active').length;
    const paused = offers.filter((offer) => offer.status === 'paused').length;
    const totalApplications = offers.reduce((sum, offer) => sum + (offer.applications_count ?? 0), 0);

    return { active, paused, totalApplications };
  }, [offers]);

  const handleCreateOrUpdateOffer = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const payload = {
        ...formData,
        salary: formData.is_paid ? formData.salary : null,
      };

      if (editingOffer) {
        await api.patch(`/offers/${editingOffer.id}/`, payload);
        window.alert('Offre mise a jour avec succes.');
      } else {
        await api.post('/offers/', payload);
        window.alert('Offre creee avec succes.');
      }

      setShowCreateForm(false);
      setEditingOffer(null);
      setFormData(emptyForm);
      await fetchOffers();
    } catch (error) {
      console.error("Erreur lors de la sauvegarde de l'offre:", error);
      window.alert("Erreur lors de la sauvegarde de l'offre.");
    } finally {
      setSubmitting(false);
    }
  };

  const startEditing = (offer: Offer) => {
    setEditingOffer(offer);
    setFormData({
      title: offer.title,
      description: offer.description,
      required_skills: offer.required_skills,
      location: offer.location || '',
      duration_months: offer.duration_months || 6,
      is_paid: offer.is_paid,
      salary: offer.salary || 0,
    });
    setShowCreateForm(true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDeleteOffer = async (offerId: number) => {
    if (!window.confirm('Voulez-vous vraiment supprimer cette offre definitivement ?')) return;
    try {
      await api.delete(`/offers/${offerId}/`);
      setOffers(offers.filter(o => o.id !== offerId));
      window.alert('Offre supprimee avec succes.');
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      window.alert('Erreur lors de la suppression.');
    }
  };

  const handleStatusChange = async (offerId: number, newStatus: Offer['status']) => {
    try {
      await api.patch(`/offers/${offerId}/`, {
        status: newStatus,
      });
      await fetchOffers();
    } catch (error) {
      console.error('Erreur lors de la modification du statut:', error);
    }
  };

  const handleApplicationAction = async (applicationId: number, action: 'accept' | 'reject') => {
    try {
      await api.patch(`/offers/applications/${applicationId}/status/`, {
        status: action === 'accept' ? 'accepted' : 'rejected',
      });
      if (selectedOffer) {
        await fetchApplications(selectedOffer.id);
      }
    } catch (error) {
      console.error('Erreur lors de la gestion de la candidature:', error);
    }
  };

  const getStatusColor = (status: Offer['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!user || user.role !== 'company') {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Cette page est reservee aux entreprises.</p>
      </div>
    );
  }

  if (loading) {
    return <div className="text-center py-8">Chargement de vos offres...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="glass-card rounded-2xl p-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-secondary-foreground">Espace entreprise</p>
            <h1 className="text-3xl md:text-4xl font-heading font-bold mt-2">Pilotez vos offres et candidatures</h1>
            <p className="text-secondary-foreground mt-3 max-w-2xl">
              Publiez des offres, suivez le volume de candidatures et traitez les profils entrants depuis un seul espace.
            </p>
          </div>
          <button
            onClick={() => {
              if (showCreateForm) {
                setShowCreateForm(false);
                setEditingOffer(null);
                setFormData(emptyForm);
              } else {
                setShowCreateForm(true);
              }
            }}
            className="bg-primary text-primary-foreground px-6 py-3 rounded-xl font-semibold hover:bg-primary/90 transition-colors"
          >
            {showCreateForm ? 'Fermer le formulaire' : 'Nouvelle offre'}
          </button>
        </div>

        <div className="grid sm:grid-cols-3 gap-4 mt-8">
          <div className="bg-white/70 rounded-xl p-4 border border-border">
            <p className="text-sm text-secondary-foreground">Offres actives</p>
            <p className="text-3xl font-bold mt-2">{offerStats.active}</p>
          </div>
          <div className="bg-white/70 rounded-xl p-4 border border-border">
            <p className="text-sm text-secondary-foreground">Offres en pause</p>
            <p className="text-3xl font-bold mt-2">{offerStats.paused}</p>
          </div>
          <div className="bg-white/70 rounded-xl p-4 border border-border">
            <p className="text-sm text-secondary-foreground">Candidatures recues</p>
            <p className="text-3xl font-bold mt-2">{offerStats.totalApplications}</p>
          </div>
        </div>
      </div>

      {showCreateForm ? (
        <div className="bg-white rounded-2xl shadow-md p-6">
          <h2 className="text-xl font-semibold mb-6">
            {editingOffer ? 'Modifier l\'offre' : 'Creer une nouvelle offre'}
          </h2>
          <form onSubmit={handleCreateOrUpdateOffer} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Titre du poste</label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea
                required
                rows={5}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Competences requises</label>
              <input
                type="text"
                required
                placeholder="Python, Django, REST, Git"
                value={formData.required_skills}
                onChange={(e) => setFormData({ ...formData, required_skills: e.target.value })}
                className="input-field"
              />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Lieu</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Duree (mois)</label>
                <input
                  type="number"
                  min="1"
                  max="12"
                  value={formData.duration_months}
                  onChange={(e) => setFormData({ ...formData, duration_months: Number(e.target.value) })}
                  className="input-field"
                />
              </div>
            </div>

            <label className="flex items-center gap-3 text-sm font-medium text-gray-700">
              <input
                type="checkbox"
                checked={formData.is_paid}
                onChange={(e) => setFormData({ ...formData, is_paid: e.target.checked })}
                className="h-4 w-4 rounded border-gray-300"
              />
              Stage remunere
            </label>

            {formData.is_paid ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Salaire mensuel (MAD)</label>
                <input
                  type="number"
                  min="0"
                  value={formData.salary}
                  onChange={(e) => setFormData({ ...formData, salary: Number(e.target.value) })}
                  className="input-field"
                />
              </div>
            ) : null}

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={submitting}
                className="bg-primary text-primary-foreground px-5 py-2.5 rounded-lg font-semibold hover:bg-primary/90 disabled:opacity-50"
              >
                {submitting ? 'Publication...' : editingOffer ? 'Sauvegarder les modifications' : "Publier l'offre"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingOffer(null);
                  setFormData(emptyForm);
                }}
                className="border border-border px-5 py-2.5 rounded-lg font-semibold hover:bg-secondary"
              >
                Annuler
              </button>
            </div>
          </form>
        </div>
      ) : null}

      <div className="space-y-5">
        {offers.length === 0 ? (
          <div className="glass rounded-2xl p-10 text-center">
            <h3 className="text-xl font-semibold">Aucune offre creee</h3>
            <p className="text-secondary-foreground mt-2">
              Creez votre premiere offre pour commencer a recevoir des candidatures.
            </p>
          </div>
        ) : (
          offers.map((offer) => (
            <div key={offer.id} className="bg-white rounded-2xl shadow-md p-6">
              <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-3 mb-3">
                    <h3 className="text-xl font-semibold text-gray-900">{offer.title}</h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(offer.status)}`}>
                      {offer.status === 'active' ? 'Active' : offer.status === 'paused' ? 'En pause' : 'Archivee'}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-4 text-sm text-secondary-foreground mb-4">
                    <span>Publiee le {new Date(offer.created_at).toLocaleDateString('fr-FR')}</span>
                    <span>{offer.applications_count} candidature{offer.applications_count > 1 ? 's' : ''}</span>
                    {offer.location ? <span>{offer.location}</span> : null}
                  </div>
                  <p className="text-gray-700 mb-4">{offer.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {offer.required_skills.split(',').map((skill, index) => (
                      <span key={index} className="bg-primary/10 text-primary px-2.5 py-1 rounded-full text-sm">
                        {skill.trim()}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col gap-3 min-w-[220px]">
                  <select
                    value={offer.status}
                    onChange={(e) => void handleStatusChange(offer.id, e.target.value as Offer['status'])}
                    className="input-field"
                  >
                    <option value="active">Active</option>
                    <option value="paused">En pause</option>
                    <option value="archived">Archivee</option>
                  </select>
                  <button
                    onClick={() => {
                      setSelectedOffer(offer);
                      void fetchApplications(offer.id);
                    }}
                    className="bg-emerald-600 text-white px-4 py-2.5 rounded-lg hover:bg-emerald-700 font-semibold"
                  >
                    Voir les candidatures
                  </button>
                  <div className="flex gap-2">
                    <button
                      onClick={() => startEditing(offer)}
                      className="flex-1 border border-blue-600 text-blue-600 px-4 py-2 rounded-lg hover:bg-blue-50 font-semibold"
                    >
                      Modifier
                    </button>
                    <button
                      onClick={() => handleDeleteOffer(offer.id)}
                      className="flex-1 border border-red-600 text-red-600 px-4 py-2 rounded-lg hover:bg-red-50 font-semibold"
                    >
                      Supprimer
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {selectedOffer ? (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[85vh] overflow-y-auto shadow-2xl">
            <div className="p-6 border-b border-border flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Candidatures</h2>
                <p className="text-secondary-foreground mt-1">{selectedOffer.title}</p>
              </div>
              <button
                onClick={() => setSelectedOffer(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                x
              </button>
            </div>

            <div className="p-6">
              {applications.length === 0 ? (
                <p className="text-secondary-foreground">Aucune candidature pour cette offre.</p>
              ) : (
                <div className="space-y-4">
                  {applications.map((application) => (
                    <div key={application.id} className="border border-border rounded-xl p-4">
                      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-4">
                        <div>
                          <h3 className="font-semibold text-lg">
                            {application.student_info.user.first_name} {application.student_info.user.last_name}
                          </h3>
                          <p className="text-gray-600">{application.student_info.user.email}</p>
                          <p className="text-sm text-secondary-foreground mt-1">
                            Postule le {new Date(application.applied_at).toLocaleDateString('fr-FR')}
                          </p>
                        </div>
                        <div className="flex flex-wrap items-center gap-2">
                          {application.status === 'pending' ? (
                            <>
                              <button
                                onClick={() => void handleApplicationAction(application.id, 'accept')}
                                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                              >
                                Accepter
                              </button>
                              <button
                                onClick={() => void handleApplicationAction(application.id, 'reject')}
                                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
                              >
                                Refuser
                              </button>
                            </>
                          ) : null}
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            application.status === 'accepted'
                              ? 'bg-green-100 text-green-800'
                              : application.status === 'rejected'
                                ? 'bg-red-100 text-red-800'
                                : application.status === 'withdrawn'
                                  ? 'bg-gray-100 text-gray-800'
                                  : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {application.status === 'accepted'
                              ? 'Acceptee'
                              : application.status === 'rejected'
                                ? 'Refusee'
                                : application.status === 'withdrawn'
                                  ? 'Retiree'
                                  : 'En attente'}
                          </span>
                        </div>
                      </div>

                      {application.cover_letter ? (
                        <div>
                          <h4 className="font-medium mb-2">Lettre de motivation</h4>
                          <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                            {application.cover_letter}
                          </p>
                        </div>
                      ) : null}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
