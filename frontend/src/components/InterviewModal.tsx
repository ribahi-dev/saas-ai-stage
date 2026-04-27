import { useEffect, useRef, useState } from 'react';
import { XMarkIcon, PaperAirplaneIcon, CpuChipIcon } from '@heroicons/react/24/outline';
import api from '../services/api';

interface Message {
  role: 'user' | 'bot';
  text: string;
}

interface InterviewModalProps {
  offerId: number;
  offerTitle: string;
  companyName: string;
  onClose: () => void;
}

export default function InterviewModal({ offerId, offerTitle, companyName, onClose }: InterviewModalProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim() && started) return;

    const userMessage: Message | null = messageText ? { role: 'user', text: messageText } : null;
    const updatedMessages = userMessage ? [...messages, userMessage] : messages;

    if (userMessage) {
      setMessages(updatedMessages);
    }

    setInput('');
    setLoading(true);
    setStarted(true);

    try {
      const res = await api.post(`/ai/interview/${offerId}/`, {
        message: messageText,
        history: updatedMessages.map((message) => ({ role: message.role, text: message.text })),
      });

      const botMessage: Message = { role: 'bot', text: res.data.bot_message };
      setMessages((prev) => [...prev, botMessage]);
    } catch {
      setMessages((prev) => [...prev, { role: 'bot', text: "Erreur de connexion avec l'IA. Reessayez." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void sendMessage(input);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="glass-card rounded-2xl w-full max-w-2xl h-[80vh] flex flex-col shadow-2xl">
        <div className="flex items-center justify-between p-5 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <CpuChipIcon className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h2 className="text-lg font-bold font-heading">Simulateur d&apos;entretien IA</h2>
              <p className="text-sm text-secondary-foreground">{offerTitle} - {companyName}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-secondary rounded-lg transition-colors">
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-4">
          {!started ? (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white text-2xl">IA</div>
              <h3 className="text-xl font-bold">Pret pour l&apos;entretien ?</h3>
              <p className="text-secondary-foreground max-w-sm text-sm">
                Un recruteur IA de <strong>{companyName}</strong> va vous poser des questions sur le poste <strong>{offerTitle}</strong>.
              </p>
              <button
                onClick={() => void sendMessage('')}
                className="bg-gradient-to-r from-primary to-accent text-white px-6 py-3 rounded-xl font-bold hover:opacity-90 transition-all shadow-lg"
              >
                Commencer
              </button>
            </div>
          ) : null}

          {messages.map((message, index) => (
            <div key={index} className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0 ${
                message.role === 'bot' ? 'bg-gradient-to-br from-primary to-accent text-white' : 'bg-secondary text-foreground'
              }`}>
                {message.role === 'bot' ? 'IA' : 'Vous'}
              </div>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground rounded-tr-none'
                  : 'bg-secondary text-foreground rounded-tl-none'
              }`}>
                {message.text}
              </div>
            </div>
          ))}

          {loading ? (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-xs text-white flex-shrink-0">IA</div>
              <div className="bg-secondary rounded-2xl rounded-tl-none px-4 py-3">
                <div className="flex gap-1.5">
                  <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            </div>
          ) : null}

          <div ref={bottomRef} />
        </div>

        {started ? (
          <form onSubmit={handleSubmit} className="p-4 border-t border-border flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Votre reponse..."
              disabled={loading}
              className="input-field flex-1 disabled:opacity-50"
              autoFocus
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-gradient-to-r from-primary to-accent text-white p-3 rounded-xl hover:opacity-90 disabled:opacity-50 transition-all"
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </form>
        ) : null}
      </div>
    </div>
  );
}
