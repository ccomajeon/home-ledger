import { render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import App from "./App";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("App", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders local administrator login when it is enabled", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/api/me")) {
          return Promise.resolve(
            jsonResponse({ detail: "Authentication required" }, 401),
          );
        }
        if (url.endsWith("/api/auth/config")) {
          return Promise.resolve(
            jsonResponse({ google_enabled: false, local_admin_enabled: true }),
          );
        }
        throw new Error(`Unexpected URL: ${url}`);
      }),
    );

    render(<App />);

    expect(
      await screen.findByRole("heading", { name: "다시 만나서 반가워요" }),
    ).toBeInTheDocument();
    expect(await screen.findByLabelText("사용자 이름")).toHaveValue("SYSTEM");
    expect(
      screen.getByRole("button", { name: /관리자로 로그인/ }),
    ).toBeInTheDocument();
  });

  it("renders the finance dashboard for an owner", async () => {
    const fetchMock = vi.fn().mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/api/me")) {
        return Promise.resolve(
          jsonResponse({
            id: 1,
            email: "system@local",
            role: "OWNER",
            enabled: true,
            created_at: "2026-07-19T00:00:00",
          }),
        );
      }
      if (url.includes("/api/transactions/summary")) {
        return Promise.resolve(
          jsonResponse({
            income: "100000",
            expense: "25000",
            balance: "75000",
          }),
        );
      }
      if (url.includes("/api/transactions?")) {
        return Promise.resolve(jsonResponse([]));
      }
      throw new Error(`Unexpected URL: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    expect(
      await screen.findByText("SYSTEM님, 오늘도 좋은 하루예요."),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /서비스 관리/ }),
    ).toBeInTheDocument();
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));
  });
});
