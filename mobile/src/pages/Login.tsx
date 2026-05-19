import { useState } from 'react';
import type { AxiosError } from 'axios';
import { useNavigate } from 'react-router-dom';
import GoogleAuthButton, { isGoogleAuthConfigured } from '../components/GoogleAuthButton';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login, loginWithGoogle } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch {
      setError('Identifiants incorrects.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative z-10">
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-primary/20 rounded-full blur-3xl animate-blob"></div>
      <div className="absolute top-1/3 right-1/4 w-72 h-72 bg-accent/20 rounded-full blur-3xl animate-blob animation-delay-2000"></div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative">
        <h2 className="text-center text-4xl font-extrabold font-heading text-foreground tracking-tight">
          Bienvenue
        </h2>
        <p className="mt-2 text-center text-sm text-secondary-foreground">
          Connectez-vous pour trouver votre stage avec l&apos;IA
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative">
        <div className="glass py-8 px-4 shadow sm:rounded-2xl sm:px-10">
          <form className="space-y-6" onSubmit={handleLogin}>
            <div>
              <label className="block text-sm font-medium text-foreground">
                Nom d&apos;utilisateur
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-background/50"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground">
                Mot de passe
              </label>
              <div className="mt-1">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-background/50"
                />
              </div>
            </div>

            {error ? (
              <div className="text-red-500 text-sm font-medium">{error}</div>
            ) : null}

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-md text-sm font-bold text-white bg-gradient-to-r from-primary to-accent hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-all disabled:opacity-50"
              >
                {loading ? 'Connexion...' : 'Se connecter'}
              </button>
            </div>
          </form>

          {isGoogleAuthConfigured() ? (
            <>
              <div className="relative my-8">
                <div className="absolute inset-0 flex items-center" aria-hidden>
                  <span className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center">
                  <span className="px-3 text-xs uppercase tracking-wide text-secondary-foreground bg-background/90">
                    Ou avec Google
                  </span>
                </div>
              </div>
              <GoogleAuthButton
                onSuccess={async (credential) => {
                  setError('');
                  setLoading(true);
                  try {
                    await loginWithGoogle(credential);
                    navigate('/dashboard');
                  } catch (err) {
                    const ax = err as AxiosError<{ detail?: string }>;
                    setError(
                      ax.response?.data?.detail ||
                        'Connexion Google refusee ou service temporairement indisponible.',
                    );
                  } finally {
                    setLoading(false);
                  }
                }}
                onError={() => setError('Connexion Google annulee.')}
              />
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
