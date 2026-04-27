/* eslint-disable react-hooks/set-state-in-effect */
/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface BaseUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

interface StudentProfile {
  id: number;
  user: BaseUser;
  bio: string | null;
  phone: string | null;
  linkedin_url: string | null;
  university: string | null;
  field_of_study: string | null;
  graduation_year: number | null;
  cv_file: string | null;
  target_job_titles: string[];
  preferred_locations: string[];
  preferred_offer_types: string[];
  remote_ok: boolean;
  expected_salary: number | null;
}

interface CompanyProfile {
  id: number;
  user: BaseUser;
  company_name: string;
  description: string | null;
  website: string | null;
  industry: string | null;
  city: string | null;
  country: string | null;
  logo: string | null;
}

interface StudentProfileForm {
  bio: string;
  phone: string;
  linkedin_url: string;
  university: string;
  field_of_study: string;
  graduation_year: number;
  target_job_titles: string;
  preferred_locations: string;
  preferred_offer_types: string[];
  remote_ok: boolean;
  expected_salary: string;
}

const defaultStudentForm: StudentProfileForm = {
  bio: '',
  phone: '',
  linkedin_url: '',
  university: '',
  field_of_study: '',
  graduation_year: new Date().getFullYear() + 1,
  target_job_titles: '',
  preferred_locations: '',
  preferred_offer_types: [] as string[],
  remote_ok: true,
  expected_salary: '',
};

const defaultCompanyForm = {
  company_name: '',
  description: '',
  website: '',
  industry: '',
  city: '',
  country: 'Maroc',
};

