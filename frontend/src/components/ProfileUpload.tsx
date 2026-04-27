import { useState } from 'react';
import type { AxiosError } from 'axios';
import { DocumentArrowUpIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import api from '../services/api';

interface ProfileUploadProps {
  onUploadSuccess: () => void;
}

interface UploadErrorResponse {
  detail?: string;
}

export default function ProfileUpload({ onUploadSuccess }: ProfileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('cv_file', file);

    try {
      await api.post('/users/me/cv/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      await api.post('/ai/recommendations/refresh/');
      setFile(null);
      onUploadSuccess();
    } catch (err) {
      const axiosError = err as AxiosError<UploadErrorResponse>;
      setError(axiosError.response?.data?.detail || "Erreur lors de l'upload. L'IA a peut-etre rencontre un probleme avec ce fichier.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="glass-card rounded-2xl p-8 text-center border-dashed border-2 border-primary/30 hover:border-primary/50 transition-colors">
      <div className="max-w-md mx-auto">
        <div className="w-20 h-20 mx-auto bg-primary/10 rounded-full flex items-center justify-center mb-6 shadow-inner">
          <DocumentArrowUpIcon className="h-10 w-10 text-primary" />
        </div>

        <h2 className="text-2xl font-heading font-bold mb-2">Upload ton CV</h2>
        <p className="text-secondary-foreground mb-8">
          Laisse notre IA analyser tes competences et te trouver le stage parfait. (PDF ou DOCX)
        </p>

        <div className="space-y-4">
          <input
            type="file"
            id="cv-upload"
            className="hidden"
            accept=".pdf,.doc,.docx"
            onChange={handleFileChange}
            disabled={isUploading}
          />
          <label
            htmlFor="cv-upload"
            className={`cursor-pointer inline-block w-full py-3 px-4 rounded-xl border border-border shadow-sm font-medium transition-colors ${
              file ? 'bg-secondary text-foreground' : 'bg-card text-secondary-foreground hover:bg-secondary'
            } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {file ? file.name : 'Choisir un fichier'}
          </label>

          <button
            onClick={() => void handleUpload()}
            disabled={!file || isUploading}
            className={`w-full py-3 rounded-xl font-bold shadow-lg transition-all flex items-center justify-center gap-2 ${
              !file || isUploading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed dark:bg-gray-800'
                : 'bg-gradient-to-r from-primary to-accent text-white hover:opacity-90 hover:-translate-y-0.5'
            }`}
          >
            {isUploading ? (
              <>
                <ArrowPathIcon className="h-5 w-5 animate-spin" />
                Analyse de l&apos;IA en cours...
              </>
            ) : (
              'Scanner mon profil'
            )}
          </button>

          {error ? <p className="text-red-500 text-sm mt-2">{error}</p> : null}
        </div>
      </div>
    </div>
  );
}
