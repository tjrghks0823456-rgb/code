"use client";

import React, { useEffect, useState } from "react";
import { getDsaoCharacter, DsaoCharacterColor } from "../data/dsaoCharacters";

type CharacterAvatarProps = {
  code: string;
  size?: "sm" | "md" | "lg";
  showName?: boolean;
  className?: string;
};

const sizeClasses = {
  sm: {
    shell: "w-20 min-h-20 rounded-2xl p-2",
    emoji: "text-2xl",
    name: "text-[10px]",
    code: "text-[8px] px-1.5 py-0.5"
  },
  md: {
    shell: "w-28 min-h-28 rounded-3xl p-3",
    emoji: "text-4xl",
    name: "text-xs",
    code: "text-[9px] px-2 py-0.5"
  },
  lg: {
    shell: "w-36 min-h-36 rounded-3xl p-4",
    emoji: "text-5xl",
    name: "text-sm",
    code: "text-[10px] px-2.5 py-1"
  }
};

const gradientClasses: Record<DsaoCharacterColor, string> = {
  amber: "from-amber-300 via-orange-400 to-pink-500",
  blue: "from-blue-300 via-sky-500 to-indigo-600",
  cyan: "from-cyan-300 via-teal-400 to-blue-500",
  emerald: "from-emerald-300 via-teal-500 to-slate-700",
  fuchsia: "from-fuchsia-300 via-pink-500 to-purple-700",
  indigo: "from-indigo-300 via-violet-500 to-slate-800",
  lime: "from-lime-200 via-emerald-400 to-teal-600",
  orange: "from-orange-200 via-amber-500 to-rose-500",
  pink: "from-pink-300 via-rose-500 to-indigo-700",
  purple: "from-purple-300 via-violet-600 to-indigo-800",
  rose: "from-rose-300 via-pink-500 to-orange-500",
  sky: "from-sky-200 via-cyan-400 to-blue-600",
  teal: "from-teal-200 via-emerald-500 to-cyan-700",
  violet: "from-violet-300 via-purple-600 to-slate-800"
};

export default function CharacterAvatar({
  code,
  size = "md",
  showName = true,
  className = ""
}: CharacterAvatarProps) {
  const character = getDsaoCharacter(code);
  const [imageLoaded, setImageLoaded] = useState(false);
  const imagePath = character.imagePath;
  const selectedSize = sizeClasses[size];

  useEffect(() => {
    setImageLoaded(false);
    if (!imagePath) return;

    let isMounted = true;
    const image = new Image();
    image.onload = () => {
      if (isMounted) setImageLoaded(true);
    };
    image.onerror = () => {
      if (isMounted) setImageLoaded(false);
    };
    image.src = imagePath;

    return () => {
      isMounted = false;
    };
  }, [imagePath]);

  return (
    <div
      className={[
        "relative shrink-0 overflow-hidden border border-white/15 bg-gradient-to-br shadow-xl shadow-slate-950/30",
        gradientClasses[character.color],
        selectedSize.shell,
        className
      ].join(" ")}
      aria-label={`${character.characterName} ${character.code} 캐릭터 아바타`}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.35),transparent_28%),linear-gradient(145deg,rgba(255,255,255,0.18),transparent_45%)]" />
      <div className="absolute -bottom-6 -right-5 h-20 w-20 rounded-full bg-white/15 blur-xl" />

      <div className="relative z-10 flex h-full min-h-[inherit] flex-col items-center justify-center gap-1 text-center text-white">
        <span className={["drop-shadow-lg", selectedSize.emoji].join(" ")}>{character.emoji}</span>
        {showName && (
          <span className={["font-black leading-tight tracking-normal", selectedSize.name].join(" ")}>
            {character.characterName}
          </span>
        )}
        <span className={["rounded-full border border-white/25 bg-slate-950/30 font-black leading-none text-white/90 backdrop-blur", selectedSize.code].join(" ")}>
          {character.code}
        </span>
      </div>

      {imageLoaded && imagePath && (
        <img
          src={imagePath}
          alt={`${character.characterName} 캐릭터`}
          className="absolute inset-0 z-20 h-full w-full object-cover"
          onError={() => setImageLoaded(false)}
        />
      )}
    </div>
  );
}
