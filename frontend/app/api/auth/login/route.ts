import { NextResponse } from "next/server";

const API_URL = (
  typeof window === "undefined"
    ? process.env.BACKEND_INTERNAL_URL || "http://backend:8000"
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

).replace(/\/$/, "");

export async function POST(request: Request) {
  const body = await request.text();
  const response = await fetch(`${API_URL}/api/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  const payload = await response.json();
  if (!response.ok)
    return NextResponse.json(payload, { status: response.status });

  const result = NextResponse.json({ ok: true });
  for (const [name, value] of [
    ["admin_access", payload.access],
    ["admin_refresh", payload.refresh],
  ] as const) {
    result.cookies.set(name, value, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: name === "admin_access" ? 60 * 15 : 60 * 60 * 24 * 7,
    });
  }
  return result;
}
