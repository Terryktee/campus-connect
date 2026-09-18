const API_URL = (
  typeof window === "undefined"
    ? process.env.BACKEND_INTERNAL_URL || "http://backend:8000"
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

).replace(/\/$/, "");
  
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly fieldErrors: Record<string, string[]> = {},
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { Accept: "application/json", ...init?.headers },
    });
  } catch {
    throw new ApiError(0, "The CampusConnect backend is unavailable.");
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      typeof body?.error === "string"
        ? body.error
        : typeof body?.detail === "string"
          ? body.detail
          : response.status >= 500
            ? "The CampusConnect backend is temporarily unavailable."
            : "This CampusConnect request could not be completed.";
    throw new ApiError(response.status, message, normaliseErrors(body));
  }
  return body as T;
}

export type ApiCategory = { id: number; name: string; slug: string };
export type ApiInstitution = { id: number; name: string; short_code: string };
export type ApiPost = {
  id: number;
  title: string;
  content: string;
  category: number;
  institution: number | null;
  channel: number | null;
  image_url: string;
  link_url: string;
  submitter_name: string;
  submitter_institution: string;
  is_featured: boolean;
  view_count: number;
  created_at: string;
};
export type ApiChannel = {
  id: number;
  slug: string;
  name: string;
  bio: string;
  category_focus: number | null;
  institution: number | null;
  follower_count: number;
  is_verified: boolean;
  posts?: ApiPost[];
};
export type ApiOrientationGuide = {
  id: number;
  guide_type: "how_to" | "directory_entry" | "campus_map_note";
  title: string;
  content: string;
  contact_info: string;
  sort_order: number;
};

type Paginated<T> = { results: T[] };

function unwrap<T>(value: T[] | Paginated<T>): T[] {
  return Array.isArray(value) ? value : value.results;
}

export function getPosts(params = "") {
  return request<Paginated<ApiPost> | ApiPost[]>(`/api/posts/${params}`).then(
    unwrap,
  );
}

export const getPost = (id: string) =>
  request<ApiPost>(`/api/posts/${encodeURIComponent(id)}/`);
export const getCategories = () =>
  request<ApiCategory[] | Paginated<ApiCategory>>("/api/categories/").then(
    unwrap,
  );
export const getInstitutions = () =>
  request<ApiInstitution[] | Paginated<ApiInstitution>>(
    "/api/institutions/",
  ).then(unwrap);
export const getOrientationGuides = (institutionShortCode: string) =>
  request<Record<ApiOrientationGuide["guide_type"], ApiOrientationGuide[]>>(
    `/api/orientation/${encodeURIComponent(institutionShortCode)}/`,
  );
export const getChannels = () =>
  request<Paginated<ApiChannel> | ApiChannel[]>("/api/channels/").then(unwrap);
export const getChannel = (slug: string) =>
  request<ApiChannel>(`/api/channels/${encodeURIComponent(slug)}/`);

export type FollowTarget = {
  channel?: string;
  category?: string;
  institution?: string;
};

export function follow(contact: string, target: FollowTarget) {
  return request<{ id: number }>("/api/follow/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ follower_contact: contact, ...target }),
  });
}

export function unfollow(contact: string, target: FollowTarget) {
  return request<void>("/api/follow/", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ follower_contact: contact, ...target }),
  });
}

export type SubmissionResponse = {
  id?: number;
  status: string;
  channel_created?: boolean;
  channel_name?: string;
};

function normaliseErrors(value: unknown): Record<string, string[]> {
  if (!value || typeof value !== "object") return {};
  return Object.entries(value as Record<string, unknown>).reduce<
    Record<string, string[]>
  >((errors, [field, messages]) => {
    const values = Array.isArray(messages) ? messages : [messages];
    errors[field] = values.filter(
      (message): message is string => typeof message === "string",
    );
    return errors;
  }, {});
}

export async function submitPost(
  payload: Record<string, string>,
): Promise<SubmissionResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/posts/submit/`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new ApiError(0, "The CampusConnect backend is unavailable.");
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const fieldErrors = normaliseErrors(body);
    const message =
      typeof body?.error === "string"
        ? body.error
        : typeof body?.detail === "string"
          ? body.detail
          : response.status >= 500
            ? "The CampusConnect backend is temporarily unavailable."
            : "This CampusConnect request could not be completed.";
    throw new ApiError(response.status, message, fieldErrors);
  }
  return body as SubmissionResponse;
}
