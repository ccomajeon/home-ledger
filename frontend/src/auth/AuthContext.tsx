import type { PropsWithChildren } from "react";
import { AuthContext } from "./context";
import { useMe } from "./useMe";

export function AuthProvider({ children }: PropsWithChildren) {
  const state = useMe();
  return <AuthContext.Provider value={state}>{children}</AuthContext.Provider>;
}
