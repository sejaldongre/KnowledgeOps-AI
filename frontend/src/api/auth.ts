import apiClient from "./client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
}

export async function login(
  data: LoginRequest,
): Promise<TokenResponse> {
  const response =
    await apiClient.post<TokenResponse>(
      "/auth/login",
      data,
    );

  return response.data;
}

export async function getCurrentUser(): Promise<UserResponse> {
  const response =
    await apiClient.get<UserResponse>(
      "/auth/me",
    );

  return response.data;
}