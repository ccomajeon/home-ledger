import type { PropsWithChildren } from "react";
import { NavLink } from "react-router-dom";
import { API_BASE_URL } from "../api/client";
import { useAuth } from "../auth/context";
import { Icon } from "./Icon";

const navigation = [
  { to: "/", label: "대시보드", icon: "home" as const, end: true },
  { to: "/transactions", label: "거래 내역", icon: "receipt" as const },
  { to: "/settings", label: "가계부 설정", icon: "settings" as const },
];

const today = new Intl.DateTimeFormat("ko-KR", {
  month: "long",
  day: "numeric",
  weekday: "long",
}).format(new Date());

function Logo() {
  return (
    <NavLink className="product-logo" to="/">
      <span className="logo-symbol">
        <Icon name="wallet" size={22} />
      </span>
      <span>
        <strong>Home Ledger</strong>
        <small>HOUSEHOLD FINANCE</small>
      </span>
    </NavLink>
  );
}

export function Layout({ children }: PropsWithChildren) {
  const { user, loading } = useAuth();
  const displayName =
    user?.email === "system@local" ? "SYSTEM" : user?.email.split("@")[0];

  if (!user) {
    return (
      <div className={`public-shell ${loading ? "is-loading" : ""}`}>
        <header className="public-header">
          <Logo />
          <span className="secure-label">
            <Icon name="lock" size={15} />
            Private finance workspace
          </span>
        </header>
        <main>{children}</main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Logo />
        <div className="sidebar-caption">WORKSPACE</div>
        <nav className="side-nav">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              className={({ isActive }) => (isActive ? "active" : "")}
              end={item.end}
              to={item.to}
            >
              <Icon name={item.icon} />
              <span>{item.label}</span>
            </NavLink>
          ))}
          {user.role === "OWNER" && (
            <NavLink
              className={({ isActive }) => (isActive ? "active" : "")}
              to="/admin"
            >
              <Icon name="shield" />
              <span>서비스 관리</span>
            </NavLink>
          )}
        </nav>
        <div className="sidebar-spacer" />
        <div className="sidebar-user">
          <span className="user-avatar">
            {displayName?.slice(0, 2).toUpperCase()}
          </span>
          <span className="user-copy">
            <strong>{displayName}</strong>
            <small>{user.role} ACCOUNT</small>
          </span>
          <form action={`${API_BASE_URL}/auth/logout`} method="post">
            <button aria-label="로그아웃" type="submit">
              <Icon name="logout" size={18} />
            </button>
          </form>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div>
            <span className="topbar-kicker">PERSONAL FINANCE</span>
            <strong>{today}</strong>
          </div>
          <div className="topbar-account">
            <span className="status-dot" />
            {displayName}으로 접속 중
          </div>
        </header>
        <main className="page-content">{children}</main>
      </div>

      <nav className="mobile-nav">
        {navigation.map((item) => (
          <NavLink
            key={item.to}
            className={({ isActive }) => (isActive ? "active" : "")}
            end={item.end}
            to={item.to}
          >
            <Icon name={item.icon} size={19} />
            <span>{item.label.replace("가계부 ", "")}</span>
          </NavLink>
        ))}
        {user.role === "OWNER" && (
          <NavLink
            className={({ isActive }) => (isActive ? "active" : "")}
            to="/admin"
          >
            <Icon name="shield" size={19} />
            <span>관리</span>
          </NavLink>
        )}
      </nav>
    </div>
  );
}
