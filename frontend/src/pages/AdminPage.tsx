import { useEffect, useState, type FormEvent } from "react";
import { apiGet, apiPatch, apiPost } from "../api/client";
import type { Account, Backup } from "../api/types";
import { useAuth } from "../auth/context";

export function AdminPage() {
  const { user, loading } = useAuth();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [backups, setBackups] = useState<Backup[]>([]);
  const [email, setEmail] = useState("");

  async function load() {
    const [accountData, backupData] = await Promise.all([
      apiGet<Account[]>("/api/admin/accounts"),
      apiGet<Backup[]>("/api/admin/backups").catch(() => []),
    ]);
    setAccounts(accountData);
    setBackups(backupData);
  }

  useEffect(() => {
    if (user?.role !== "OWNER") return;
    Promise.all([
      apiGet<Account[]>("/api/admin/accounts"),
      apiGet<Backup[]>("/api/admin/backups").catch(() => []),
    ]).then(([accountData, backupData]) => {
      setAccounts(accountData);
      setBackups(backupData);
    });
  }, [user]);

  async function addAccount(event: FormEvent) {
    event.preventDefault();
    await apiPost("/api/admin/accounts", { email, role: "USER" });
    setEmail("");
    await load();
  }

  async function toggleAccount(account: Account) {
    await apiPatch(`/api/admin/accounts/${account.id}`, {
      enabled: !account.enabled,
    });
    await load();
  }

  async function createBackup() {
    await apiPost("/api/admin/backups");
    await load();
  }

  async function restoreBackup(backup: Backup) {
    if (
      !window.confirm(
        `${backup.name} 시점으로 데이터를 복원할까요? 현재 데이터는 교체됩니다.`,
      )
    ) {
      return;
    }
    await apiPost("/api/admin/restore", { name: backup.name });
    window.location.reload();
  }

  if (loading) return <section className="card">불러오는 중입니다.</section>;
  if (user?.role !== "OWNER") {
    return (
      <section className="card">
        OWNER 계정만 관리 화면을 사용할 수 있습니다.
      </section>
    );
  }

  return (
    <section className="stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">OWNER 전용</p>
          <h1>서비스 관리</h1>
        </div>
      </div>
      <div className="two-column">
        <article className="card">
          <h2>허용 계정</h2>
          <form className="inline-form" onSubmit={addAccount}>
            <input
              required
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="family@example.com"
            />
            <button className="button" type="submit">
              초대
            </button>
          </form>
          <ul className="setting-list">
            {accounts.map((account) => (
              <li key={account.id}>
                <span>
                  <strong>{account.email}</strong>
                  <small>{account.role}</small>
                </span>
                <button
                  className="button button-secondary button-small"
                  disabled={account.id === user.id}
                  type="button"
                  onClick={() => toggleAccount(account)}
                >
                  {account.enabled ? "차단" : "허용"}
                </button>
              </li>
            ))}
          </ul>
        </article>
        <article className="card">
          <div className="toolbar">
            <h2>데이터 백업</h2>
            <button
              className="button button-small"
              type="button"
              onClick={createBackup}
            >
              지금 백업
            </button>
          </div>
          <p className="muted">
            SQLite 데이터베이스의 안전한 복사본을 생성합니다.
          </p>
          <ul className="setting-list">
            {backups.map((backup) => (
              <li key={backup.name}>
                <span>
                  <strong>{backup.name}</strong>
                  <small>
                    {(backup.size / 1024).toFixed(1)} KB ·{" "}
                    {new Date(backup.created_at).toLocaleString("ko-KR")}
                  </small>
                </span>
                <button
                  className="button button-secondary button-small"
                  type="button"
                  onClick={() => restoreBackup(backup)}
                >
                  복원
                </button>
              </li>
            ))}
          </ul>
        </article>
      </div>
    </section>
  );
}
