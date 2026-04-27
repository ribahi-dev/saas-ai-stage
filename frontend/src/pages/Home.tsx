import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="w-full space-y-8">
      <section className="glass-card rounded-3xl p-8 md:p-12 overflow-hidden relative">
        <div className="absolute inset-y-0 right-0 w-1/2 bg-gradient-to-l from-primary/10 to-transparent pointer-events-none"></div>
        <div className="relative max-w-3xl">
          <p className="text-sm uppercase tracking-[0.25em] text-secondary-foreground">AI Intern Match</p>
          <h1 className="text-4xl md:text-6xl font-heading font-bold mt-4 leading-tight">
            La plateforme qui rapproche les etudiants des bonnes offres.
          </h1>
          <p className="text-lg md:text-xl text-secondary-foreground mt-5 max-w-2xl">
            Analyse du CV, recommandations ciblees, simulation d'entretien et suivi des candidatures dans un espace clair.
          </p>

          <div className="flex flex-wrap gap-3 mt-8">
            {user ? (
              <Link
                to={user.role === 'company' ? '/company/offers' : '/dashboard'}
                className="bg-primary text-primary-foreground px-6 py-3 rounded-xl font-semibold hover:bg-primary/90"
              >
                Ouvrir mon espace
              </Link>
            ) : (
              <>
                <Link
                  to="/register"
                  className="bg-primary text-primary-foreground px-6 py-3 rounded-xl font-semibold hover:bg-primary/90"
                >
                  Creer un compte
                </Link>
                <Link
                  to="/offers"
                  className="border border-border bg-white/60 px-6 py-3 rounded-xl font-semibold hover:bg-white"
                >
                  Explorer les offres
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      <section className="grid md:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl shadow-md p-6">
          <p className="text-sm uppercase tracking-[0.2em] text-secondary-foreground">Etudiants</p>
          <h3 className="text-2xl font-semibold mt-3">Un parcours fluide</h3>
          <p className="text-secondary-foreground mt-3">
            Uploadez votre CV, obtenez un profil extrait par l&apos;IA, puis ciblez rapidement les offres les plus compatibles.
          </p>
        </div>
        <div className="bg-white rounded-2xl shadow-md p-6">
          <p className="text-sm uppercase tracking-[0.2em] text-secondary-foreground">Entreprises</p>
          <h3 className="text-2xl font-semibold mt-3">Un pilotage clair</h3>
          <p className="text-secondary-foreground mt-3">
            Publiez vos offres, recevez des candidatures et traitez-les directement depuis un tableau de bord simple.
          </p>
        </div>
        <div className="bg-white rounded-2xl shadow-md p-6">
          <p className="text-sm uppercase tracking-[0.2em] text-secondary-foreground">IA</p>
          <h3 className="text-2xl font-semibold mt-3">Des outils utiles</h3>
          <p className="text-secondary-foreground mt-3">
            Recommandations, lettre de motivation et entrainement entretien servent un objectif concret, pas juste un effet demo.
          </p>
        </div>
      </section>
    </div>
  );
}
