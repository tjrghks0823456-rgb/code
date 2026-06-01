import React from "react";
import { CheckCircle2, Circle } from "lucide-react";

type MissionCardProps = {
  title: string;
  description: string;
  label?: string;
  completed?: boolean;
  children?: React.ReactNode;
  onToggle?: () => void;
};

export default function MissionCard({
  title,
  description,
  label,
  completed = false,
  children,
  onToggle
}: MissionCardProps) {
  const Icon = completed ? CheckCircle2 : Circle;

  return (
    <div className={["rounded-3xl border bg-white p-5 shadow-sm transition", completed ? "border-teal-200" : "border-slate-200"].join(" ")}>
      <div className="flex items-start gap-4">
        <button
          type="button"
          onClick={onToggle}
          className="mt-0.5 text-teal-700 disabled:cursor-default"
          disabled={!onToggle}
          aria-label={completed ? "미션 완료됨" : "미션 완료 표시"}
        >
          <Icon size={24} strokeWidth={2.2} />
        </button>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-base font-black leading-tight text-slate-950">{title}</h3>
            {label && (
              <span className="rounded-full bg-amber-100 px-2.5 py-1 text-[10px] font-black text-amber-800">
                {label}
              </span>
            )}
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
          {children && <div className="mt-4">{children}</div>}
        </div>
      </div>
    </div>
  );
}

