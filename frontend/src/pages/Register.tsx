import { useState } from 'react';
import type { AxiosError } from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface RegisterErrorResponse {
  detail?: string;
  email?: string[];
  password?: string[];
  username?: string[];
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
  const { register } = useAuth();
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
      navigate('/login');
    } catch (err) {
      const axiosError = err as AxiosError<RegisterErrorResponse>;
      const apiError = axiosError.response?.data;
      setError(
        apiError?.detail ||
        apiError?.email?.[0] ||
        apiError?.password?.[0] ||
        apiError?.username?.[0] ||
        "Erreur lors de l'inscription."
      );
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
