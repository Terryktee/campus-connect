# Loop: Master Build Plan and Antigravity Prompt Pack

*Formerly Campus Loop ZW. A no-account platform for youth everywhere. No youth left behind.*

## 0. Read this first

Decisions I made where your brief left room. Change them if you disagree.

- **Reactions:** you asked for "like & hate". I kept both but named the negative one **Nah**. It lowers a post's Pulse quietly and is never shown as a public count, so nobody gets pile-on shamed. This is a youth platform with images, so that choice matters.
- **Rewards are points and perks, not cash**, at launch. Cash payouts on a no-account platform with minors invite fraud and legal trouble. Sponsor-funded airtime/data bundles come later.
- **Ama2K Fame Status** is the name of the tier ladder (section 2.3). Rename if "ama2k" meant something else.
- **Folder assumption:** `backend/` (Django) and `frontend/` (Next.js). Adjust paths if your repo differs.
- **Open-source license:** AGPL-3.0 (section 8). Alternatives are listed.
- **Non-negotiables because youth upload images and audio:** EXIF stripping, NSFW/CSAM scanning, report flows, and no stranger DMs.

## 1. Product spec

**Tagline options:** "Loop in." / "Your voice. Your loop." / "No youth left behind."

**Principle:** "a platform without direction, controlled by the statements" means the community's posts steer the feed, not an editor. So there are no follow-graph walls. The feed is made of **statements** (posts) ranked by Pulse (section 2).

### Features (nothing optional)

| Area | Requirement |
| --- | --- |
| Posts | Text + **images** (up to 4) + **audio** (voice notes up to 3 min, audio posts up to 10 min). |
| Images | Client-side compression, server WebP/AVIF variants, EXIF/GPS stripped, blurhash placeholder, NSFW + hash-match scan, alt text field. |
| Audio | Record in browser or upload. ffmpeg transcode to Opus/AAC in Celery, waveform peaks, transcript (Whisper) used for moderation and search, playback speed, listen-completion tracking. |
| Reactions | Like, Nah, Comment (threaded, 2 levels), Repost, Save, Share. |
| **Snapshots** | See 1.1. |
| Analytics | Per post: views (total + unique), likes, comments, reposts, shares, snapshot opens, saves, audio listens and completion rate, top communities. **Public** shows views, likes, comments, shares. **Admin** shows everything plus fraud flags. |
| Trending | Trending posts and profiles via Pulse and Aura. |
| Fame-game | Aura score, Ama2K Fame Status, weekly Top 5 rewards, Hall of Fame. |
| Marketplace | See 1.2. |
| News | See 1.3. |
| Search | Global search over posts, profiles, products, news (MySQL FULLTEXT first, Meilisearch when ready). Filters by community, country, type, date. |
| Moderation | Delete, hide, ban, suspend (timed), shadow-limit, report queue, appeals, audit log, on posts, comments, profiles, products, news. |
| SEO | Server-rendered metadata, canonical URLs, JSON-LD, sitemap index, robots, OG images, Core Web Vitals budget. |
| Low-data mode | Default on slow connections: no autoplay, images deferred, audio on tap. Essential for African users. |
| PWA | Installable, offline reading of saved items. |
| i18n | English, Shona, Ndebele first. The architecture must allow adding Swahili, Zulu, French, Portuguese, Arabic, Spanish and others. |

### 1.1 Snapshots

A **snapshot** is a shareable, frozen-looking card of content.

- **Types:** `post`, `post_with_comments` (post plus top N comments), `comment` (one comment with its parent context line), `profile_card`, `product`.
- Each snapshot has a short URL `loop.app/s/{id}`.
- Creating one stores a **frozen JSON copy** (content, counts at that moment, timestamp), so edits or deletions later don't silently rewrite shared history. If the original is deleted by moderation, the snapshot goes dark too (safety first).
- Rendering: Next.js `ImageResponse` (OG image) for 1:1, 4:5 and 9:16 sizes, with the Loop wordmark watermark. The share sheet offers Copy link, Download image, WhatsApp, X, Facebook, Telegram, and Web Share API.
- Every snapshot open and share counts toward the post's analytics and the author's Aura.

