import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { API_BASE_URL, apiGet, apiPost } from "../api/client";
import type {
  CurrentUser,
  LedgerTransaction,
  TransactionSummary,
} from "../api/types";
import { useAuth } from "../auth/context";
import { Icon } from "../components/Icon";

type AuthConfig = {
  google_enabled: boolean;
  local_admin_enabled: boolean;
};

const currency = new Intl.NumberFormat("ko-KR", {
  style: "currency",
  currency: "KRW",
  maximumFractionDigits: 0,
});

function monthRange() {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), 1);
  const end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
  const format = (value: Date) =>
    new Intl.DateTimeFormat("sv-SE").format(value);
  return { start: format(start), end: format(end) };
}

export function DashboardPage() {
  const { loading, user, errorStatus } = useAuth();
  const [summary, setSummary] = useState<TransactionSummary | null>(null);
  const [transactions, setTransactions] = useState<LedgerTransaction[]>([]);
  const [authConfig, setAuthConfig] = useState<AuthConfig | null>(null);
  const [username, setUsername] = useState("SYSTEM");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [signingIn, setSigningIn] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      apiGet<AuthConfig>("/api/auth/config")
        .then(setAuthConfig)
        .catch(() =>
          setAuthConfig({ google_enabled: false, local_admin_enabled: false }),
        );
    }
  }, [loading, user]);

  useEffect(() => {
    if (!user) return;
    const range = monthRange();
    const query = `start_date=${range.start}&end_date=${range.end}`;
    Promise.all([
      apiGet<TransactionSummary>(`/api/transactions/summary?${query}`),
      apiGet<LedgerTransaction[]>(`/api/transactions?${query}&limit=200`),
    ]).then(([summaryData, transactionData]) => {
      setSummary(summaryData);
      setTransactions(transactionData);
    });
  }, [user]);

  const categoryTotals = useMemo(() => {
    const totals = new Map<string, number>();
    for (const item of transactions) {
      if (item.tx_type === "EXPENSE") {
        totals.set(
          item.category_name,
          (totals.get(item.category_name) ?? 0) + Number(item.amount),
        );
      }
    }
    return [...totals.entries()]
      .sort((left, right) => right[1] - left[1])
      .slice(0, 5);
  }, [transactions]);

  async function localLogin(event: FormEvent) {
    event.preventDefault();
    setLoginError("");
    setSigningIn(true);
    try {
      await apiPost<CurrentUser>("/auth/local-login", { username, password });
      window.location.href = "/";
    } catch (error) {
      setLoginError((error as Error).message);
      setSigningIn(false);
    }
  }

  if (loading) {
    return (
      <section className="auth-stage">
        <div className="auth-loader">
          <span />
          안전한 세션을 확인하고 있습니다
        </div>
      </section>
    );
  }

  if (!user) {
    return (
      <section className="auth-stage">
        <div className="auth-visual">
          <div className="visual-orb orb-one" />
          <div className="visual-orb orb-two" />
          <div className="auth-visual-content">
            <span className="auth-badge">
              <Icon name="spark" size={16} />
              YOUR MONEY, CLEARLY
            </span>
            <h1>
              숫자는 단순하게,
              <br />
              생활은 더 여유롭게.
            </h1>
            <p>
              가족의 모든 수입과 지출을 한눈에 파악하고, 중요한 결정에 더 많은
              시간을 쓰세요.
            </p>
            <div className="visual-metric">
              <span>이번 달 재정 리포트</span>
              <strong>한 곳에서 완성</strong>
              <div className="metric-bars">
                {[42, 66, 53, 82, 70, 91, 76].map((height, index) => (
                  <i key={index} style={{ height: `${height}%` }} />
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="auth-panel">
          <div className="auth-panel-inner">
            <span className="auth-step">SECURE ACCESS</span>
            <h2>다시 만나서 반가워요</h2>
            <p>관리자 계정으로 Home Ledger에 접속하세요.</p>

            {authConfig?.local_admin_enabled && (
              <form className="login-form" onSubmit={localLogin}>
                <label>
                  사용자 이름
                  <input
                    autoComplete="username"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                  />
                </label>
                <label>
                  비밀번호
                  <input
                    required
                    autoComplete="current-password"
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="비밀번호를 입력하세요"
                  />
                </label>
                {loginError && <p className="login-error">{loginError}</p>}
                <button
                  className="button login-button"
                  disabled={signingIn}
                  type="submit"
                >
                  {signingIn ? "접속 확인 중..." : "관리자로 로그인"}
                  <span>→</span>
                </button>
              </form>
            )}

            {authConfig?.google_enabled && authConfig.local_admin_enabled && (
              <div className="auth-divider">
                <span>또는</span>
              </div>
            )}
            {authConfig?.google_enabled && (
              <a className="google-button" href={`${API_BASE_URL}/auth/login`}>
                <span className="google-mark">G</span>
                Google 계정으로 계속하기
              </a>
            )}
            {authConfig &&
              !authConfig.google_enabled &&
              !authConfig.local_admin_enabled && (
                <p className="login-error">
                  사용할 수 있는 로그인 방식이 없습니다. 서버 환경 설정을
                  확인하세요.
                </p>
              )}
            {errorStatus === 403 && (
              <p className="login-error">
                이 계정은 사용 허용 목록에 없습니다.
              </p>
            )}

            <div className="auth-footnote">
              <Icon name="lock" size={14} />
              로그인 정보는 암호화된 세션으로만 처리됩니다.
            </div>
          </div>
        </div>
      </section>
    );
  }

  const income = Number(summary?.income ?? 0);
  const expense = Number(summary?.expense ?? 0);
  const balance = Number(summary?.balance ?? 0);
  const expenseRatio = income > 0 ? Math.min((expense / income) * 100, 100) : 0;
  const maxCategory = categoryTotals[0]?.[1] ?? 1;
  const displayName =
    user.email === "system@local" ? "SYSTEM" : user.email.split("@")[0];

  return (
    <section className="dashboard">
      <div className="dashboard-heading">
        <div>
          <span className="section-label">OVERVIEW</span>
          <h1>{displayName}님, 오늘도 좋은 하루예요.</h1>
          <p>이번 달 우리 집의 재정 흐름을 정리했어요.</p>
        </div>
        <Link className="button primary-action" to="/transactions">
          <Icon name="plus" size={18} />새 거래
        </Link>
      </div>

      <div className="summary-grid">
        <article className="balance-card">
          <div className="balance-card-top">
            <span>이번 달 잔액</span>
            <span className="glass-icon">
              <Icon name="wallet" />
            </span>
          </div>
          <strong>{currency.format(balance)}</strong>
          <p>수입에서 지출을 제외한 금액</p>
          <div className="balance-progress">
            <span style={{ width: `${100 - expenseRatio}%` }} />
          </div>
          <small>수입의 {Math.round(100 - expenseRatio)}%가 남아 있어요</small>
        </article>

        <article className="metric-card">
          <span className="metric-icon income">
            <Icon name="arrow-up" />
          </span>
          <div>
            <span className="metric-label">총 수입</span>
            <strong>{currency.format(income)}</strong>
            <small>이번 달 유입 금액</small>
          </div>
        </article>

        <article className="metric-card">
          <span className="metric-icon expense">
            <Icon name="arrow-down" />
          </span>
          <div>
            <span className="metric-label">총 지출</span>
            <strong>{currency.format(expense)}</strong>
            <small>이번 달 사용 금액</small>
          </div>
        </article>
      </div>

      <div className="dashboard-grid">
        <article className="card spending-card">
          <div className="card-heading">
            <div>
              <span className="section-label">SPENDING</span>
              <h2>카테고리별 지출</h2>
            </div>
            <span className="period-chip">이번 달</span>
          </div>
          {categoryTotals.length ? (
            <div className="category-chart">
              {categoryTotals.map(([name, value], index) => (
                <div className="category-row" key={name}>
                  <div className="category-meta">
                    <span>
                      <i className={`category-dot color-${index}`} />
                      {name}
                    </span>
                    <strong>{currency.format(value)}</strong>
                  </div>
                  <div className="category-track">
                    <span
                      className={`color-${index}`}
                      style={{ width: `${(value / maxCategory) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="chart-empty">
              <Icon name="receipt" size={28} />
              <strong>아직 지출 기록이 없어요</strong>
              <span>첫 거래를 추가하면 분석이 시작됩니다.</span>
            </div>
          )}
        </article>

        <article className="card recent-card">
          <div className="card-heading">
            <div>
              <span className="section-label">ACTIVITY</span>
              <h2>최근 거래</h2>
            </div>
            <Link to="/transactions">전체 보기 →</Link>
          </div>
          {transactions.length ? (
            <div className="recent-list">
              {transactions.slice(0, 5).map((item) => (
                <div className="recent-item" key={item.id}>
                  <span
                    className={`transaction-icon ${item.tx_type.toLowerCase()}`}
                  >
                    <Icon
                      name={
                        item.tx_type === "INCOME" ? "arrow-up" : "arrow-down"
                      }
                      size={18}
                    />
                  </span>
                  <span className="recent-copy">
                    <strong>{item.description || item.category_name}</strong>
                    <small>
                      {item.category_name} · {item.tx_date}
                    </small>
                  </span>
                  <strong
                    className={
                      item.tx_type === "INCOME" ? "positive" : "negative"
                    }
                  >
                    {item.tx_type === "INCOME" ? "+" : "-"}
                    {currency.format(Number(item.amount))}
                  </strong>
                </div>
              ))}
            </div>
          ) : (
            <div className="recent-empty">표시할 거래가 없습니다.</div>
          )}
        </article>
      </div>
    </section>
  );
}
