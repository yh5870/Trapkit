import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "트립킷 — 입력 한 번으로 끝내는 여행 준비",
  description: "내 여행에 꼭 맞는 준비물과 수화물 규정을 한 번에 확인하세요.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>
        {children}
      </body>
    </html>
  );
}
