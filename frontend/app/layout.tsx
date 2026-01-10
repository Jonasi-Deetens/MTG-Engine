import type { Metadata } from "next";
import { Inter, Cinzel } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { ThemeProvider } from "@/context/ThemeContext";
import { NavbarWrapper } from "@/components/navigation/NavbarWrapper";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const cinzel = Cinzel({
  variable: "--font-cinzel",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

export const metadata: Metadata = {
  title: "MTG Engine",
  description: "Magic: The Gathering card search and engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="overflow-x-hidden" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  let theme = localStorage.getItem('mtg-engine-theme') || 'light';
                  // Migrate 'angel' theme to 'light' for backward compatibility
                  if (theme === 'angel') {
                    theme = 'light';
                    localStorage.setItem('mtg-engine-theme', 'light');
                  }
                  document.documentElement.setAttribute('data-theme', theme);
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body
        className={`${inter.variable} ${cinzel.variable} antialiased bg-[color:var(--theme-bg-primary)] text-[color:var(--theme-text-primary)] overflow-x-hidden`}
      >
        <ThemeProvider>
          <AuthProvider>
            <NavbarWrapper>{children}</NavbarWrapper>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
