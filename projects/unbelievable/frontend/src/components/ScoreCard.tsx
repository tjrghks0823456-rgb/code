import React from "react";

type ScoreCardProps = {
  label: string;
  value: string | number;
  caption?: string;
  tone?: string;
};

export default function ScoreCard({
  label,
  value,
  caption,
  tone = "bg-slate-950 text-white"
}: ScoreCardProps) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className={["mb-4 inline-flex rounded-2xl px-3 py-2 text-xs font-black", tone].join(" ")}>
        {label}
      </div>
      <div className="text-3xl font-black tracking-normal text-slate-950">{value}</div>
      {caption && <p className="mt-2 text-sm font-semibold leading-5 text-slate-500">{caption}</p>}
    </div>
  );
}

