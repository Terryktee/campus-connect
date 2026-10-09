"use client";

import Link from "next/link";
import {
  Bell,
  CalendarDays,
  ChartNoAxesColumn,
  Menu,
  Search,
  ShieldCheck,
  Sparkles,
  UserRound,
  X,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { FollowButton } from "@/components/follow-button";
import {
  ApiError,
  ApiPost,
  getCategories,
  getChannel,
  getChannels,
  getInstitutions,
  getOrientationGuides,
  getPosts,
  submitPost,
  type ApiCategory,
  type ApiChannel,
  type ApiInstitution,
  type ApiOrientationGuide,
} from "@/lib/api";

const footerLinks = {
  Explore: [
    ["Home", "/"],
    ["Channels", "/channels"],
    ["Profiles", "/profiles"],
    ["Events", "/events"],
  ],
  Info: [
    ["Orientation", "/orientation"],
    ["Guidelines", "/guidelines"],
    ["Contact", "/contact"],
    ["Privacy", "/privacy"],
  ],
  Community: [
    ["Submit a post", "/submit"],
    ["Analytics", "/analytics"],
  ],
};

export function Header() {
  const [open, setOpen] = useState(false);

  return (
    <header className="site-header">
      <div className="container nav">
        <Link href="/" className="brand">
          <span className="brand-mark">L</span>
          <span>Loop</span>
        </Link>
        <nav className={open ? "nav-links open" : "nav-links"}>
          <Link href="/">Explore</Link>
          <Link href="/channels">Channels</Link>
          <Link href="/profiles">Profiles</Link>
          <Link href="/events">Events</Link>
          <Link href="/orientation">Orientation Hub</Link>
          <Link href="/submit" className="nav-cta">
            Submit a Post <span>+</span>
          </Link>
        </nav>
        <div className="nav-actions">
          <Link
            href="/analytics"
            className="icon-button"
            aria-label="Analytics"
          >
            <ChartNoAxesColumn />
          </Link>
          <button className="icon-button" aria-label="Search">
            <Search />
          </button>
          <button className="icon-button" aria-label="Notifications">
            <Bell />
          </button>
          <button
            className="menu-button"
            onClick={() => setOpen(!open)}
            aria-label="Menu"
          >
            {open ? <X /> : <Menu />}
          </button>
        </div>
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer>
      <div className="container footer-grid">
        <div>
          <Link href="/" className="brand">
            <span className="brand-mark">L</span>
            <span>Loop</span>
          </Link>
          <p className="muted footer-copy">
            The open platform for youth worldwide.
            <br />
            Find your people. Share what matters.
          </p>
        </div>
        {Object.entries(footerLinks).map(([title, links]) => (
          <div key={title}>
            <h4>{title}</h4>
            {links.map(([label, href]) => (
              <Link href={href} key={href}>
                {label}
              </Link>
            ))}
          </div>
        ))}
      </div>
      <div className="container footer-bottom">
        <span>© 2026 Loop</span>
        <span>Made for youth, by youth.</span>
      </div>
    </footer>
  );
}

function State({ message, retry }: { message: string; retry?: () => void }) {
  return (
    <div className="container narrow" role="status">
      <p className="large-copy">{message}</p>
      {retry && (
        <button className="button primary" onClick={retry}>
          Try again
        </button>
      )}
    </div>
  );
}

function postView(
  post: ApiPost,
  categories: ApiCategory[],
  institutions: ApiInstitution[],
  channels: ApiChannel[],
) {
  return {
    ...post,
    categoryName:
      categories.find((item) => item.id === post.category)?.name || "Community",
    institutionName:
      institutions.find((item) => item.id === post.institution)?.name || "",
    channelName: channels.find((item) => item.id === post.channel)?.name || "",
  };
}

export function ApiHome() {
  const [posts, setPosts] = useState<ApiPost[]>([]);
  const [categories, setCategories] = useState<ApiCategory[]>([]);
  const [institutions, setInstitutions] = useState<ApiInstitution[]>([]);
  const [channels, setChannels] = useState<ApiChannel[]>([]);
  const [active, setActive] = useState("all");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    setError("");
    Promise.all([getPosts(), getCategories(), getInstitutions(), getChannels()])
      .then(([postData, categoryData, institutionData, channelData]) => {
        setPosts(postData);
        setCategories(categoryData);
        setInstitutions(institutionData);
        setChannels(channelData);
      })
      .catch((reason: unknown) =>
        setError(
          reason instanceof ApiError
            ? reason.message
            : "We could not load the noticeboard.",
        ),
      )
      .finally(() => setLoading(false));
  };
  useEffect(load, []);

  const visible = useMemo(
    () =>
      posts
        .filter((post) => active === "all" || post.category === Number(active))
        .map((post) => postView(post, categories, institutions, channels)),
    [posts, categories, institutions, channels, active],
  );

  return (
    <>
      <Header />
      <main>
        <section className="hero">
          <div className="container hero-grid">
            <div>
              <span className="eyebrow">THE STUDENT NOTICEBOARD</span>
              <h1>
                What&apos;s happening
                <br />
                <i>on campus?</i>
              </h1>
              <p className="hero-copy">
                Community news, opportunities, and voices for youth worldwide.
                Find your people, share what matters, and make your voice heard.
              </p>
              <div className="hero-actions">
                <Link href="/submit" className="button primary">
                  Submit a Post <span>→</span>
                </Link>
                <Link href="/orientation" className="button ghost">
                  New here? Start here
                </Link>
              </div>
            </div>
          </div>
        </section>
        <section className="container feed-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">FROM THE COMMUNITY</span>
              <h2>Fresh on the noticeboard</h2>
            </div>
            <Link href="/channels" className="text-link">
              Explore channels →
            </Link>
          </div>
          {loading ? (
            <State message="Loading the latest posts…" />
          ) : error ? (
            <State message={error} retry={load} />
          ) : (
            <>
              {" "}
              <div className="category-row">
                <button
                  className={active === "all" ? "category active" : "category"}
                  onClick={() => setActive("all")}
                >
                  All posts
                </button>
                {categories.map((category) => (
                  <div className="category-follow" key={category.id}>
                    <button
                      className={
                        active === String(category.id)
                          ? "category active"
                          : "category"
                      }
                      onClick={() => setActive(String(category.id))}
                    >
                      {category.name}
                    </button>
                    <FollowButton
                      target={{ category: category.slug }}
                      label="Follow"
                    />
                  </div>
                ))}
              </div>
              {visible.length ? (
                <div className="post-grid">
                  {visible.map((post, index) => (
                    <article
                      className={
                        index === 0 && active === "all"
                          ? "post-card featured"
                          : "post-card"
                      }
                      key={post.id}
                    >
                      <div className="post-top">
                        <span className="category-pill">
                          {post.categoryName}
                        </span>
                        <span className="post-time">
                          {new Date(post.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <Link href={`/post/${post.id}`}>
                        <h3>{post.title}</h3>
                      </Link>
                      <p>{post.content}</p>
                      <div className="post-meta">
                        <span className="avatar">
                          {(post.submitter_name || "C").charAt(0)}
                        </span>
                        <span>
                          {post.channelName ||
                            post.institutionName ||
                            post.submitter_name ||
                            "Loop"}
                        </span>
                        <span className="meta-spacer" />
                      </div>
                    </article>
                  ))}
                </div>
              ) : (
                <State message="No approved posts match this category yet." />
              )}
            </>
          )}
        </section>
      </main>
      <Footer />
    </>
  );
}

export function ApiChannels() {
  const [channels, setChannels] = useState<ApiChannel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    getChannels()
      .then(setChannels)
      .catch((reason: unknown) =>
        setError(
          reason instanceof ApiError
            ? reason.message
            : "We could not load channels.",
        ),
      )
      .finally(() => setLoading(false));
  }, []);
  return (
    <>
      <Header />
      <main className="page">
        <div className="container page-intro">
          <span className="eyebrow">FIND YOUR PEOPLE</span>
          <h1>Campus channels</h1>
          <p>
            Join focused communities with their own description, conversations
            and opportunities.
          </p>
        </div>
        {loading ? (
          <State message="Loading channels…" />
        ) : error ? (
          <State message={error} />
        ) : channels.length ? (
          <div className="container channel-grid">
            {channels.map((channel) => (
              <div className="channel-card green" key={channel.id}>
                <Link href={`/c/${channel.slug}`} className="channel-badge">
                  {channel.name.slice(0, 3).toUpperCase()}
                </Link>
                <div>
                  <Link href={`/c/${channel.slug}`}>
                    <h3>{channel.name}</h3>
                  </Link>
                  <p>{channel.bio}</p>
                  <span>{channel.follower_count} followers</span>
                  <FollowButton target={{ channel: channel.slug }} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <State message="No active channels are available yet." />
        )}
      </main>
      <Footer />
    </>
  );
}

export function ApiSubmit() {
  const [sent, setSent] = useState(false);
  const [categories, setCategories] = useState<ApiCategory[]>([]);
  const [institutions, setInstitutions] = useState<ApiInstitution[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});

  useEffect(() => {
    Promise.all([getCategories(), getInstitutions()])
      .then(([categoryData, institutionData]) => {
        setCategories(categoryData);
        setInstitutions(institutionData);
      })
      .catch(() => setError("We could not load form options."));
  }, []);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setFieldErrors({});
    setSubmitting(true);

    const data = new FormData(event.currentTarget);
    try {
      await submitPost({
        title: String(data.get("title") || ""),
        content: String(data.get("content") || ""),
        category: String(data.get("category") || ""),
        institution: String(data.get("institution") || ""),
        channel_name: String(data.get("channel_name") || ""),
        submitter_name: String(data.get("submitter_name") || ""),
        submitter_contact: String(data.get("submitter_contact") || ""),
        link_url: String(data.get("link_url") || ""),
        image_url: "",
        submitter_institution: String(data.get("submitter_institution") || ""),
        website: String(data.get("website") || ""),
      });
      setSent(true);
    } catch (reason) {
      if (reason instanceof ApiError) {
        setFieldErrors(reason.fieldErrors);
        setError(reason.message);
      } else {
        setError("The submission could not be sent. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  const fieldError = (name: string) => fieldErrors[name]?.join(" ") || "";
  const fieldProps = (name: string) => ({
    "aria-invalid": Boolean(fieldError(name)),
    "aria-describedby": fieldError(name) ? `${name}-error` : undefined,
  });

  return (
    <>
      <Header />
      <main className="page">
        <div className="container submit-layout">
          <div className="page-intro">
            <span className="eyebrow">ADD TO THE CONVERSATION</span>
            <h1>
              Share something
              <br />
              <i>with campus.</i>
            </h1>
            <p>Useful, kind and relevant. That&apos;s the whole brief.</p>
            <div className="submit-aside">
              <ShieldCheck />
              <span>
                Every post is reviewed before it goes live. Private contact
                details stay private.
              </span>
            </div>
          </div>
          <div className="form-card">
            {sent ? (
              <div className="success">
                <div className="success-mark">✓</div>
                <h2>Thanks — your post is in review.</h2>
                <p>It will appear once approved, usually within 24 hours.</p>
                <Link href="/" className="button primary">
                  Back to explore
                </Link>
              </div>
            ) : (
              <form onSubmit={handleSubmit} noValidate>
                <label>
                  Title *
                  <input
                    name="title"
                    required
                    placeholder="Keep it short and clear"
                    {...fieldProps("title")}
                  />
                  {fieldError("title") && (
                    <small className="form-error" id="title-error">
                      {fieldError("title")}
                    </small>
                  )}
                </label>
                <div className="form-two">
                  <label>
                    Institution *
                    <select
                      name="institution"
                      required
                      defaultValue={institutions[0]?.name || ""}
                      {...fieldProps("institution")}
                    >
                      {institutions.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.name}
                        </option>
                      ))}
                    </select>
                    {fieldError("institution") && (
                      <small className="form-error" id="institution-error">
                        {fieldError("institution")}
                      </small>
                    )}
                  </label>
                  <label>
                    Channel name (optional)
                    <input
                      name="channel_name"
                      placeholder="e.g. Women in STEM"
                      {...fieldProps("channel_name")}
                    />
                    {fieldError("channel_name") && (
                      <small className="form-error" id="channel_name-error">
                        {fieldError("channel_name")}
                      </small>
                    )}
                  </label>
                </div>
                <label>
                  Category *
                  <select
                    name="category"
                    required
                    defaultValue={categories[0]?.name || ""}
                    {...fieldProps("category")}
                  >
                    {categories.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                  {fieldError("category") && (
                    <small className="form-error" id="category-error">
                      {fieldError("category")}
                    </small>
                  )}
                </label>
                <label>
                  Content *
                  <textarea
                    name="content"
                    required
                    placeholder="Add the useful details..."
                    rows={6}
                    {...fieldProps("content")}
                  />
                  {fieldError("content") && (
                    <small className="form-error" id="content-error">
                      {fieldError("content")}
                    </small>
                  )}
                </label>
                <label>
                  Post as username or name *
                  <input
                    name="submitter_name"
                    required
                    placeholder="e.g. nyasha.codes or Nyasha Moyo"
                    {...fieldProps("submitter_name")}
                  />
                  <small>
                    Choose the username or name you want students to see.
                  </small>
                  {fieldError("submitter_name") && (
                    <small className="form-error" id="submitter_name-error">
                      {fieldError("submitter_name")}
                    </small>
                  )}
                </label>
                <label>
                  Optional external link
                  <input
                    name="link_url"
                    type="url"
                    placeholder="https://..."
                    {...fieldProps("link_url")}
                  />
                  <small>Only share a relevant external resource.</small>
                  {fieldError("link_url") && (
                    <small className="form-error" id="link_url-error">
                      {fieldError("link_url")}
                    </small>
                  )}
                </label>
                <label>
                  Contact email or phone *
                  <input
                    name="submitter_contact"
                    required
                    placeholder="Private contact details"
                    {...fieldProps("submitter_contact")}
                  />
                  <small>
                    Only used if we need to reach you about this post, never
                    shown publicly.
                  </small>
                  {fieldError("submitter_contact") && (
                    <small className="form-error" id="submitter_contact-error">
                      {fieldError("submitter_contact")}
                    </small>
                  )}
                </label>
                <label className="sr-only">
                  Website
                  <input name="website" tabIndex={-1} autoComplete="off" />
                </label>
                {error && (
                  <p className="form-error" role="alert">
                    {error}
                  </p>
                )}
                <button
                  className="button primary"
                  type="submit"
                  disabled={submitting}
                >
                  {submitting ? "Sending…" : "Submit for review"}{" "}
                  {!submitting && <span>→</span>}
                </button>
                <small>
                  By posting, you agree to our{" "}
                  <Link href="/guidelines">posting guidelines</Link>.
                </small>
              </form>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

export function ApiOrientation() {
  const [institutions, setInstitutions] = useState<ApiInstitution[]>([]);
  const [selected, setSelected] = useState("");
  const [guideGroups, setGuideGroups] = useState<Record<
    ApiOrientationGuide["guide_type"],
    ApiOrientationGuide[]
  > | null>(null);
  const [posts, setPosts] = useState<ApiPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([getInstitutions(), getPosts()])
      .then(([institutionData, postData]) => {
        if (!active) return;
        setInstitutions(institutionData);
        setPosts(postData.slice(0, 5));
        const initial = institutionData[0]?.name || "";
        setSelected(initial);
      })
      .catch(() => {
        if (active) setError("Orientation content could not be loaded.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const selectedInstitution = institutions.find(
    (item) => item.name === selected,
  );

  useEffect(() => {
    if (!selectedInstitution) return;
    let active = true;
    setGuideGroups(null);
    setLoading(true);
    setError("");
    getOrientationGuides(selectedInstitution.short_code)
      .then((data) => {
        if (active) setGuideGroups(data);
      })
      .catch((reason) => {
        if (active)
          setError(
            reason instanceof ApiError
              ? reason.message
              : "Orientation content could not be loaded.",
          );
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [selectedInstitution]);

  const howTo = guideGroups?.how_to || [];
  const directoryEntries = guideGroups?.directory_entry || [];
  const mapNotes = guideGroups?.campus_map_note || [];
  const hasGuides =
    howTo.length + directoryEntries.length + mapNotes.length > 0;

  return (
    <>
      <Header />
      <main className="page">
        <div className="container orientation-grid">
          <div className="page-intro">
            <span className="eyebrow">A SMALL HEAD START</span>
            <h1>
              New here?
              <br />
              <i>Start here.</i>
            </h1>
            <p>A friendly guide to the bits no one puts in the prospectus.</p>
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              aria-label="Choose your institution"
            >
              {institutions.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </div>
          <div aria-live="polite">
            {loading ? (
              <p className="orientation-state">Loading orientation content…</p>
            ) : error ? (
              <p className="orientation-state form-error" role="alert">
                {error}
              </p>
            ) : !hasGuides ? (
              <p className="orientation-state">
                Orientation content for {selected} is coming soon.
              </p>
            ) : (
              <div className="guide-stack">
                {howTo.map((guide, index) => (
                  <details key={guide.id} open={index === 0}>
                    <summary>
                      <span>{String(index + 1).padStart(2, "0")}</span>
                      {guide.title}
                      <span>⌄</span>
                    </summary>
                    <p>{guide.content}</p>
                  </details>
                ))}
              </div>
            )}
          </div>
        </div>
        {!loading && !error && hasGuides && (
          <>
            <section className="container orientation-section">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">WHO DO I ASK?</span>
                  <h2>Useful campus contacts</h2>
                </div>
              </div>
              <div className="orientation-table">
                {directoryEntries.map((guide) => (
                  <div className="orientation-table-row" key={guide.id}>
                    <div>
                      <h3>{guide.title}</h3>
                      <p>{guide.content}</p>
                    </div>
                    <strong>{guide.contact_info}</strong>
                  </div>
                ))}
              </div>
            </section>
            <section className="container orientation-section">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">FIND YOUR WAY</span>
                  <h2>Campus map notes</h2>
                </div>
              </div>
              <div className="map-notes">
                {mapNotes.map((guide) => (
                  <article className="map-note" key={guide.id}>
                    <h3>{guide.title}</h3>
                    <p>{guide.content}</p>
                  </article>
                ))}
              </div>
            </section>
          </>
        )}
        <section className="container events">
          <div className="section-heading">
            <div>
              <span className="eyebrow">{selected.toUpperCase()}</span>
              <h2>This week&apos;s orientation events</h2>
            </div>
            <Link href="/events/new" className="text-link">
              Suggest an event →
            </Link>
          </div>
          <div className="event-row">
            {posts.map((post) => (
              <div className="event" key={post.id}>
                <strong>
                  {new Date(post.created_at).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                  })}
                </strong>
                <span className="category-pill">{post.title}</span>
                <h3>{post.title}</h3>
                <p>{post.content}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

export function ApiInstitutions({
  children,
}: {
  children: (institutions: ApiInstitution[]) => React.ReactNode;
}) {
  const [items, setItems] = useState<ApiInstitution[]>([]);
  useEffect(() => {
    getInstitutions()
      .then(setItems)
      .catch(() => setItems([]));
  }, []);
  return <>{children(items)}</>;
}

function initials(name: string) {
  return (
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? "")
      .join("") || "C"
  );
}

export function ApiProfiles() {
  const [profiles, setProfiles] = useState<
    Array<{
      username: string;
      name: string;
      institution: string;
      programme: string;
      description: string;
      tags: string[];
      accent: string;
    }>
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getPosts(), getCategories(), getInstitutions()])
      .then(([posts, categories, institutions]) => {
        const byUser = new Map<
          string,
          {
            username: string;
            name: string;
            institution: string;
            programme: string;
            description: string;
            tags: string[];
            accent: string;
          }
        >();
        for (const post of posts) {
          const name = post.submitter_name || "Campus member";
          const key = name.toLowerCase();
          const institution =
            institutions.find((item) => item.id === post.institution)?.name ||
            "Campus community";
          const programme =
            categories.find((item) => item.id === post.category)?.name ||
            "Community";
          const existing = byUser.get(key);
          if (existing) {
            existing.tags = Array.from(new Set([...existing.tags, programme]));
            existing.description =
              existing.description || post.content.slice(0, 180);
            continue;
          }
          byUser.set(key, {
            username: name.toLowerCase().replace(/\s+/g, "."),
            name,
            institution,
            programme,
            description: post.content.slice(0, 180),
            tags: [programme],
            accent: ["green", "ochre", "coral"][byUser.size % 3],
          });
        }
        setProfiles([...byUser.values()].slice(0, 12));
      })
      .catch(() => setError("We could not load the live community profiles."))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <>
        <Header />
        <main className="page">
          <div className="container narrow">
            <p className="large-copy">Loading community profiles…</p>
          </div>
        </main>
        <Footer />
      </>
    );
  if (error)
    return (
      <>
        <Header />
        <main className="page">
          <div className="container narrow">
            <p className="large-copy">{error}</p>
          </div>
        </main>
        <Footer />
      </>
    );

  return (
    <>
      <Header />
      <main className="page">
        <div className="container page-intro">
          <span className="eyebrow">
            <UserRound /> FIND YOUR PEOPLE
          </span>
          <h1>Student profiles</h1>
          <p>
            Live community members surfaced from the latest approved posts and
            institution data.
          </p>
        </div>
        <div className="container profile-grid">
          {profiles.map((profile) => (
            <Link
              href={`/profiles/${encodeURIComponent(profile.username)}`}
              className={`profile-card ${profile.accent}`}
              key={profile.username}
            >
              <div className="profile-avatar">{initials(profile.name)}</div>
              <span className="profile-handle">@{profile.username}</span>
              <h3>{profile.name}</h3>
              <p>
                {profile.programme} · {profile.institution}
              </p>
              <div className="tag-row">
                {profile.tags.slice(0, 3).map((tag) => (
                  <span key={tag}>{tag}</span>
                ))}
              </div>
              <div className="profile-description">{profile.description}</div>
            </Link>
          ))}
          {!profiles.length && (
            <div className="container narrow">
              <p className="large-copy">
                No community members are available yet.
              </p>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}

export function ApiEvents() {
  const [items, setItems] = useState<ApiPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getPosts()
      .then((posts) => setItems(posts.slice(0, 8)))
      .catch(() =>
        setError("We could not load the latest community highlights."),
      )
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <>
        <Header />
        <main className="page">
          <div className="container narrow">
            <p className="large-copy">Loading community highlights…</p>
          </div>
        </main>
        <Footer />
      </>
    );
  if (error)
    return (
      <>
        <Header />
        <main className="page">
          <div className="container narrow">
            <p className="large-copy">{error}</p>
          </div>
        </main>
        <Footer />
      </>
    );

  return (
    <>
      <Header />
      <main className="page">
        <div className="container page-intro">
          <span className="eyebrow">
            <CalendarDays /> WHAT&apos;S ON
          </span>
          <h1>Campus highlights</h1>
          <p>Live notices and opportunities pulled from the backend feed.</p>
        </div>
        <div className="container event-grid">
          {items.map((post) => (
            <article className="event-card" key={post.id}>
              <div className="event-date">
                <strong>
                  {new Date(post.created_at).toLocaleDateString(undefined, {
                    day: "numeric",
                  })}
                </strong>
                <span>
                  {new Date(post.created_at).toLocaleDateString(undefined, {
                    month: "short",
                  })}
                </span>
              </div>
              <div>
                <span className="category-pill">{post.title}</span>
                <h3>{post.title}</h3>
                <p>{post.content}</p>
                <small>
                  {post.submitter_name || "Campus community"} ·{" "}
                  {post.link_url ? "External link available" : "Community post"}
                </small>
              </div>
            </article>
          ))}
          {!items.length && (
            <div className="container narrow">
              <p className="large-copy">
                No live campus highlights are available right now.
              </p>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}

export function ApiAnalytics() {
  const [posts, setPosts] = useState<ApiPost[]>([]);
  const [channels, setChannels] = useState<ApiChannel[]>([]);
  const [institutions, setInstitutions] = useState<ApiInstitution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getPosts(), getChannels(), getInstitutions()])
      .then(([postData, channelData, institutionData]) => {
        setPosts(postData);
        setChannels(channelData);
        setInstitutions(institutionData);
      })
      .catch(() => setError("We could not load the live analytics snapshot."))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <>
        <Header />
        <main className="page">
          <div className="container narrow">
            <p className="large-copy">Loading live analytics…</p>
          </div>
        </main>
        <Footer />
      </>
    );
  if (error)
    return (
      <>
        <Header />
        <main className="page">
          <div className="container narrow">
            <p className="large-copy">{error}</p>
          </div>
        </main>
        <Footer />
      </>
    );

  const approved = posts.filter((post) => post.id > 0).length;
  return (
    <>
      <Header />
      <main className="page">
        <div className="container page-intro">
          <span className="eyebrow">
            <ChartNoAxesColumn /> COMMUNITY PULSE
          </span>
          <h1>Live analytics</h1>
          <p>Updated from the current backend feed.</p>
        </div>
        <div className="container analytics-grid">
          <div className="metric-card">
            <strong>{approved}</strong>
            <span>Total approved posts</span>
            <small>from the backend</small>
          </div>
          <div className="metric-card">
            <strong>{channels.length}</strong>
            <span>Active channels</span>
            <small>currently on the platform</small>
          </div>
          <div className="metric-card">
            <strong>{institutions.length}</strong>
            <span>Institutions</span>
            <small>available in the directory</small>
          </div>
          <div className="metric-card">
            <strong>{posts.filter((post) => post.title).length}</strong>
            <span>Visible noticeboard items</span>
            <small>live and public</small>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
