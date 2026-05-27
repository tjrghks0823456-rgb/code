import React from "react";
import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "언블리버블 (SH.SON_UNBELIEVABLE) - 디지털 편향 진단 및 맞춤 디톡스",
  description: "YouTube 시청 기록을 정량 분석하여 사전 자가진단 결과와 실제 소비 간의 메타인지 격차를 시각적으로 분석하고 개인 맞춤형 디톡스 가이드를 제시합니다.",
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
      <body className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-purple-500/30">
        {/* Glow ambient background effects */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
          <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-purple-900/10 blur-[120px] animate-pulse-slow" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-blue-900/10 blur-[120px] animate-pulse-slow" />
        </div>
        
        {/* Core Layout Shell */}
        <main className="flex-1 flex flex-col z-10">
          {children}
        </main>
      </body>
    </html>
  );
}
