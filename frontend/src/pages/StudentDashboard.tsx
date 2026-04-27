/* eslint-disable react-hooks/set-state-in-effect */
/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import ProfileUpload from '../components/ProfileUpload';
import ExtractedProfile from '../components/ExtractedProfile';
import Flashcard from '../components/Flashcard';
import CareerInsights from '../components/CareerInsights';

interface ExtractedProfileData {
  skills: string[];
  experience_level: string;
  projects: string[];
  target_job_titles: string[];
  preferred_locations: string[];
  preferred_offer_types: string[];
  remote_ok: boolean;
  expected_salary: number | null;
}

interface RecommendationOffer {
  id: number;
  offer: number;
  offer_detail: {
    title: string;
    description: string;
    required_skills: string;
    duration_months: number | null;
    location: string | null;
    offer_type?: string;
    source_url?: string | null;
    source_platform?: string | null;
    published_date?: string | null;
    contact_email?: string | null;
    company_info?: {
      company_name: string;
    };
  };
  score_percent: number;
  missing_skills?: string[];
  recommendation_summary?: string;
  insights?: {
    semantic_score?: number;
    skill_overlap_score?: number;
    context_bonus?: number;
    preference_bonus?: number;
    matching_skills?: string[];
    missing_skills?: string[];
    score_band?: string;
  };
}

interface RecommendationsData {
  cv_uploaded: boolean;
  extracted_profile: ExtractedProfileData | null;
  career_insights: {
    profile_completion_score: number;
    strengths: string[];
    priority_skills: string[];
    target_cities: string[];
    recommended_track: string;
    action_plan: string[];
  } | null;
  recommendations_count: number;
  recommendations: RecommendationOffer[];
}

export default function StudentDashboard() {
  const [data, setData] = useState<RecommendationsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [locationFilter, setLocationFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const navigate = useNavigate();

  async function fetchRecommendations(location = '', type = '') {
    setLoading(true);
    try {
      const response = await api.get<RecommendationsData>(`/ai/recommendations/?location=${location}&type=${type}`);
      setData(response.data);
    } catch (error: unknown) {
      const status = typeof error === 'object' && error && 'response' in error
        ? (error as { response?: { status?: number } }).response?.status
        : undefined;
      if (status === 401) {
        navigate('/login');
      }
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void fetchRecommendations();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    void fetchRecommendations(locationFilter, typeFilter);
  };

  if (loading && !data) {
    return (
      <div className="flex-1 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full animate-fade-in">
      <div className="mb-10 text-center">
        <h1 className="text-3xl md:text-5xl font-heading font-extrabold mb-4">
          Trouve ton stage ideal avec l&apos;<span className="text-gradient">Intelligence Artificielle</span>
        </h1>
        <p className="text-lg text-secondary-foreground max-w-2xl mx-auto">
          Notre moteur analyse ton profil et affiche les offres les plus pertinentes avec un score lisible.
        </p>
      </div>

      {!data?.cv_uploaded ? (
        <ProfileUpload onUploadSuccess={() => void fetchRecommendations()} />
      ) : (
        <div className="flex flex-col lg:flex-row gap-8">
          <div className="w-full lg:w-1/3 flex flex-col gap-6">
            <ExtractedProfile profile={data.extracted_profile} />
            <CareerInsights insights={data.career_insights} />
            <ProfileUpload onUploadSuccess={() => void fetchRecommendations(locationFilter, typeFilter)} />
          </div>

          <div className="w-full lg:w-2/3">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
              <h2 className="text-2xl font-bold font-heading">Recommandations ({data.recommendations_count})</h2>

              <form onSubmit={handleSearch} className="flex flex-col sm:flex-row w-full md:w-auto gap-2">
                <div className="flex w-full">
                  <input
                    type="text"
                    placeholder="Ville ou Pays"
                    className="input-field rounded-r-none w-full md:w-48"
                    value={locationFilter}
                    onChange={(e) => setLocationFilter(e.target.value)}
                  />
                  <select
                    className="input-field rounded-none border-l-0 w-36 cursor-pointer bg-white"
                    value={typeFilter}
                    onChange={(e) => setTypeFilter(e.target.value)}
                  >
                    <option value="">Tous les types</option>
                    <option value="stage">Stage</option>
                    <option value="emploi">Emploi</option>
                    <option value="freelance">Freelance</option>
                  </select>
                  <button type="submit" className="bg-primary text-primary-foreground px-4 py-2 rounded-r-lg hover:bg-primary/90 transition-colors font-bold">
                    Filtrer
                  </button>
                </div>
              </form>
            </div>

            {loading ? (
              <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : data.recommendations_count > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {data.recommendations.map((offer) => (
                  <Flashcard key={offer.id} offer={offer} />
                ))}
              </div>
            ) : (
              <div className="glass p-10 text-center rounded-2xl">
                <p className="text-secondary-foreground">
                  Aucune recommandation trouvee pour le moment. Essayez un autre filtre ou rechargez votre CV.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
