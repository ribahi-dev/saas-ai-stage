import api from './api';

export interface AdminStats {
  total_students: number;
  total_companies: number;
  total_offers: number;
  active_offers: number;
  total_applications: number;
}

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  role: string;
  date_joined: string;
  is_active: boolean;
}

export interface AdminOffer {
  id: number;
  title: string;
  company_name: string;
  status: string;
  created_at: string;
}

export const getAdminStats = async (): Promise<AdminStats> => {
  const response = await api.get('/users/admin/stats/');
  return response.data;
};

export const getAdminUsers = async (): Promise<AdminUser[]> => {
  const response = await api.get('/users/admin/users/');
  return response.data;
};

export const deleteAdminUser = async (userId: number): Promise<void> => {
  await api.delete(`/users/admin/users/${userId}/`);
};

export const getAdminOffers = async (): Promise<AdminOffer[]> => {
  const response = await api.get('/users/admin/offers/');
  return response.data;
};

export const deleteAdminOffer = async (offerId: number): Promise<void> => {
  await api.delete(`/users/admin/offers/${offerId}/`);
};

export const triggerScraping = async (): Promise<{ message: string }> => {
  const response = await api.post('/users/admin/scrape/');
  return response.data;
};
