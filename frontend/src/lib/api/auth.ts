import { apiClient } from "./client";
import type { AuthResponse, LoginRequest, RegisterRequest, User } from "@/types/auth";

/** Register a new user account. */
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>("/auth/register", data);
  return response.data;
}

/** Log in with email and password. */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>("/auth/login", data);
  return response.data;
}

/** Refresh the access token using a refresh token. */
export async function refreshToken(token: string): Promise<{ access_token: string; refresh_token: string }> {
  const response = await apiClient.post("/auth/refresh", { refresh_token: token });
  return response.data;
}

/** Get the currently authenticated user profile. */
export async function getMe(): Promise<User> {
  const response = await apiClient.get<User>("/auth/me");
  return response.data;
}
