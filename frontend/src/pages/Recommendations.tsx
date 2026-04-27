/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface RecommendationItem {
  id: number;
  score: number;
  score_percent: number;
  matching_skills: string[];
  missing_skills: string[];
  recommendation_summary: string;
  offer_detail: {
    id: number;
    title: string;
    description: string;
    required_skills: string;
    offer_type: string;
    location: string | null;
    duration_months: number | null;
    is_paid: boolean;
    salary: number | null;
    source_url?: string | null;
    source_platform?: string | null;
    published_date?: string | null;
    company_info: {
      company_name: string;
      city: string | null;
    };
  };
}

interface RecommendationsResponse {
  cv_uploaded: boolean;
  recommendations: RecommendationItem[];
  recommendations_count?: number;
  extracted_profile?: {
    skills: string[];
    experience_level: string;
    projects: string[];
  };
}

const Recommendations = () => {
  const { user } = useAuth();
  const [data, setData] = useState<RecommendationsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  async function fetchRecommendations() {
    try {
      const response = await api.get('/ai/recommendations/');
      setData(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des recommandations:', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (user?.role === 'student') {
      void fetchRecommendations();
    }
  }, [user]);

  const handleApply = async (offerId: number) => {
    try {
      await api.post(`/offers/${offerId}/apply/`, {});
      await fetchRecommendations();
      window.alert('Candidature envoyee avec succes.');
    } catch (error) {
      console.error('Erreur lors de la candidature:', error);
      window.alert("Erreur lors de l'envoi de la candidature.");
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.8) return 'Excellent match';
    if (score >= 0.6) return 'Bon match';
    return 'Match possible';
  };

  if (!user || user.role !== 'student') {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Cette page est reservee aux etudiants.</p>
      </div>
    );
  }

  if (loading) {
    return <div className="text-center py-8">Chargement des recommandations...</div>;
  }

  if (!data?.cv_uploaded) {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-yellow-800 mb-4">
            CV requis pour les recommandations
          </h2>
          <p className="text-yellow-700 mb-6">
            Uploadez votre CV pour que l&apos;IA puisse analyser votre profil et proposer les offres les plus pertinentes.
          </p>
          <Link
            to="/profile"
            className="bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700 inline-block"
          >
            Completer mon profil
          </Link>
        </div>
      </div>
    );
  }

  const recommendations = data.recommendations ?? [];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Recommandations IA
        </h1>
        <p className="text-gray-600">
          Decouvrez les offres qui correspondent le mieux a votre profil.
        </p>
      </div>

      {data.extracted_profile ? (
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 mb-8">
          <div className="flex flex-wrap items-center gap-3 mb-3">
            <h2 className="text-lg font-semibold text-slate-900">Profil detecte</h2>
            <span className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
              {data.extracted_profile.experience_level}
            </span>
            <span className="text-sm bg-slate-200 text-slate-700 px-3 py-1 rounded-full">
              {recommendations.length} offre(s) pertinentes
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {data.extracted_profile.skills.slice(0, 8).map((skill) => (
              <span
                key={skill}
                className="bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full text-sm"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {recommendations.length === 0 ? (
        <div className="text-center py-12">
          <div className="bg-gray-50 rounded-lg p-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Aucune recommandation disponible
            </h3>
            <p className="text-gray-600">
              L&apos;IA n&apos;a pas encore trouve de correspondance avec les offres actives.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {recommendations.map((rec) => (
            <div key={rec.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4 gap-4">
                <div className="flex-1">
                  <div className="flex items-center flex-wrap gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">
                      {rec.offer_detail.title}
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(rec.score)}`}>
                      {getScoreLabel(rec.score)} ({rec.score_percent.toFixed(0)}%)
                    </span>
                    <span className="px-3 py-1 rounded-full text-sm font-medium bg-slate-100 text-slate-700">
                      {rec.offer_detail.offer_type}
                    </span>
                  </div>
                  <p className="text-blue-600 font-medium mb-2">
                    {rec.offer_detail.company_info.company_name}
                  </p>
                  <div className="flex items-center text-sm text-gray-600 space-x-4 mb-4 flex-wrap">
                    <span>{rec.offer_detail.location || rec.offer_detail.company_info.city || 'Non specifie'}</span>
                    {rec.offer_detail.duration_months ? <span>{rec.offer_detail.duration_months} mois</span> : null}
                    {rec.offer_detail.is_paid && rec.offer_detail.salary ? <span>{rec.offer_detail.salary} MAD/mois</span> : null}
                    {rec.offer_detail.source_platform ? <span>Source: {rec.offer_detail.source_platform}</span> : null}
                  </div>
                  <p className="text-gray-700 mb-4">{rec.recommendation_summary}</p>
                  <p className="text-gray-600 mb-4">{rec.offer_detail.description}</p>
                </div>
                <button
                  onClick={() => void handleApply(rec.offer_detail.id)}
                  className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
                >
                  Postuler
                </button>
              </div>

              <div className="border-t pt-4 space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Competences requises :</h4>
                  <div className="flex flex-wrap gap-2">
                    {rec.offer_detail.required_skills.split(',').map((skill, index) => (
                      <span
                        key={index}
                        className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm"
                      >
                        {skill.trim()}
                      </span>
                    ))}
                  </div>
                </div>

                {rec.matching_skills.length > 0 ? (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Vos points forts :</h4>
                    <div className="flex flex-wrap gap-2">
                      {rec.matching_skills.map((skill) => (
                        <span
                          key={skill}
                          className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null}

                {rec.missing_skills.length > 0 ? (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">A renforcer :</h4>
                    <div className="flex flex-wrap gap-2">
                      {rec.missing_skills.map((skill) => (
                        <span
                          key={skill}
                          className="bg-amber-100 text-amber-800 px-2 py-1 rounded-full text-sm"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null}

                {rec.offer_detail.source_url ? (
                  <div>
                    <a
                      href={rec.offer_detail.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm font-medium text-blue-600 hover:text-blue-700"
                    >
                      Voir l&apos;offre source
                    </a>
                  </div>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Recommendations;
