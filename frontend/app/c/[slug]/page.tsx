import Link from "next/link";
import { Header, Footer } from "@/components/campus-app";
import { FollowButton } from "@/components/follow-button";
import {
  ApiError,
  getCategories,
  getChannel,
  getInstitutions,
} from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  try {
    const [channel, categories, institutions] = await Promise.all([
      getChannel(slug),
      getCategories(),
      getInstitutions(),
    ]);
    const category = categories.find(
      (item) => item.id === channel.category_focus,
    )?.name;
    const institution = institutions.find(
      (item) => item.id === channel.institution,
    )?.name;
    return (
      <>
        <Header />
        <main className="page">
          <div className="container page-intro">
            <span className="eyebrow">CAMPUS CHANNEL</span>
            <h1>{channel.name}</h1>
            <p>
              {channel.bio}{" "}
              {institution && (
                <>
                  <b>{institution}.</b>{" "}
                </>
              )}
              {channel.follower_count} followers.
            </p>
            <FollowButton target={{ channel: channel.slug }} />
            {category && <span className="category-pill">{category}</span>}
          </div>
          {channel.posts?.length ? (
            <section className="container post-grid">
              {channel.posts.map((post) => (
                <article className="post-card" key={post.id}>
                  <div className="post-top">
                    <span className="category-pill">
                      {categories.find((item) => item.id === post.category)
                        ?.name || "Community"}
                    </span>
                    <span className="post-time">
                      {new Date(post.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <Link href={`/post/${post.id}`}>
                    <h3>{post.title}</h3>
                  </Link>
                  <p>{post.content}</p>
                </article>
              ))}
            </section>
          ) : (
            <div className="container narrow">
              <p className="large-copy">
                No approved posts in this channel yet.
              </p>
            </div>
          )}
        </main>
        <Footer />
      </>
    );
  } catch (error) {
    const message =
      error instanceof ApiError
        ? error.message
        : "We could not load this channel.";
    return (
      <>
        <Header />
        <main className="page">
          <div className="container narrow">
            <h1>Channel unavailable</h1>
            <p className="large-copy">{message}</p>
            <Link href="/channels" className="button primary">
              View channels
            </Link>
          </div>
        </main>
        <Footer />
      </>
    );
  }
}
