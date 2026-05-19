import { useState } from 'react';
import { MapPinIcon, ClockIcon, ArrowTopRightOnSquareIcon, CalendarDaysIcon, GlobeAltIcon, DocumentTextIcon, CpuChipIcon } from '@heroicons/react/24/outline';
import CoverLetterModal from './CoverLetterModal';
import InterviewModal from './InterviewModal';

interface FlashcardProps {
  offer: {
    id: number;
    offer: number;
    offer_detail: {
      title: string;
      description: string;
      required_skills: string;
      duration_months: number | null;
      company_name?: string;
      company_info?: {
        company_name: string;
      };
      location: string | null;
      offer_type?: string;
      source_url?: string | null;
      source_platform?: string | null;
      published_date?: string | null;
      contact_email?: string | null;
    };
    score_percent: number;
    missing_skills?: string[];
    recommendation_summary?: string;
    insights?: {
      semantic_score?: number;
      skill_overlap_score?: number;
      context_bonus?: number;
      preference_bonus?: number;
      score_band?: string;
    };
  };
}

export default function Flashcard({ offer }: FlashcardProps) {
  const { title, description, required_skills, duration_months, location, offer_type, source_url, source_platform, published_date, contact_email } = offer.offer_detail;
  const companyName = offer.offer_detail.company_name ?? offer.offer_detail.company_info?.company_name ?? 'Entreprise';
  const score = offer.score_percent;
  const insights = offer.insights ?? {};
  const [showCoverLetter, setShowCoverLetter] = useState(false);
  const [showInterview, setShowInterview] = useState(false);
  const offerId = offer.offer;
  
  const radius = 20;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  
  const getScoreColor = (s: number) => {
    if (s >= 80) return 'text-green-500 stroke-green-500';
    if (s >= 50) return 'text-yellow-500 stroke-yellow-500';
    return 'text-red-500 stroke-red-500';
  };

  const getPlatformColor = (platform?: string) => {
    if (!platform) return 'bg-gray-100 text-gray-600';
    const p = platform.toLowerCase();
    if (p.includes('linkedin')) return 'bg-blue-100 text-blue-700 border-blue-200';
    if (p.includes('indeed')) return 'bg-blue-50 text-blue-800 border-blue-200';
    if (p.includes('google')) return 'bg-red-50 text-red-600 border-red-200';
    return 'bg-purple-50 text-purple-700 border-purple-200';
  };

  const getTypeBadge = (type?: string) => {
    if (type === 'emploi') return <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded text-xs font-bold border border-emerald-200 uppercase tracking-wider">Emploi</span>;
    if (type === 'freelance') return <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded text-xs font-bold border border-purple-200 uppercase tracking-wider">Freelance</span>;
    return <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs font-bold border border-blue-200 uppercase tracking-wider">Stage</span>;
  };

  // Calcul du nombre de jours depuis la publication
  const getDaysAgo = (dateStr?: string) => {
    if (!dateStr) return null;
    const diffTime = Math.abs(new Date().getTime() - new Date(dateStr).getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays === 0) return "Aujourd'hui";
    if (diffDays === 1) return "Hier";
    return `Il y a ${diffDays} jours`;
  };

  return (
    <div className="glass-card rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl relative overflow-hidden group flex flex-col h-full">
      <div className="absolute top-0 right-0 p-4 flex justify-end">
        <div className="relative flex items-center justify-center">
          <svg className="transform -rotate-90 w-16 h-16">
            <circle cx="32" cy="32" r={radius} stroke="currentColor" strokeWidth="4" fill="transparent" className="text-gray-200 dark:text-gray-700" />
            <circle
              cx="32"
              cy="32"
              r={radius}
              stroke="currentColor"
              strokeWidth="4"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className={`transition-all duration-1000 ease-out ${getScoreColor(score)}`}
              strokeLinecap="round"
            />
          </svg>
          <span className="absolute text-sm font-bold">{score}%</span>
        </div>
      </div>
      
      <div className="pr-16 flex-1">
        <div className="flex items-center gap-2 mb-2">
          {getTypeBadge(offer_type)}
          {source_platform && (
            <span className={`text-xs font-bold px-2 py-0.5 rounded border ${getPlatformColor(source_platform)} flex items-center gap-1`}>
              <GlobeAltIcon className="h-3 w-3" />
              {source_platform}
            </span>
          )}
          {published_date && (
            <span className="text-xs text-gray-500 flex items-center gap-1">
              <CalendarDaysIcon className="h-3 w-3" />
              {getDaysAgo(published_date)}
            </span>
          )}
        </div>
        
        <h3 className="text-xl font-heading font-bold mb-1 text-foreground">{title}</h3>
        <p className="text-primary font-medium mb-4">{companyName}</p>
        
        <div className="flex flex-wrap gap-3 mb-4 text-sm text-secondary-foreground">
          {location && (
            <div className="flex items-center gap-1 bg-secondary px-2.5 py-1 rounded-full">
              <MapPinIcon className="h-4 w-4" /> <span>{location}</span>
            </div>
          )}
          {duration_months && (
            <div className="flex items-center gap-1 bg-secondary px-2.5 py-1 rounded-full">
              <ClockIcon className="h-4 w-4" /> <span>{duration_months} Mois</span>
            </div>
          )}
        </div>
        
        <p className="text-sm text-secondary-foreground mb-4 line-clamp-3 leading-relaxed">
          {description}
        </p>

        {offer.recommendation_summary ? (
          <div className="mb-4 rounded-xl bg-primary/5 border border-primary/10 p-3">
            <p className="text-sm text-foreground">{offer.recommendation_summary}</p>
          </div>
        ) : null}
        
        <div className="flex flex-col gap-2 mb-6">
          <div className="flex flex-wrap gap-2">
            <span className="text-xs font-bold text-gray-500 mr-1 flex items-center">Requis :</span>
            {required_skills.split(',').slice(0, 4).map((skill, idx) => (
              <span key={idx} className="text-xs font-medium bg-primary/10 text-primary px-2 py-1 rounded border border-primary/20">
                {skill.trim()}
              </span>
            ))}
          </div>
          
          {offer.missing_skills && offer.missing_skills.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-1">
              <span className="text-xs font-bold text-red-500 mr-1 flex items-center">Lacunes (à apprendre) :</span>
              {offer.missing_skills.map((skill: string, idx: number) => (
                <span key={`missing-${idx}`} className="text-xs font-medium bg-red-50 text-red-600 px-2 py-1 rounded border border-red-200 shadow-sm">
                  {skill.trim()}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-2 mb-5 text-xs">
          <div className="bg-secondary rounded-lg px-3 py-2">
            <div className="text-secondary-foreground">Semantic</div>
            <div className="font-bold">{insights.semantic_score ?? 0}%</div>
          </div>
          <div className="bg-secondary rounded-lg px-3 py-2">
            <div className="text-secondary-foreground">Skills</div>
            <div className="font-bold">{insights.skill_overlap_score ?? 0}%</div>
          </div>
          <div className="bg-secondary rounded-lg px-3 py-2">
            <div className="text-secondary-foreground">Context</div>
            <div className="font-bold">+{insights.context_bonus ?? 0}</div>
          </div>
          <div className="bg-secondary rounded-lg px-3 py-2">
            <div className="text-secondary-foreground">Prefs</div>
            <div className="font-bold">+{insights.preference_bonus ?? 0}</div>
          </div>
        </div>
      </div>
      
      {/* Footer avec Actions */}
      <div className="mt-auto pt-4 border-t border-border">
        {/* Boutons IA */}
        <div className="flex gap-2 mb-3">
          <button
            onClick={() => setShowCoverLetter(true)}
            className="flex-1 flex items-center justify-center gap-1.5 border border-primary text-primary px-3 py-2 rounded-lg text-xs font-bold hover:bg-primary/10 transition-all"
          >
            <DocumentTextIcon className="h-3.5 w-3.5" /> Lettre IA
          </button>
          <button
            onClick={() => setShowInterview(true)}
            className="flex-1 flex items-center justify-center gap-1.5 border border-accent text-accent px-3 py-2 rounded-lg text-xs font-bold hover:bg-accent/10 transition-all"
          >
            <CpuChipIcon className="h-3.5 w-3.5" /> Entretien IA
          </button>
        </div>
        
        {/* Bouton Postuler */}
        <div className="flex justify-between items-center">
          <span className="text-xs text-secondary-foreground font-medium">Match: {score}%</span>
          {source_url ? (
            <a
              href={source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 bg-gradient-to-r from-primary to-accent text-white px-4 py-2 rounded-lg text-sm font-bold shadow-md hover:opacity-90 hover:shadow-lg transition-all"
            >
              Postuler <ArrowTopRightOnSquareIcon className="h-4 w-4" />
            </a>
          ) : contact_email ? (
            <a
              href={`mailto:${contact_email}?subject=Candidature pour le poste de ${title}`}
              className="flex items-center gap-1.5 bg-gradient-to-r from-primary to-accent text-white px-4 py-2 rounded-lg text-sm font-bold shadow-md hover:opacity-90 hover:shadow-lg transition-all"
            >
              Postuler par email
            </a>
          ) : (
            <span className="text-xs text-gray-400 italic">Candidature interne</span>
          )}
        </div>
      </div>
      
      <div className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-accent transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-500"></div>

      {/* Modals */}
      {showCoverLetter && (
            <CoverLetterModal
              offerId={offerId}
              offerTitle={title}
              companyName={companyName}
              onClose={() => setShowCoverLetter(false)}
            />
          )}
      {showInterview && (
            <InterviewModal
              offerId={offerId}
              offerTitle={title}
              companyName={companyName}
              onClose={() => setShowInterview(false)}
            />
          )}
    </div>
  );
}
