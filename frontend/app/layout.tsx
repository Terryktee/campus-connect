import { Analytics } from "@vercel/analytics/next";
import type { Metadata, Viewport } from "next";
import { DM_Sans, Lora } from "next/font/google";
import "./globals.css";
const sans = DM_Sans({ subsets: ["latin"], variable: "--font-dm-sans" });
const serif = Lora({ subsets: ["latin"], variable: "--font-lora" });
export const metadata: Metadata = {
  title: "Loop — What’s happening?",
  description:
    "An open, no-account social platform for youth worldwide. Find your community, share what matters, and loop in.",
  generator: "Loop",
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
