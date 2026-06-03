// frontend/lib/auth.ts

import { api } from './api';

export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  message: string;
}

export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  return api.post<AuthResponse>('/api/auth/login', credentials);
}

export async function register(data: RegisterData): Promise<AuthResponse> {
  return api.post<AuthResponse>('/api/auth/register', data);
}

export async function logout(): Promise<{ message: string }> {
  return api.post<{ message: string }>('/api/auth/logout');
}

export async function getCurrentUser(): Promise<User> {
  return api.get<User>('/api/auth/me');
}