export default function Profile() {
  const { user } = useAuth();
  const [studentProfile, setStudentProfile] = useState<StudentProfile | null>(null);
  const [companyProfile, setCompanyProfile] = useState<CompanyProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [cvUploading, setCvUploading] = useState(false);
  const [studentForm, setStudentForm] = useState(defaultStudentForm);
  const [companyForm, setCompanyForm] = useState(defaultCompanyForm);

  async function fetchProfile() {
    try {
      if (user?.role === 'student') {
        const response = await api.get<StudentProfile>('/users/me/student/');
        setStudentProfile(response.data);
        setStudentForm({
          bio: response.data.bio ?? '',
          phone: response.data.phone ?? '',
          linkedin_url: response.data.linkedin_url ?? '',
          university: response.data.university ?? '',
          field_of_study: response.data.field_of_study ?? '',
          graduation_year: response.data.graduation_year ?? new Date().getFullYear() + 1,
          target_job_titles: (response.data.target_job_titles ?? []).join(', '),
          preferred_locations: (response.data.preferred_locations ?? []).join(', '),
          preferred_offer_types: response.data.preferred_offer_types ?? [],
          remote_ok: response.data.remote_ok ?? true,
          expected_salary: response.data.expected_salary ? String(response.data.expected_salary) : '',
        });
      }

      if (user?.role === 'company') {
        const response = await api.get<CompanyProfile>('/users/me/company/');
        setCompanyProfile(response.data);
        setCompanyForm({
          company_name: response.data.company_name ?? '',
          description: response.data.description ?? '',
          website: response.data.website ?? '',
          industry: response.data.industry ?? '',
          city: response.data.city ?? '',
          country: response.data.country ?? 'Maroc',
        });
      }
    } catch (error) {
      console.error('Erreur lors du chargement du profil:', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (user?.role === 'student' || user?.role === 'company') {
      void fetchProfile();
    }
  }, [user]);

  const handleStudentUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      await api.patch('/users/me/student/', {
        ...studentForm,
        target_job_titles: studentForm.target_job_titles
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean),
        preferred_locations: studentForm.preferred_locations
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean),
        expected_salary: studentForm.expected_salary ? Number(studentForm.expected_salary) : null,
      });
      window.alert('Profil mis a jour avec succes.');
      await fetchProfile();
    } catch (error) {
      console.error('Erreur lors de la mise a jour du profil:', error);
      window.alert('Erreur lors de la mise a jour du profil.');
    } finally {
      setSaving(false);
    }
  };

  const handleCompanyUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      await api.patch('/users/me/company/', companyForm);
      window.alert('Profil entreprise mis a jour avec succes.');
      await fetchProfile();
    } catch (error) {
      console.error('Erreur lors de la mise a jour du profil entreprise:', error);
      window.alert('Erreur lors de la mise a jour du profil entreprise.');
    } finally {
      setSaving(false);
    }
  };

  const handleCVUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)) {
      window.alert('Veuillez selectionner un PDF ou un DOCX.');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      window.alert('Le fichier ne doit pas depasser 5MB.');
      return;
    }

    setCvUploading(true);
    setLoading(true);
    const formDataCV = new FormData();
    formDataCV.append('cv_file', file);

    try {
      await api.post('/users/me/cv/', formDataCV, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      await api.post('/ai/recommendations/refresh/');
      window.alert('CV uploade avec succes.');
      await fetchProfile();
    } catch (error) {
      console.error("Erreur lors de l'upload du CV:", error);
      window.alert("Erreur lors de l'upload du CV.");
    } finally {
      setCvUploading(false);
    }
  };

  if (!user || (user.role !== 'student' && user.role !== 'company')) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Veuillez vous connecter pour acceder a votre profil.</p>
      </div>
    );
  }

  if (loading) {
    return <div className="text-center py-8">Chargement du profil...</div>;
  }

  if (user.role === 'company' && companyProfile) {
    return (
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Profil Entreprise</h1>

        <div className="bg-white rounded-lg shadow-md p-6">
          <form onSubmit={handleCompanyUpdate} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nom de l&apos;entreprise</label>
                <input
                  type="text"
                  value={companyForm.company_name}
                  onChange={(e) => setCompanyForm({ ...companyForm, company_name: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Secteur</label>
                <input
                  type="text"
                  value={companyForm.industry}
                  onChange={(e) => setCompanyForm({ ...companyForm, industry: e.target.value })}
                  className="input-field"
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Ville</label>
                <input
                  type="text"
                  value={companyForm.city}
                  onChange={(e) => setCompanyForm({ ...companyForm, city: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Pays</label>
                <input
                  type="text"
                  value={companyForm.country}
                  onChange={(e) => setCompanyForm({ ...companyForm, country: e.target.value })}
                  className="input-field"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Site web</label>
              <input
                type="url"
                value={companyForm.website}
                onChange={(e) => setCompanyForm({ ...companyForm, website: e.target.value })}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea
                rows={5}
                value={companyForm.description}
                onChange={(e) => setCompanyForm({ ...companyForm, description: e.target.value })}
                className="input-field"
              />
            </div>

            <button
              type="submit"
              disabled={saving}
              className="bg-primary text-primary-foreground px-5 py-2.5 rounded-lg font-semibold hover:bg-primary/90 disabled:opacity-50"
            >
              {saving ? 'Enregistrement...' : 'Enregistrer'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Mon Profil</h1>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-6">Informations Personnelles</h2>

          <form onSubmit={handleStudentUpdate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Nom complet</label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={studentProfile?.user.first_name ?? ''}
                  disabled
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                />
                <input
                  type="text"
                  value={studentProfile?.user.last_name ?? ''}
                  disabled
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={studentProfile?.user.email ?? ''}
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Telephone</label>
              <input
                type="tel"
                value={studentForm.phone}
                onChange={(e) => setStudentForm({ ...studentForm, phone: e.target.value })}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">LinkedIn URL</label>
              <input
                type="url"
                value={studentForm.linkedin_url}
                onChange={(e) => setStudentForm({ ...studentForm, linkedin_url: e.target.value })}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Biographie</label>
              <textarea
                rows={4}
                value={studentForm.bio}
                onChange={(e) => setStudentForm({ ...studentForm, bio: e.target.value })}
                className="input-field"
              />
            </div>

            <button
              type="submit"
              disabled={saving}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
              {saving ? 'Enregistrement...' : 'Enregistrer les modifications'}
            </button>
          </form>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-6">Informations Academiques</h2>

            <form onSubmit={handleStudentUpdate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Universite / Ecole</label>
                <input
                  type="text"
                  value={studentForm.university}
                  onChange={(e) => setStudentForm({ ...studentForm, university: e.target.value })}
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Filiere</label>
                <input
                  type="text"
                  value={studentForm.field_of_study}
                  onChange={(e) => setStudentForm({ ...studentForm, field_of_study: e.target.value })}
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Annee de diplomation</label>
                <input
                  type="number"
                  min="2020"
                  max="2035"
                  value={studentForm.graduation_year}
                  onChange={(e) => setStudentForm({ ...studentForm, graduation_year: Number(e.target.value) })}
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Postes cibles</label>
                <input
                  type="text"
                  value={studentForm.target_job_titles}
                  onChange={(e) => setStudentForm({ ...studentForm, target_job_titles: e.target.value })}
                  placeholder="ex: Data Analyst, Developpeur Python, Product Designer"
                  className="input-field"
                />
                <p className="text-xs text-gray-500 mt-1">Separe les intitulés par des virgules.</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Villes preferees</label>
                <input
                  type="text"
                  value={studentForm.preferred_locations}
                  onChange={(e) => setStudentForm({ ...studentForm, preferred_locations: e.target.value })}
                  placeholder="Casablanca, Rabat, Remote Maroc"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Types d'offres preferes</label>
                <div className="flex flex-wrap gap-3">
                  {[
                    { value: 'stage', label: 'Stage' },
                    { value: 'emploi', label: 'Emploi' },
                    { value: 'freelance', label: 'Freelance' },
                  ].map((option) => (
                    <label key={option.value} className="inline-flex items-center gap-2 text-sm text-gray-700">
                      <input
                        type="checkbox"
                        checked={studentForm.preferred_offer_types.includes(option.value)}
                        onChange={(e) => {
                          const next = e.target.checked
                            ? [...studentForm.preferred_offer_types, option.value]
                            : studentForm.preferred_offer_types.filter((item) => item !== option.value);
                          setStudentForm({ ...studentForm, preferred_offer_types: next });
                        }}
                      />
                      {option.label}
                    </label>
                  ))}
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <label className="inline-flex items-center gap-2 text-sm font-medium text-gray-700">
                  <input
                    type="checkbox"
                    checked={studentForm.remote_ok}
                    onChange={(e) => setStudentForm({ ...studentForm, remote_ok: e.target.checked })}
                  />
                  J'accepte les offres remote
                </label>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Salaire vise (MAD)</label>
                  <input
                    type="number"
                    min="0"
                    value={studentForm.expected_salary}
                    onChange={(e) => setStudentForm({ ...studentForm, expected_salary: e.target.value })}
                    placeholder="Optionnel"
                    className="input-field"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={saving}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              >
                {saving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            </form>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-6">Curriculum Vitae</h2>

            {studentProfile?.cv_file ? (
              <div className="mb-4">
                <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
                  <span className="text-green-800">CV uploadé avec succes</span>
                  <a
                    href={studentProfile.cv_file}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Voir le CV
                  </a>
                </div>
              </div>
            ) : (
              <div className="mb-4">
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-yellow-800 text-sm">
                    Aucun CV uploadé. Ajoutez votre CV pour activer les recommandations IA.
                  </p>
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {studentProfile?.cv_file ? 'Remplacer le CV' : 'Uploader un CV'} (PDF ou DOCX, max 5MB)
              </label>
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={handleCVUpload}
                disabled={cvUploading}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              {cvUploading ? (
                <p className="text-sm text-blue-600 mt-2">Upload en cours...</p>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
