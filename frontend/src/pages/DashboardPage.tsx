import { API_BASE_URL } from "../api/client";
import { useMe } from "../auth/useMe";

export function DashboardPage() {
  const { loading, user, errorStatus } = useMe();

  return (
    <section className="stack">
      <div className="card">
        <h2>Account</h2>
        {loading && <p>Checking session...</p>}
        {!loading && user && (
          <p>
            Signed in as <strong>{user.email}</strong> ({user.role})
          </p>
        )}
        {!loading && errorStatus === 401 && <p>Not signed in yet.</p>}
        {!loading && errorStatus === 403 && <p>This account is not allowlisted.</p>}
      </div>

      <div className="card">
        <h2>Authentication</h2>
        <p>Use backend OAuth endpoint for sign-in.</p>
        <a className="button" href={`${API_BASE_URL}/auth/login`}>
          Continue with Google
        </a>
      </div>
    </section>
  );
}

