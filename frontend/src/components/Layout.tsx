import { Link } from "react-router-dom";
import type { PropsWithChildren } from "react";

export function Layout({ children }: PropsWithChildren) {
  return (
    <div className="layout">
      <header className="header">
        <h1 className="title">Home Ledger</h1>
        <nav className="nav">
          <Link to="/">Dashboard</Link>
          <Link to="/403">Not Authorized</Link>
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}

