"use client";

import React from "react";
import Link from "next/link";

type ButtonTone = "primary" | "secondary" | "ghost" | "soft";

const toneClasses: Record<ButtonTone, string> = {
  primary: "bg-slate-950 text-white shadow-lg shadow-slate-900/15 hover:bg-slate-800",
  secondary: "border border-slate-200 bg-white text-slate-800 hover:border-slate-300 hover:bg-slate-50",
  ghost: "text-slate-600 hover:bg-slate-100 hover:text-slate-950",
  soft: "border border-teal-100 bg-teal-50 text-teal-800 hover:bg-teal-100"
};

const baseClasses =
  "inline-flex min-h-11 items-center justify-center gap-2 rounded-2xl px-5 py-2.5 text-sm font-bold transition focus:outline-none focus:ring-2 focus:ring-slate-900/15 disabled:cursor-not-allowed disabled:opacity-45";

type SharedProps = {
  children: React.ReactNode;
  className?: string;
  icon?: React.ReactNode;
  tone?: ButtonTone;
};

export function Button({
  children,
  className = "",
  icon,
  tone = "primary",
  ...props
}: SharedProps & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button className={[baseClasses, toneClasses[tone], className].join(" ")} {...props}>
      {icon}
      <span>{children}</span>
    </button>
  );
}

export function ButtonLink({
  children,
  className = "",
  href,
  icon,
  tone = "primary"
}: SharedProps & { href: string }) {
  return (
    <Link href={href} className={[baseClasses, toneClasses[tone], className].join(" ")}>
      {icon}
      <span>{children}</span>
    </Link>
  );
}
