"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Activity, BarChart3, ClipboardList, FileUp, Home, Map, Target } from "lucide-react";

type PageShellProps = {
  children: React.ReactNode;
  active?: "home" | "survey" | "upload" | "dashboard" | "mission" | "types";
  compact?: boolean;
};

const navBase = [
  { href: "/", label: "홈", id: "home", icon: Home },
  { href: "/survey", label: "자가진단", id: "survey", icon: ClipboardList },
  { href: "/upload", label: "기록 업로드", id: "upload", icon: FileUp },
  { href: "/types", label: "유형", id: "types", icon: Map },
];

export default function PageShell({ children, active = "home", compact = false }: PageShellProps) {
  const [runId, setRunId] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setRunId(localStorage.getItem("latest_run_id"));
    }
  }, []);

  const navItems = [
    ...navBase,
    ...(runId ? [{ href: `/dashboard?run_id=${runId}`, label: "결과", id: "dashboard", icon: BarChart3 }] : []),
    { href: runId ? "/mission" : "/mission?demo=true", label: "미션", id: "mission", icon: Target },
  ];

  return (
    <div className="min-h-screen bg-[#f6f7f3] text-slate-950">
      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-[#f6f7f3]/92 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 md:px-8">
          <Link href="/" className="flex min-w-0 items-center gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-slate-950 text-sm font-black text-white">
              U
            </span>
            <span className="min-w-0">
              <span className="block truncate text-base font-black tracking-normal text-slate-950">UNBELIEVABLE</span>
              <span className="block truncate text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">
                media detox report
              </span>
            </span>
          </Link>

          <nav className="hidden items-center gap-1 rounded-2xl border border-slate-200 bg-white/80 p-1 shadow-sm md:flex">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.id}
                  href={item.href}
                  className={[
                    "inline-flex min-h-10 items-center gap-1.5 rounded-xl px-3 py-2 text-xs font-black transition",
                    active === item.id
                      ? "bg-slate-950 text-white"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-950",
                  ].join(" ")}
                >
                  <Icon size={14} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </header>

      <main className={compact ? "mx-auto max-w-5xl px-4 py-8 md:px-8" : "mx-auto max-w-7xl px-4 py-8 md:px-8 md:py-12"}>
        {children}
      </main>

      <footer className="mx-auto max-w-7xl px-4 pb-8 pt-4 text-xs font-semibold leading-6 text-slate-500 md:px-8">
        <span className="inline-flex items-center gap-1.5">
          <Activity size={14} />
          SH.SON_UNBELIEVABLE prototype
        </span>
        <span className="ml-2">분석 결과는 Google Takeout 기반 참고 지표이며, 디톡스 전후 변화를 확인하기 위한 보조 도구입니다.</span>
      </footer>
    </div>
  );
}
