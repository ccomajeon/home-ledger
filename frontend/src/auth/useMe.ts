import { useEffect, useState } from "react";
import { apiGet, ApiError } from "../api/client";
import type { CurrentUser } from "../api/types";

type MeState = {
  loading: boolean;
  user: CurrentUser | null;
  errorStatus: number | null;
};

export function useMe() {
  const [state, setState] = useState<MeState>({
    loading: true,
    user: null,
    errorStatus: null,
  });

  useEffect(() => {
    let active = true;

    apiGet<CurrentUser>("/api/me")
      .then((user) => {
        if (active) setState({ loading: false, user, errorStatus: null });
      })
      .catch((error: unknown) => {
        if (!active) return;
        setState({
          loading: false,
          user: null,
          errorStatus: error instanceof ApiError ? error.status : 500,
        });
      });

    return () => {
      active = false;
    };
  }, []);

  return state;
}
