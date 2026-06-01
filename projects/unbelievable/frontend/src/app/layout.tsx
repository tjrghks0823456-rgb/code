import React from "react";
import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "UNBELIEVABLE - 내 알고리즘 속 미디어 성향 테스트",
  description: "최근 시청 기록과 자가진단을 비교해 나의 미디어 성향과 알고리즘 쏠림을 보여주는 분석 리포트입니다.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700;900&display=swap" rel="stylesheet" />
      </head>
      <body className="min-h-screen bg-[#f7f4ee] text-slate-950 selection:bg-teal-200">
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
