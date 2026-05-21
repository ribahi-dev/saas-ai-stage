import { GoogleLogin } from '@react-oauth/google';
import { isGoogleAuthConfigured } from '../services/authConfig';

type GoogleAuthButtonProps = {
  onSuccess: (credential: string) => void;
  onError?: () => void;
};

/**
 * Bouton officiel Sign In With Google (@react-oauth/google).
 * Necessite <GoogleOAuthProvider> et VITE_GOOGLE_CLIENT_ID dans .env frontend.
 */
export default function GoogleAuthButton({ onSuccess, onError }: GoogleAuthButtonProps) {
  if (!isGoogleAuthConfigured()) return null;

  return (
    <div className="flex w-full justify-center [&>div]:!w-full [&_iframe]:!w-full [&_iframe]:!max-w-none">
      <GoogleLogin
        onSuccess={(r) => {
          if (r.credential) onSuccess(r.credential);
          else onError?.();
        }}
        onError={() => onError?.()}
        theme="outline"
        size="large"
        text="continue_with"
      />
    </div>
  );
}
