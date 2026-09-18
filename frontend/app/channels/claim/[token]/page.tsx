"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError } from "@/lib/api";
import { Header, Footer } from "@/components/campus-app";

type ClaimChannel = { name: string; bio: string };

export default function Page({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const [channel, setChannel] = useState<ClaimChannel | null>(null);
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    params.then(({ token }) =>
      fetch(
        `${(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "")}/api/channels/claim/${encodeURIComponent(token)}/`,
        { headers: { Accept: "application/json" } },
      )
        .then(async (response) => {
          const body = await response.json().catch(() => ({}));
          if (!response.ok)
            throw new ApiError(
              response.status,
              typeof body?.detail === "string"
                ? body.detail
                : "This claim link is no longer available.",
            );
          setChannel(body as ClaimChannel);
        })
        .catch((reason) =>
          setError(
            reason instanceof ApiError
              ? reason.message
              : "We could not load this claim link.",
          ),
        )
        .finally(() => setLoading(false)),
    );
  }, [params]);

  const confirm = async () => {
    setConfirming(true);
    setError("");
    try {
      const { token } = await params;
      const response = await fetch(
        `${(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "")}/api/channels/claim/${encodeURIComponent(token)}/confirm/`,
        { method: "POST", headers: { Accept: "application/json" } },
      );
      const body = await response.json().catch(() => ({}));
      if (!response.ok)
        throw new ApiError(
          response.status,
          typeof body?.detail === "string"
            ? body.detail
            : "We could not confirm this claim.",
        );
      setConfirmed(true);
    } catch (reason) {
      setError(
        reason instanceof ApiError
          ? reason.message
          : "We could not confirm this claim.",
      );
    } finally {
      setConfirming(false);
    }
  };

  return (
    <>
      <Header />
      <main className="page">
        <div className="container narrow">
          <span className="eyebrow">CHANNEL CLAIM</span>
          {loading ? (
            <p className="large-copy">Loading claim details…</p>
          ) : error ? (
            <>
              <h1>Claim unavailable</h1>
              <p className="large-copy">{error}</p>
              <Link href="/channels" className="button primary">
                View channels
              </Link>
            </>
          ) : confirmed ? (
            <div className="success">
              <div className="success-mark">✓</div>
              <h1>Claim submitted</h1>
              <p className="large-copy">
                Thanks for confirming {channel?.name}. A super_admin still needs
                to give final approval before this channel goes live.
              </p>
              <Link href="/channels" className="button primary">
                Back to channels
              </Link>
            </div>
          ) : channel ? (
            <>
              <h1>{channel.name}</h1>
              <p className="large-copy">{channel.bio}</p>
              <button
                className="button primary"
                onClick={confirm}
                disabled={confirming}
              >
                {confirming ? "Confirming…" : "Confirm channel"}
              </button>
            </>
          ) : null}
        </div>
      </main>
      <Footer />
    </>
  );
}
