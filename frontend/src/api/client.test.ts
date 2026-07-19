import { afterEach, describe, expect, it, vi } from "vitest";
import { apiGet, apiPost, ApiError } from "./client";

describe("API client", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("sends JSON with the session cookie", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        new Response(JSON.stringify({ ok: true }), { status: 200 }),
      );
    vi.stubGlobal("fetch", fetchMock);

    await apiPost("/api/example", { name: "테스트" });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/example",
      expect.objectContaining({
        credentials: "include",
        method: "POST",
        body: JSON.stringify({ name: "테스트" }),
      }),
    );
  });

  it("uses the API detail when a request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Account is not allowed" }), {
          status: 403,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    try {
      await apiGet("/api/me");
      throw new Error("Expected the request to fail");
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(403);
      expect((error as ApiError).message).toBe("Account is not allowed");
    }
  });
});
