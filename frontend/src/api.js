import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ─── Product Classifier ────────────────────────────────────────────────────
export const classifyProduct = async (description) => {
  const res = await api.post('/classify', { description });
  return res.data;
};

// ─── SNP Matcher ───────────────────────────────────────────────────────────
export const matchSNP = async ({ product_desc, location, capacity, top_k = 3 }) => {
  const res = await api.get('/match/snp', {
    params: { product_desc, location, capacity, top_k },
  });
  return res.data;
};

// ─── Onboarding ────────────────────────────────────────────────────────────
export const onboardMSE = async (formData) => {
  const res = await api.post('/onboard/mse', formData);
  return res.data;
};

export const listMSEs = async (skip = 0, limit = 20) => {
  const res = await api.get('/onboard/mse/list', { params: { skip, limit } });
  return res.data;
};

// ─── Voice / Sarvam ──────────────────────────────────────────────────────
export const transcribeVoice = async (audio_base64, source_lang, audio_format = 'webm') => {
  const res = await api.post('/voice/transcribe/base64', {
    audio_base64,
    source_lang,
    audio_format
  });
  return res.data;
};

export const getSupportedLanguages = async () => {
  const res = await api.get('/voice/languages');
  return res.data;
};

// ─── Document Verification ────────────────────────────────────────────────
export const verifyDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/verify/document', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

// ─── Contract Search ────────────────────────────────────────────────────────
export const searchContracts = async ({ product_desc, location, state, top_k = 10 }) => {
  const res = await api.get('/contracts/search', {
    params: { product_desc, location, state, top_k },
  });
  return res.data;
};

export const getContractPortals = async () => {
  const res = await api.get('/contracts/portals');
  return res.data;
};

export default api;
