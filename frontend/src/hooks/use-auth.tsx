"use client";

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState
} from "react";

import { api } from "@/services/api";
import { loginJson, me, registerUser } from "@/services/auth";
import { clearToken, getToken, setToken as persistToken } from "@/services/token";
import type { LoginPayload, RegisterPayload, User } from "@/types";

type AuthContextValue = {
  ready: boolean;
  token: string | null;
  user: User | null;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const storedToken = getToken();
    setTokenState(storedToken);
    if (!storedToken) {
      setReady(true);
      return;
    }

    me()
      .then(setUser)
      .catch(() => {
        clearToken();
        setTokenState(null);
      })
      .finally(() => setReady(true));
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const tokenResponse = await loginJson(payload);
    persistToken(tokenResponse.access_token);
    setTokenState(tokenResponse.access_token);
    const currentUser = await me();
    setUser(currentUser);
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    await registerUser(payload);
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setTokenState(null);
    setUser(null);
    api.defaults.headers.common.Authorization = "";
  }, []);

  const value = useMemo(
    () => ({ ready, token, user, login, register, logout }),
    [ready, token, user, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return value;
}

