import React from "react";
import Link from "next/link";

type PageShellProps = {
  children: React.ReactNode;
  active?: "home" | "survey" | "upload" | "dashboard" | "mission" | "types";
  compact?: boolean;
};

const navItems = [
  { href: "/", label: "홈", id: "home" },
  { href: "/survey", label: "진단", id: "survey" },
  { href: "/upload", label: "분석", id: "upload" },
  { href: "/types", label: "유형", id: "types" },
  { href: "/mission?demo=true", label: "미션", id: "mission" }
];

export default function PageShell({ children, active = "home", compact = false }: PageShellProps) {
  return (
    <div className="min-h-screen bg-[#f7f4ee] text-slate-950">
      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-[#f7f4ee]/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 md:px-8">
          <Link href="/" className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-950 text-sm font-black text-white">
              U
            </span>
            <span>
              <span className="block text-base font-black tracking-normal text-slate-950">UNBELIEVABLE</span>
              <span className="block text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
                media tendency report
              </span>
            </span>
          </Link>
          <nav className="hidden items-center gap-1 rounded-2xl border border-slate-200 bg-white/70 p-1 md:flex">
            {navItems.map((item) => (
              <Link
                key={item.id}
                href={item.href}
                className={[
                  "rounded-xl px-3 py-2 text-xs font-bold transition",
                  active === item.id ? "bg-slate-950 text-white" : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
                ].join(" ")}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className={compact ? "mx-auto max-w-5xl px-4 py-8 md:px-8" : "mx-auto max-w-7xl px-4 py-8 md:px-8 md:py-12"}>
        {children}
      </main>
      <footer className="mx-auto max-w-7xl px-4 pb-8 pt-4 text-xs text-slate-500 md:px-8">
        SH.SON_UNBELIEVABLE prototype. 분석 데이터는 결과 생성 목적 외에는 사용하지 않아요.
      </footer>
    </div>
  );
}

