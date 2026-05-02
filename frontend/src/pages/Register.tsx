import { useState } from 'react';
import type { AxiosError } from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import GoogleAuthButton, { isGoogleAuthConfigured } from '../components/GoogleAuthButton';
import { useAuth } from '../contexts/AuthContext';

interface RegisterErrorResponse {
  detail?: string;
  email?: string[];
  password?: string[];
  password2?: string[];
  username?: string[];
  non_field_errors?: string[];
  role?: string[];
  [key: string]: string[] | string | undefined;
}

function extractRegisterError(payload?: RegisterErrorResponse): string {
  if (!payload) {
    return "Erreur lors de l'inscription.";
  }

  if (payload.detail) {
    return payload.detail;
  }

  if (payload.non_field_errors?.length) {
    return payload.non_field_errors[0];
  }

  const prioritizedKeys = ['email', 'username', 'password', 'password2', 'role'];
  for (const key of prioritizedKeys) {
    const value = payload[key];
    if (Array.isArray(value) && value.length > 0) {
      return value[0];
    }
    if (typeof value === 'string' && value.trim()) {
      return value;
    }
  }

  for (const value of Object.values(payload)) {
    if (Array.isArray(value) && value.length > 0) {
      return value[0];
    }
    if (typeof value === 'string' && value.trim()) {
      return value;
    }
  }

  return "Erreur lors de l'inscription.";
}

export default function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password2: '',
    role: 'student' as 'student' | 'company',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData((current) => ({
      ...current,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (formData.password !== formData.password2) {
      setError('Les mots de passe ne correspondent pas.');
      setLoading(false);
      return;
    }

    try {
      await register(formData);
      navigate('/dashboard');
    } catch (err) {
      const axiosError = err as AxiosError<RegisterErrorResponse>;
      const apiError = axiosError.response?.data;
      setError(extractRegisterError(apiError));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto glass-card rounded-2xl p-8 shadow-xl">
      <div className="text-center mb-8">
        <p className="text-sm uppercase tracking-[0.2em] text-secondary-foreground">Creation de compte</p>
        <h2 className="text-3xl font-heading font-bold mt-3">Rejoindre la plateforme</h2>
        <p className="text-secondary-foreground mt-2">
          Creez votre espace pour publier des offres ou recevoir des recommandations de stage.
        </p>
      </div>

      {error ? (
        <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-xl mb-5">
          {error}
        </div>
      ) : null}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">Role</label>
          <select
            name="role"
            value={formData.role}
            onChange={handleChange}
            className="input-field"
          >
            <option value="student">Etudiant</option>
            <option value="company">Entreprise</option>
          </select>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Prenom</label>
            <input
              type="text"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              className="input-field"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Nom</label>
            <input
              type="text"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              className="input-field"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">Nom d'utilisateur</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className="input-field"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">Email</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="input-field"
            required
          />
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Mot de passe</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="input-field"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Confirmation</label>
            <input
              type="password"
              name="password2"
              value={formData.password2}
              onChange={handleChange}
              className="input-field"
              required
            />
          </div>
        </div>

        {isGoogleAuthConfigured() ? (
          <>
            <div className="relative py-6">
              <div className="absolute inset-0 flex items-center" aria-hidden>
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center">
                <span className="px-3 text-xs uppercase tracking-wide text-secondary-foreground bg-card">
                  Ou avec Google
                </span>
              </div>
            </div>
            <p className="text-xs text-center text-secondary-foreground mb-3">
              Le role selectionne ci-dessus sera utilise pour votre premier compte Google.
            </p>
            <GoogleAuthButton
              onSuccess={async (credential) => {
                setError('');
                setLoading(true);
                try {
                  await loginWithGoogle(credential, formData.role);
                  navigate('/dashboard');
                } catch (err) {
                  const axiosErr = err as AxiosError<RegisterErrorResponse>;
                  setError(extractRegisterError(axiosErr.response?.data));
                } finally {
                  setLoading(false);
                }
              }}
              onError={() => setError('Connexion Google annulee.')}
            />
          </>
        ) : null}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary text-primary-foreground py-3 px-4 rounded-xl hover:bg-primary/90 disabled:opacity-50 font-semibold"
        >
          {loading ? 'Inscription...' : "S'inscrire"}
        </button>
      </form>

      <p className="text-center mt-5 text-secondary-foreground">
        Deja un compte ?{' '}
        <Link to="/login" className="text-primary hover:underline font-medium">
          Se connecter
        </Link>
      </p>
    </div>
  );
}
