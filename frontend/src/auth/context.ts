import { createContext, useContext } from "react";
import type { CurrentUser } from "../api/types";

export type AuthState = {
  loading: boolean;
  user: CurrentUser | null;
  errorStatus: number | null;
};

export const AuthContext = createContext<AuthState | null>(null);

export function useAuth(): AuthState {
  const state = useContext(AuthContext);
  if (!state) throw new Error("useAuth must be used within AuthProvider");
  return state;
}
