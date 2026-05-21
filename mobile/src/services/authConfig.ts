export function isGoogleAuthConfigured(): boolean {
  const cid = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  return Boolean(cid && String(cid).trim().length > 0);
}
