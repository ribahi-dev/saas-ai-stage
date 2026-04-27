import { useState } from 'react';
import type { AxiosError } from 'axios';
import { XMarkIcon, DocumentTextIcon, ClipboardDocumentIcon, CheckIcon } from '@heroicons/react/24/outline';
import api from '../services/api';

interface CoverLetterModalProps {
  offerId: number;
  offerTitle: string;
  companyName: string;
  onClose: () => void;
}

interface CoverLetterErrorResponse {
  detail?: string;
}

export default function CoverLetterModal({ offerId, offerTitle, companyName, onClose }: CoverLetterModalProps) {
  const [coverLetter, setCoverLetter] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');

  const generateLetter = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.post(`/ai/cover-letter/${offerId}/`);
      setCoverLetter(res.data.cover_letter);
    } catch (err) {
      const axiosError = err as AxiosError<CoverLetterErrorResponse>;
      setError(axiosError.response?.data?.detail || 'Erreur lors de la generation. Reessayez.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(coverLetter);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="glass-card rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <DocumentTextIcon className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h2 className="text-lg font-bold font-heading">Lettre de motivation IA</h2>
              <p className="text-sm text-secondary-foreground">{offerTitle} - {companyName}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-secondary rounded-lg transition-colors">
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {!coverLetter && !loading ? (
            <div className="flex flex-col items-center justify-center gap-4 py-10 text-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white text-2xl">*</div>
              <h3 className="text-xl font-bold">Generer votre lettre</h3>
              <p className="text-secondary-foreground max-w-sm">
                L&apos;IA va lire votre CV et l&apos;offre ciblee pour rediger une lettre personnalisee et exploitable.
              </p>
              {error ? <p className="text-red-500 text-sm">{error}</p> : null}
              <button
                onClick={() => void generateLetter()}
                className="bg-gradient-to-r from-primary to-accent text-white px-6 py-3 rounded-xl font-bold hover:opacity-90 transition-all shadow-lg"
              >
                Generer avec Gemini
              </button>
            </div>
          ) : null}

          {loading ? (
            <div className="flex flex-col items-center justify-center gap-4 py-10">
              <div className="relative w-16 h-16">
                <div className="absolute inset-0 rounded-full border-4 border-primary/20"></div>
                <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-primary animate-spin"></div>
              </div>
              <p className="text-secondary-foreground font-medium">Gemini redige votre lettre...</p>
            </div>
          ) : null}

          {coverLetter ? (
            <div className="bg-white/5 dark:bg-black/10 rounded-xl p-5 border border-border text-sm leading-relaxed whitespace-pre-wrap font-mono">
              {coverLetter}
            </div>
          ) : null}
        </div>

        {coverLetter ? (
          <div className="p-4 border-t border-border flex justify-end gap-3">
            <button
              onClick={() => void generateLetter()}
              className="px-4 py-2 text-sm rounded-lg border border-border hover:bg-secondary transition-colors"
            >
              Regenerer
            </button>
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-gradient-to-r from-primary to-accent text-white rounded-lg font-bold hover:opacity-90 transition-all"
            >
              {copied ? (
                <><CheckIcon className="h-4 w-4" /> Copie !</>
              ) : (
                <><ClipboardDocumentIcon className="h-4 w-4" /> Copier la lettre</>
              )}
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
