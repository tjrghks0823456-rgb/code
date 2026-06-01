import React from "react";

type SectionTitleProps = {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: "left" | "center";
};

export default function SectionTitle({
  eyebrow,
  title,
  description,
  align = "left"
}: SectionTitleProps) {
  const centered = align === "center";

  return (
    <div className={centered ? "mx-auto max-w-2xl text-center" : "max-w-2xl"}>
      {eyebrow && (
        <p className="mb-2 text-xs font-black uppercase tracking-[0.18em] text-teal-700">
          {eyebrow}
        </p>
      )}
      <h2 className="text-2xl font-black leading-tight text-slate-950 md:text-3xl">
        {title}
      </h2>
      {description && (
        <p className="mt-3 text-sm leading-6 text-slate-600 md:text-base">{description}</p>
      )}
    </div>
  );
}

