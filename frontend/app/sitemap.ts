import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const siteUrl = (
    process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"
  ).replace(/\/$/, "");
  const publicRoutes = [
    "/",
    "/channels",
    "/events",
    "/guidelines",
    "/orientation",
    "/privacy",
    "/contact",
    "/profiles",
  ];

  return publicRoutes.map((route) => ({
    url: `${siteUrl}${route}`,
    changeFrequency: "weekly",
    priority: route === "/" ? 1 : 0.7,
  }));
}