### 1.2 Marketplace

- **Listing:** title, photos (up to 6), description, price + currency (USD/ZWG/other), category, condition, **location** (city/area plus optional campus), **contact methods** (WhatsApp, phone, Telegram, in-person only). Contact details are hidden behind a "Reveal contact" tap, rate-limited per device, and logged. This stops scraping.
- **Ownership without accounts:** the seller's device key owns the listing. An edit/delete token is also shown once as a backup. Recovery phrase restores ownership on a new device.
- **Search:** keyword, category, price range, location radius/area, sort by newest/price/Aura of seller.
- **Highlights:** "Featured" slots rotate weekly to the best-trusted listings. Sellers can also earn highlights using Loop Points.
- **Anti-scam (the "don't get scammed" part):**
  - Automatic red flags: advance-fee wording, "pay before viewing", off-platform wire/crypto requests, price far below category median, stock photos (perceptual-hash reuse across sellers), duplicate listings.
  - Seller trust badge: New, Active, Trusted (age, no upheld reports, buyer confirmations).
  - **Buyer confirmation:** after a deal, the buyer can enter the seller's one-time deal code to confirm it. This is the only thing that raises Trusted.
  - "Safe deal" tips on every listing: meet in public/campus places, inspect first, never pay deposits for unseen items.
  - One-tap Report scam. Three independent reports auto-hide pending review.
  - Marketplace has the same delete, suspend and ban powers as posts.
- **Youth protection:** age-restricted items (alcohol, drugs, weapons, adult content) are blocked outright.

### 1.3 News

- Editorial **News** tab with three sources: staff-written, RSS/curated feeds linked out with headline + short excerpt + attribution (never full copied articles), and **youth reporter submissions** that go through moderation.
- Categories: Campus, Zimbabwe, Africa, World, Opportunities (scholarships, jobs, grants), Tech, Sport, Culture.
- News items are also postable into the feed as statements, so they get reactions and snapshots too.

## 2. Algorithms

### 2.1 Pulse (trending posts)

Goal: surface what is **surprising and spreading**, not what is already big. Big accounts shouldn't permanently win, and a great post from a first-timer should be able to reach the top.

**Action weights (w):** unique view with 3s+ dwell 0.1, like 1, comment (3+ words) 3, share/snapshot-share 4, repost 5, save 2, audio listened >70% 1.5, Nah -0.6.

**Step 1: raw heat.** For each window `W` in {1h, 6h, 24h}: `H_W = Σ over action types a: w_a × log2(1 + n_a,W)`, where `n` counts **distinct trusted actors** only. Log saturation stops a mob from dominating.

**Step 2: velocity.** `V = 3·H_1h + 1.5·H_6h + 0.5·H_24h`.

**Step 3: Surprise factor.** Compare to the author's own baseline: `S = clamp(V / max(author_median_V, 1), 0.5, 4)`. A post doing 4× better than that author's usual gets lifted regardless of fame.

**Step 4: Ripple.** `R = 1 + 0.15·ln(1 + distinct_communities_reached)`, where a community is a campus, country, or interest group. Posts that jump across communities beat posts that only circulate in one.

**Step 5: Spark quality.** `Q = 0.8 + 0.4·(comment_rate_per_view normalized) + 0.2·(completion_rate)`, range about 0.8–1.4.

**Step 6: Freshness.** `F = 1 / (1 + age_hours/10)^1.4`.

**Step 7: Newcomer lift.** Author under 10 posts or under 14 days on Loop: ×1.2.

**Pulse = V × S × R × Q × F × N × Trust**, where Trust is the brigading discount (0.2–1.0, see below).

**Step 8: Diversity re-rank (MMR style) when building the list.** Max 2 posts per author in the top 20. At least 30% of slots go to communities other than the viewer's biggest one. At least 1 in 5 slots is an "Outside Your Loop" post, which keeps youth from sealed bubbles. Include audio and image posts proportionally.

**Anti-brigading:** discount Trust if more than 60% of actions come from one device cluster or IP range, if many keys are under 24h old, if actions arrive in uniform bursts, or if actor trust is low. Heavily flagged posts are held for review and their rewards freeze.

