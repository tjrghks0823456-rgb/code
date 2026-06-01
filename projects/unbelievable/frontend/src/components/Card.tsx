import React from "react";

type CardProps = {
  children: React.ReactNode;
  className?: string;
  as?: keyof JSX.IntrinsicElements;
};

export default function Card({ children, className = "", as: Tag = "section" }: CardProps) {
  return (
    <Tag className={["rounded-3xl border border-slate-200 bg-white p-5 shadow-sm", className].join(" ")}>
      {children}
    </Tag>
  );
}

