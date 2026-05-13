import { api } from "@/services/api";
import type { LoginPayload, RegisterPayload, TokenResponse, User } from "@/types";

export async function loginJson(payload: LoginPayload): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>("/auth/login/json", payload);
  return response.data;
}

export async function registerUser(payload: RegisterPayload): Promise<User> {
  const response = await api.post<User>("/auth/register", payload);
  return response.data;
}

export async function me(): Promise<User> {
  const response = await api.get<User>("/auth/me");
  return response.data;
}

