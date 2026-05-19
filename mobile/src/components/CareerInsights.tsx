interface CareerInsightsProps {
  insights: {
    profile_completion_score: number;
    strengths: string[];
    priority_skills: string[];
    target_cities: string[];
    recommended_track: string;
    action_plan: string[];
  } | null;
}

const TRACK_LABELS: Record<string, string> = {
  software_engineering: 'Software Engineering',
  data_ai: 'Data & IA',
  mobile: 'Mobile',
  product_design: 'Product Design',
  generaliste: 'Generaliste',
};

export default function CareerInsights({ insights }: CareerInsightsProps) {
  if (!insights) {
    return null;
  }

  return (
    <div className="glass-card rounded-2xl p-6 border-l-4 border-l-primary">
      <div className="flex items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-xl font-heading font-bold">Career Insights</h2>
          <p className="text-sm text-secondary-foreground">
            Lecture produit de votre positionnement et des prochains leviers a travailler.
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-primary">{insights.profile_completion_score}%</div>
          <div className="text-xs text-secondary-foreground">Profil complete</div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        <div>
          <h3 className="text-sm font-semibold text-secondary-foreground mb-2">Track recommande</h3>
          <div className="inline-flex bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-semibold">
            {TRACK_LABELS[insights.recommended_track] ?? insights.recommended_track}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-secondary-foreground mb-2">Villes les plus pertinentes</h3>
          <div className="flex flex-wrap gap-2">
            {insights.target_cities.length > 0 ? insights.target_cities.map((city) => (
              <span key={city} className="bg-secondary text-foreground px-2.5 py-1 rounded-full text-sm">
                {city}
              </span>
            )) : <span className="text-sm text-secondary-foreground">Pas encore assez de signal.</span>}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-secondary-foreground mb-2">Vos forces actuelles</h3>
          <div className="flex flex-wrap gap-2">
            {insights.strengths.length > 0 ? insights.strengths.map((skill) => (
              <span key={skill} className="bg-green-100 text-green-800 px-2.5 py-1 rounded-full text-sm">
                {skill}
              </span>
            )) : <span className="text-sm text-secondary-foreground">Ajoutez votre CV et vos preferences.</span>}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-secondary-foreground mb-2">Competences prioritaires</h3>
          <div className="flex flex-wrap gap-2">
            {insights.priority_skills.length > 0 ? insights.priority_skills.map((skill) => (
              <span key={skill} className="bg-amber-100 text-amber-800 px-2.5 py-1 rounded-full text-sm">
                {skill}
              </span>
            )) : <span className="text-sm text-secondary-foreground">Vos matches sont deja bien alignes.</span>}
          </div>
        </div>
      </div>

      <div className="mt-5">
        <h3 className="text-sm font-semibold text-secondary-foreground mb-2">Plan d'action</h3>
        <ul className="space-y-2">
          {insights.action_plan.map((item) => (
            <li key={item} className="text-sm text-foreground flex items-start gap-2">
              <span className="text-primary mt-0.5">•</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
