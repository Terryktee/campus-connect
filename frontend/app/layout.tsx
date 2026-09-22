import { Analytics } from "@vercel/analytics/next";
import type { Metadata, Viewport } from "next";
import { DM_Sans, Lora } from "next/font/google";
import "./globals.css";
const sans = DM_Sans({ subsets: ["latin"], variable: "--font-dm-sans" });
const serif = Lora({ subsets: ["latin"], variable: "--font-lora" });
export const metadata: Metadata = {
  title: "CampusConnect ZW — What’s happening on campus?",
  description:
    "The student noticeboard for Zimbabwe. Find your people, share what matters and make campus life a little easier.",
  generator: "v0.app",
};
export const viewport: Viewport = {
  colorScheme: "light",
  themeColor: "#f7f4ee",
};
export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="bg-background">
      <body className={`${sans.variable} ${serif.variable}`}>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
