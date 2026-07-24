import type { Metadata } from "next";
import "./globals.css";

// Google Fonts import
const googleFonts = `
  @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Courier+Prime:wght@400;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
`;

export const metadata: Metadata = {
  title: "트립킷 — 입력 한 번으로 끝내는 여행 준비",
  description: "내 여행에 꼭 맞는 준비물과 수화물 규정을 한 번에 확인하세요.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <head>
        <style dangerouslySetInnerHTML={{ __html: googleFonts }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