**Cron:** Celery beat recomputes every 2 minutes, writing top 500 to Redis sorted sets: `pulse:global`, `pulse:country:{cc}`, `pulse:campus:{id}`.

### 2.2 Aura (profile score and trending profiles)

Aura (0–1000) measures an **inner self**: the full picture of a profile, not just popularity.

- **Reach 30%:** log of unique viewers over 30 days.
- **Resonance 25%:** *median* engagement per post (not totals, so spam doesn't win).
- **Spread 20%:** reposts, shares, snapshots and saves **by others**.
- **Consistency 15%:** active days in last 30, streak capped.
- **Community 10%:** helpful comments (liked by others), marketplace trust, upheld reports against others, minus upheld reports against self.

Everything is tracked per profile: posts, comments, reposts, shares, snapshots created, listens, marketplace deals, news contributions. Aura = weighted score × trust multiplier. Aura decays 2% per week of inactivity.

**Trending profiles = Aura momentum:** the 7-day change in Aura (relative to current Aura), so rising creators beat static big ones. Show "Rising Voices" separately from "All-time Aura".

### 2.3 Ama2K Fame Status ladder

| Aura | Status |
| --- | --- |
| 0–99 | **Spark** |
| 100–249 | **Rising** |
| 250–449 | **Blazing** |
| 450–649 | **Star** |
| 650–849 | **Legend** |
| 850+ and top 0.1% | **Icon** |

Statuses show as a badge and frame on the profile and every post. Weekly seasons create a leaderboard, but **Hall of Fame** records are permanent. Prestige: once you reach Icon and hold it for 4 weeks, you earn a permanent "Ama2K Icon" mark.

### 2.4 Rewards (Loop Points, LP)

**Weekly Top 5 posts** (by Pulse peak across the week, Monday 00:00 CAT):

| Rank | LP | Perk |
| --- | --- | --- |
| 1 | 1000 | Spotlight banner 48h + Gold Loop frame |
| 2 | 600 | Spotlight 24h + Silver frame |
| 3 | 400 | Bronze frame |
| 4 | 250 | Hall of Fame entry |
| 5 | 150 | Hall of Fame entry |

**Micro-rewards to creators**, per trusted unique actor: view 0.2 LP, like 1 LP, comment 3 LP, share 4 LP, repost 5 LP. Daily cap 500 LP per profile. LP vest for 48h before being spendable so fraud review can claw back.

**Early Eye bonus:** the first 20 trusted people to like or comment on a post that later reaches the weekly Top 5 earn 25 LP each. This rewards finding good content early.

**LP spend:** profile flairs, post boosts (capped and labeled), marketplace highlights, themes, partner perks. Cash-out is a later phase.

Fraud rule: no reward if actors fail trust checks. Admins can freeze, revoke or claw back LP, with every action audit-logged.

## 3. Identity without accounts

No email, no password, no phone number. Handles are chosen, not verified.

1. **Key identity:** on first visit the browser generates an Ed25519 keypair with WebCrypto. The private key is non-extractable in IndexedDB. The server stores only the public key and a random handle. Requests are authenticated by signing a server challenge, which gives a short-lived token with no passwords stored.
2. **Recovery phrase:** a 12-word phrase (BIP-39 wordlist) encodes the seed the key is derived from. Show it after the first post or marketplace listing with a clear "save this" screen, plus a reminder banner until the user confirms they stored it. Losing it means losing the profile, and this is stated plainly.
3. **Device transfer:** old device shows a QR plus a 6-digit code (valid 5 minutes, single use). New device scans it, and the old device approves and passes an encrypted key bundle.
4. **Backup file:** export an encrypted `.loopkey` file (passphrase-protected, AES-GCM, Argon2/PBKDF2). Import it on any device.
5. **Multi-device:** a profile can authorize extra devices, and the list is viewable and revocable.
6. **Abuse control:** proof-of-work or lightweight challenge on key creation, per-IP and per-device rate limits, new-key reputation ramp (limited posts per day until Aura/age grows), and bans bind to the key plus a privacy-preserving device signal (no raw fingerprint stored).
7. **Privacy:** no IP stored beyond short rate-limit windows. Privacy page written in plain language.

## 4. Safety (required for a youth platform)

- Hash-match images against known CSAM databases through a vetted provider (for example PhotoDNA or an equivalent), plus NSFW classifier. Block, quarantine, and follow reporting law.
- Audio transcripts checked for abuse, grooming patterns, threats, self-harm. Self-harm content shows a support resource instead of just hiding.
- No private DMs between strangers in v1.
- Strip EXIF/GPS from all uploads. Never show exact location of a minor.
- Community rules page, report on everything, appeal flow, transparent moderation log (public summary, private detail).
- Admin and moderator accounts use real auth (email + password + TOTP 2FA) and role-based permissions.

## 5. Architecture

Keep your stack: Django, DRF, Celery, Redis, MySQL, Next.js, TypeScript.

**Add:**

- **Object storage:** Cloudflare R2 or S3 for media (Railway volumes are not for media).
- **ffmpeg + Pillow/pyvips** in the Celery worker.
- **Meilisearch or Typesense** (Railway service) for search, once MySQL FULLTEXT is outgrown.
- **Sentry** for errors, **PostHog** or self-hosted analytics for product analytics (privacy-respecting).
- **django-ratelimit** / DRF throttling, **django-axes** on admin login.
- **Playwright** (e2e), **pytest**, **Vitest**, **ruff**, **eslint**, **gitleaks**.
- **Tailwind + shadcn/ui** for the new design system and admin.

**Core models:** `Profile(pubkey, handle, aura, tier, status)`, `Device`, `Post(kind, body, community, state)`, `Media(kind, variants, transcript, scan_state)`, `Reaction`, `Comment`, `Repost`, `Snapshot(type, payload_json, source_id)`, `PostMetricDaily`, `ViewEvent(sketch/unique)`, `Listing`, `ListingReport`, `NewsItem`, `PointsLedger` (append-only), `Season`, `ModerationAction`, `AuditLog`.

**Counters:** write events to Redis, aggregate to MySQL in batches every minute (HyperLogLog for unique views). Never `UPDATE count+1` on hot rows.

**Admin panel redesign:** Next.js `/admin` area (or a restyled Django admin if you prefer): dashboard (live posts, reports, signups, Pulse leaderboard), moderation queue with keyboard shortcuts, user/profile page with full Aura breakdown and action history, post analytics page, marketplace review, news editor, rewards console, audit log, mobile-friendly, dark and light mode.

## 6. Brand: Loop wordmark

Two interlocked "o" rings. Palette: Pan-African (red `#CE1126`, gold `#FCD116`, green `#009A44`, black `#111111`), Zimbabwe flag (green, yellow, red, black, white), plus world accents (blue `#0A66C2`, orange `#FF7A00`, violet `#7B3FE4`, teal `#00B8A9`). The first ring runs green→gold, the second red→violet, so the pair reads as Africa meeting the world.

Starter SVG (have the agent refine spacing, add a mono and a reversed version, and a favicon from the double ring):

```svg
<svg viewBox="0 0 340 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Loop">
  <defs>
    <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#009A44"/><stop offset="1" stop-color="#FCD116"/></linearGradient>
    <linearGradient id="g2" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#CE1126"/><stop offset="1" stop-color="#7B3FE4"/></linearGradient>
  </defs>
  <text x="8" y="92" font-family="Poppins, Arial, sans-serif" font-weight="800" font-size="96" fill="#111">L</text>
  <circle cx="142" cy="68" r="25" fill="none" stroke="url(#g1)" stroke-width="14"/>
  <circle cx="186" cy="68" r="25" fill="none" stroke="url(#g2)" stroke-width="14"/>
  <text x="222" y="92" font-family="Poppins, Arial, sans-serif" font-weight="800" font-size="96" fill="#111">p</text>
</svg>
```

## 7. CI/CD (GitHub Actions to Railway and Vercel)

**Setup once:**

- GitHub secrets: `RAILWAY_TOKEN` (project token), `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`.
- Railway: three services from the same repo (`web` = gunicorn, `worker` = celery worker, `beat` = celery beat). Set the web service's pre-deploy command to `python manage.py migrate --noinput`.
- Protect `main`: require the CI jobs to pass. Deploy only from `main`.
- Disable Railway/Vercel auto-deploy so this workflow is the single deploy path (or keep auto-deploy and delete the deploy jobs).

`.github/workflows/ci-cd.yml`:

```yaml
name: CI-CD
on:
  push: { branches: [main] }
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env: { MYSQL_ROOT_PASSWORD: root, MYSQL_DATABASE: loop }
        ports: ['3306:3306']
        options: >-
          --health-cmd="mysqladmin ping -proot" --health-interval=10s
          --health-timeout=5s --health-retries=10
      redis:
        image: redis:7
        ports: ['6379:6379']
    env:
      DATABASE_URL: mysql://root:root@127.0.0.1:3306/loop
      REDIS_URL: redis://127.0.0.1:6379/0
      DJANGO_SECRET_KEY: ci-only-secret
    defaults: { run: { working-directory: backend } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12', cache: pip }
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: ruff check .
      - run: python manage.py makemigrations --check --dry-run
      - run: pytest -q --cov

  frontend:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: frontend } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm, cache-dependency-path: frontend/package-lock.json }
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit
      - run: npm test --if-present
      - run: npm run build
        env: { NEXT_PUBLIC_API_URL: https://api.example.com }

  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: gitleaks/gitleaks-action@v2
        env: { GITHUB_TOKEN: '${{ secrets.GITHUB_TOKEN }}' }

  deploy-backend:
    if: github.ref == 'refs/heads/main'
    needs: [backend, frontend, secrets-scan]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm i -g @railway/cli
      - run: |
          railway up --service web --ci
          railway up --service worker --ci
          railway up --service beat --ci
        env: { RAILWAY_TOKEN: '${{ secrets.RAILWAY_TOKEN }}' }

  deploy-frontend:
    if: github.ref == 'refs/heads/main'
    needs: [backend, frontend, secrets-scan]
    runs-on: ubuntu-latest
    env:
      VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
      VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
    steps:
      - uses: actions/checkout@v4
      - run: npm i -g vercel
      - run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
      - run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
      - run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

If your repo root is not the Vercel project root, set Root Directory to `frontend` in Vercel. Add Dependabot and PR preview deploys later.

## 8. Open-sourcing Loop

**Before going public (do not skip):**

1. Run `gitleaks detect` over the **full git history**. Any key ever committed must be **rotated**, even if deleted since.
2. Remove real student data, seed data with real names, and private URLs.
3. Make sure `.env.example` has only placeholders.
4. Confirm you own or have permission for all assets and fonts.

**Files to add:** `LICENSE`, `README.md` (rewritten for Loop), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` (private vulnerability reporting), `GOVERNANCE.md`, `TRADEMARK.md`, `.github/ISSUE_TEMPLATE/*`, `PULL_REQUEST_TEMPLATE.md`, `docs/ARCHITECTURE.md`, `docs/MODERATION.md`.

**License choice:**

- **AGPL-3.0 (recommended):** anyone can use and fork, but a hosted fork must publish its changes. This protects a youth platform from being quietly closed-sourced.
- **Apache-2.0 or MIT:** maximum adoption, no obligation to share back.

Reserve the **Loop name and wordmark** in `TRADEMARK.md` so forks can't impersonate the official service. Keep the safety stack required in the default config so forks don't run an unmoderated youth platform by accident.

## 9. Which model for which job

Honest note: I'm Claude, so weigh this accordingly, and test each model on one real task before committing.

| Model | Use it for | Why |
| --- | --- | --- |
| **Claude Opus 4.6** | Architecture, key-based identity and crypto, Pulse/Aura/rewards logic, anti-fraud, security review, risky migrations | Strongest at deep multi-step reasoning and spotting subtle bugs. Slowest and priciest, so spend it where mistakes are expensive. |
| **Claude Sonnet 4.6** | **Default workhorse:** Django endpoints, Next.js pages, admin UI, tests, CI/CD, snapshots, search | Best balance of quality, speed and cost for agentic multi-file edits. |
| **GPT-OSS** | README/docs, boilerplate, i18n strings, seed data, test scaffolding, simple CRUD | Cheap and quick for low-risk work. Weaker on long repo-wide agent tasks and security-sensitive logic, so keep it away from auth, rewards and moderation code. |

**Verdict:** Sonnet 4.6 for about 70% of the work, Opus 4.6 for the 15% that must be right (identity, algorithms, safety, rewards), GPT-OSS for the cheap 15%. If you can only pick one, pick Sonnet 4.6. Have Opus review every PR that touches identity, rewards or moderation.

## 10. Antigravity prompt pack

**How to use:** clone the repo locally, open it in Antigravity, and put Prompt R in the project **Rules** (or `AGENTS.md`). Then paste one prompt at a time, in order, each on a fresh branch. Run tests and review the diff before merging. Each prompt names the best model.

### Prompt R: Project rules (every task)

```
You are working on Loop (formerly Campus Loop ZW), an open-source, no-account
social platform for youth worldwide. Stack: Django + DRF + Celery + Redis + MySQL
(backend/), Next.js + TypeScript + React (frontend/). Deployed on Railway (backend)
and Vercel (frontend).

Rules:
1. Work on a feature branch. Small, reviewable commits. Never push to main.
2. Never commit secrets. Use env vars and update .env.example with placeholders.
3. Every feature ships with tests (pytest / Vitest / Playwright where relevant).
4. Before finishing run: ruff, pytest, eslint, tsc --noEmit, npm run build. Fix failures.
5. Never store raw IPs long-term. Strip EXIF from images. Youth safety is a hard requirement.
6. Never UPDATE counters on hot rows: use Redis counters + batched aggregation.
7. All user-generated content must be reportable and moderatable
   (delete/hide/suspend/ban) and audit-logged.
8. Mobile-first, low-bandwidth friendly, accessible (WCAG AA), i18n-ready strings.
9. End each task by explaining what changed and any follow-up risks.
10. If a requirement is ambiguous, state your assumption and proceed.
```

### Prompt 1: Audit and rename (Sonnet 4.6)

```
Audit the whole repository and write docs/AUDIT.md: architecture, apps, models,
endpoints, auth flow, admin, env vars, what is broken or insecure, and a
prioritized fix list. Then rename the product from "Campus Loop" / "Campus Loop ZW"
to "Loop" everywhere (code, UI copy, metadata, README, docker, package names,
emails), keeping DB table names stable unless a migration is clearly safe.
Replace hard-coded "ZW only" assumptions with a configurable country/community
model because Loop is for youth worldwide. Rewrite README.md for Loop, keeping
the Docker Compose local-development instructions accurate.
```

### Prompt 2: Identity without accounts (Opus 4.6)

```
Implement account-less identity. The browser generates an Ed25519 keypair
(WebCrypto, non-extractable key in IndexedDB). Backend stores only the public key
and handle. Auth is challenge-signature issuing a short-lived token. Implement:
(a) 12-word BIP-39 recovery phrase with a save/confirm UI and persistent reminder;
(b) device transfer via QR + 6-digit single-use code valid 5 minutes;
(c) encrypted .loopkey backup export/import (AES-GCM, passphrase KDF);
(d) authorized-devices list with revoke;
(e) abuse controls: proof-of-work on key creation, per-IP/device rate limits,
    new-key reputation ramp, bans bound to key + a privacy-preserving device signal.
Write a threat model in docs/IDENTITY.md and tests for replay, expired codes,
revoked devices, and phrase recovery. Keep admin/moderator accounts on separate
real auth (password + TOTP, django-axes protection).
```

### Prompt 3: Media, images and audio (Sonnet 4.6)

```
Add image and audio support to posts and comments. Use S3-compatible storage
(Cloudflare R2) via django-storages with signed direct uploads. Images: client
compression, up to 4 per post, server WebP/AVIF variants, EXIF/GPS stripping,
blurhash, alt text. Audio: browser recording + upload, 3 min voice notes and
10 min audio posts, ffmpeg transcode to Opus/AAC in Celery, waveform peaks,
player with speed control, listen-completion events. Pipeline states:
uploaded -> scanning -> approved/quarantined. Add a pluggable scanner interface
(NSFW classifier, hash-match provider stub, Whisper transcript for audio) so
quarantine works before real providers are configured. Add a low-data mode
(no autoplay, deferred media). Include tests and docs/MEDIA.md.
```

### Prompt 4: Reactions, comments, snapshots (Sonnet 4.6)

```
Implement Like, Nah (quiet negative reaction, never a public count), threaded
comments (2 levels), Repost, Save, Share. Implement Snapshots: types post,
post_with_comments, comment, profile_card, product. Creating a snapshot stores a
frozen JSON payload and returns a short URL /s/{id}. Render snapshot images with
Next.js ImageResponse in 1:1, 4:5, 9:16 with the Loop wordmark watermark,
proper OG/Twitter meta, and a share sheet (copy link, download image, WhatsApp,
Telegram, X, Facebook, Web Share API). A snapshot goes dark if its source is
removed by moderation. Count snapshot opens/shares toward analytics. Add tests.
```

### Prompt 5: Analytics (Sonnet 4.6)

```
Build per-post analytics. Capture view events (dwell >= 3s counts) into Redis,
use HyperLogLog for unique views, and batch-aggregate to PostMetricDaily every
minute via Celery beat. Track likes, nah, comments, reposts, shares, snapshot
opens, saves, audio listens/completion, and top communities. Public post pages
show views, likes, comments, shares. The admin panel shows the full breakdown,
time-series charts, and fraud flags. Build reusable chart components. Include a
backfill command and tests for counter accuracy under concurrent writes.
```

### Prompt 6: Pulse, Aura, rewards (Opus 4.6)

```
Implement Pulse (trending posts), Aura (profile score 0-1000), Ama2K Fame Status
tiers (Spark, Rising, Blazing, Star, Legend, Icon), and Loop Points rewards
exactly as specified in sections 2.1-2.4 of the Loop Master Build Plan
[paste those sections here]. Requirements: distinct trusted actors only,
log-saturated counts, author-baseline Surprise factor, Ripple (cross-community
spread), freshness decay, newcomer lift, brigading Trust discount, MMR-style
diversity re-ranking (max 2 posts/author in top 20, 30% non-dominant community,
1-in-5 "Outside Your Loop"). Celery beat recomputes every 2 minutes into Redis
sorted sets pulse:global / pulse:country:{cc} / pulse:campus:{id}. A weekly
season job awards Top 5 post rewards through an append-only PointsLedger with
48h vesting and admin freeze/clawback. Make all weights configurable in a
settings model with an admin UI. Provide simulation tests (a coordinated-brigade
scenario and a newcomer-breakout scenario) and document the design in
docs/ALGORITHMS.md.
```

### Prompt 7: Marketplace (Sonnet 4.6)

```
Build the marketplace. Anyone (no account) can list a product with title, photos
(up to 6), description, price+currency, category, condition, location
(city/area/optional campus), and contact methods (WhatsApp/phone/Telegram/
in-person). Ownership via the device key plus a one-time backup edit token.
Contact details sit behind a rate-limited, logged "Reveal contact". Search by
keyword, category, price range, area; sort by newest/price/seller Aura.
Anti-scam: heuristic red flags (advance-fee wording, off-platform/crypto payment
asks, price far below category median, perceptual-hash reuse of photos across
sellers, duplicates), seller trust badges (New/Active/Trusted), buyer deal-code
confirmation to raise trust, safe-deal tips on every listing, Report scam with
auto-hide after 3 independent reports, and blocked categories (alcohol, drugs,
weapons, adult). Weekly rotating Featured listings. Admins can search, delete,
suspend and ban here too. Add tests.
```

### Prompt 8: News (Sonnet 4.6)

```
Add a News section: staff-written articles, RSS/curated feeds shown as headline +
short excerpt + attribution with a link out (never full copied bodies), and
youth-reporter submissions that go through moderation. Categories: Campus,
Zimbabwe, Africa, World, Opportunities, Tech, Sport, Culture. Add an admin
editor, scheduled publishing, and an option to post a news item into the feed.
Support reactions and snapshots on news. Add NewsArticle JSON-LD and tests.
```

### Prompt 9: Admin panel redo (Sonnet 4.6, then Opus 4.6 to review)

```
Redesign the admin panel for clean, fast UI/UX with Tailwind + shadcn/ui. Pages:
dashboard (live stats, report queue size, Pulse leaderboard), moderation queue
(keyboard shortcuts j/k/d/h/s/b), profile detail (Aura breakdown, history,
ban/suspend with duration + reason), post analytics, marketplace review, news
editor, rewards console (freeze/revoke/claw back), algorithm-weight settings,
and audit log. Require TOTP 2FA and role-based permissions (admin/moderator/
editor). Mobile-friendly, dark/light, accessible. Every moderation action writes
an audit entry. Include Playwright smoke tests.
```

### Prompt 10: Brand and design system (Sonnet 4.6)

```
Create the Loop brand kit from the starter SVG in the plan: refine the wordmark
(two interlocking "o" rings, green->gold and red->violet gradients using Pan-
African, Zimbabwe and world colors), then produce light/dark/mono variants,
favicon/app icons, and a PWA manifest. Create design tokens (colors, type,
spacing, radii), a Tailwind theme, and a vibrant youth-focused refresh of the
feed, profile and post pages. Document in docs/BRAND.md.
```

### Prompt 11: SEO and performance (Sonnet 4.6)

```
Fix SEO: generateMetadata on every route, canonical URLs, Open Graph/Twitter
cards, JSON-LD (Article, Product, NewsArticle, ProfilePage), a sitemap index with
chunked sitemaps for posts/products/news/profiles, robots.txt, hreflang,
semantic HTML, and an ISR/caching strategy. noindex quarantined or low-trust
content. Set Core Web Vitals budgets, optimize images and fonts, and report
before/after Lighthouse scores in docs/SEO.md.
```

### Prompt 12: CI/CD (Sonnet 4.6)

```
Create .github/workflows/ci-cd.yml as described in the plan, adapted to this
repo's real paths and commands: backend lint/tests with MySQL + Redis services,
frontend lint/tsc/test/build, gitleaks, then deploy from main to Railway (web,
worker, beat via the Railway CLI) and Vercel (prebuilt prod deploy). Add
Dependabot, a PR template, and docs/DEPLOY.md listing required secrets and
Railway/Vercel settings, including the pre-deploy migrate command.
```

### Prompt 13: Search and moderation completeness (Sonnet 4.6)

```
Implement global search across posts, profiles, products and news (MySQL FULLTEXT
behind a SearchBackend interface so Meilisearch/Typesense can replace it). Audit
that delete, comment, report, hide, suspend and ban work on posts, comments,
profiles, products and news, with timed suspensions, appeals and audit logs. Fix
any gaps and add tests.
```

### Prompt 14: Open-source readiness (GPT-OSS for docs, Opus 4.6 for the secrets review)

```
Prepare the repo for public release: scan history for secrets, list anything that
must be rotated, scrub real data, and create LICENSE (AGPL-3.0), CONTRIBUTING.md,
CODE_OF_CONDUCT.md, SECURITY.md, GOVERNANCE.md, TRADEMARK.md, issue/PR templates,
docs/ARCHITECTURE.md and docs/MODERATION.md. Make the safety stack required in the
default configuration. Output a pre-release checklist.
```

## 11. Suggested build order

1. Prompt 1 (audit and rename), then 12 (CI/CD) so every later branch is protected.
2. Prompt 2 (identity), since everything depends on it.
3. Prompts 3, 4, 5 (media, reactions and snapshots, analytics).
4. Prompts 6, 7, 8 (Pulse/Aura/rewards, marketplace, news).
5. Prompts 9, 10, 11, 13 (admin, brand, SEO, search/moderation).
6. Prompt 14, then flip the repo to public.

Do **identity and safety scanning first**. A growth algorithm on top of weak identity just rewards the fakers faster.
