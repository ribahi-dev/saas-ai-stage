import { SparklesIcon, CheckBadgeIcon } from '@heroicons/react/24/outline';

interface ExtractedProfileProps {
  profile: {
    skills: string[];
    experience_level: string;
    projects: string[];
    target_job_titles?: string[];
    preferred_locations?: string[];
    preferred_offer_types?: string[];
    remote_ok?: boolean;
    expected_salary?: number | null;
  } | null;
}

export default function ExtractedProfile({ profile }: ExtractedProfileProps) {
  if (!profile || (!profile.skills.length && !profile.projects.length)) {
    return null;
  }

  return (
    <div className="glass-card rounded-2xl p-6 mb-8 animate-slide-up border-l-4 border-l-accent relative overflow-hidden">
      <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-accent/10 rounded-full blur-2xl"></div>
      
      <div className="flex items-center gap-2 mb-4">
        <SparklesIcon className="h-6 w-6 text-accent" />
        <h2 className="text-xl font-heading font-bold">Profil Analysé par l'IA</h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
        <div>
          <h3 className="text-sm font-semibold text-secondary-foreground mb-3 flex items-center gap-1">
            <CheckBadgeIcon className="h-4 w-4 text-primary" />
            Compétences Détectées
          </h3>
          <div className="flex flex-wrap gap-2">
            {profile.skills.map((skill, idx) => (
              <span key={idx} className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-medium border border-primary/20 shadow-sm">
                {skill}
              </span>
            ))}
          </div>
        </div>
        
        <div>
          <h3 className="text-sm font-semibold text-secondary-foreground mb-3 flex items-center gap-1">
            <CheckBadgeIcon className="h-4 w-4 text-primary" />
            Niveau & Projets
          </h3>
          <div className="mb-3">
            <span className="inline-block bg-accent/10 text-accent px-3 py-1 rounded-full text-sm font-medium border border-accent/20 shadow-sm">
              Niveau: {profile.experience_level}
            </span>
          </div>
          <ul className="space-y-1">
            {profile.projects.map((project, idx) => (
              <li key={idx} className="text-sm text-secondary-foreground flex items-start gap-2">
                <span className="text-primary mt-1">•</span>
                <span className="line-clamp-1">{project}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {(profile.target_job_titles?.length || profile.preferred_locations?.length || profile.preferred_offer_types?.length) ? (
        <div className="mt-5 border-t border-border pt-4 relative z-10">
          <h3 className="text-sm font-semibold text-secondary-foreground mb-3">Preferences de recherche</h3>
          <div className="flex flex-wrap gap-2 mb-2">
            {profile.target_job_titles?.map((title) => (
              <span key={title} className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm border border-primary/20">
                {title}
              </span>
            ))}
          </div>
          <div className="flex flex-wrap gap-2 text-xs text-secondary-foreground">
            {profile.preferred_locations?.map((location) => (
              <span key={location} className="bg-secondary px-2 py-1 rounded-full">{location}</span>
            ))}
            {profile.preferred_offer_types?.map((type) => (
              <span key={type} className="bg-secondary px-2 py-1 rounded-full">{type}</span>
            ))}
            {profile.remote_ok ? <span className="bg-secondary px-2 py-1 rounded-full">Remote OK</span> : null}
            {profile.expected_salary ? <span className="bg-secondary px-2 py-1 rounded-full">{profile.expected_salary} MAD cible</span> : null}
          </div>
        </div>
      ) : null}
    </div>
  );
}
