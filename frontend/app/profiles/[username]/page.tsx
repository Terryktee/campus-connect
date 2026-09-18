"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Footer, Header } from "@/components/public-api-pages";
import {
  getCategories,
  getInstitutions,
  getPosts,
  type ApiCategory,
  type ApiInstitution,
  type ApiPost,
} from "@/lib/api";

type ProfileRecord = {
  username: string;
  name: string;
  institution: string;
  programme: string;
  description: string;
  tags: string[];
  accent: string;
};

export default function Page({
  params,
}: {
  params: Promise<{ username: string }>;
}) {
  const [profile, setProfile] = useState<ProfileRecord | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    void (async () => {
      try {
        const { username } = await params;
        const [posts, categories, institutions] = await Promise.all([
          getPosts(),
          getCategories(),
          getInstitutions(),
        ]);

        const match = posts.find(
          (post) =>
            (post.submitter_name || "").toLowerCase().replace(/\s+/g, ".") ===
            username.toLowerCase(),
        );
        if (!match || !active) return;

        const name = match.submitter_name || "Campus member";
        const institution =
          institutions.find((item) => item.id === match.institution)?.name ||
          "Campus community";
        const programme =
          categories.find((item) => item.id === match.category)?.name ||
          "Community";

        setProfile({
          username: username.toLowerCase(),
          name,
          institution,
          programme,
          description:
            match.content || "Student profile details are not yet available.",
          tags: [programme],
          accent: ["green", "ochre", "coral"][Math.abs(username.length) % 3],
        });
      } catch {
        if (active) setProfile(null);
      } finally {
        if (active) setLoading(false);
      }
    })();

    return () => {
      active = false;
    };
  }, [params]);

  if (loading)
    return (
      <>
        <Header />
        <main className="page">
          <div className="container narrow">
            <p className="large-copy">Loading profile…</p>
          </div>
        </main>
        <Footer />
      </>
    );

  if (!profile)
    return (
      <>
        <Header />
        <main className="page">
          <div className="container narrow">
            <h1>Profile not found</h1>
            <Link href="/profiles" className="button primary">
              Browse profiles
            </Link>
          </div>
        </main>
        <Footer />
      </>
    );

  return (
    <>
      <Header />
      <main className="page">
        <div className={`container profile-detail ${profile.accent}`}>
          <Link href="/profiles" className="text-link">
            ← All profiles
          </Link>
          <div className="profile-avatar large">
            {profile.name
              .split(" ")
              .map((name) => name[0])
              .join("")
              .slice(0, 2)}
          </div>
          <span className="profile-handle">@{profile.username}</span>
          <h1>{profile.name}</h1>
          <p className="large-copy">{profile.description}</p>
          <p>
            {profile.programme} · {profile.institution}
          </p>
          <div className="tag-row">
            {profile.tags.map((tag) => (
              <span key={tag}>{tag}</span>
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
