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
  amber: "from-amber-100 via-white to-orange-100",
  blue: "from-blue-100 via-white to-sky-100",
  cyan: "from-cyan-100 via-white to-teal-100",
  emerald: "from-emerald-100 via-white to-teal-100",
  fuchsia: "from-fuchsia-100 via-white to-pink-100",
  indigo: "from-indigo-100 via-white to-slate-100",
  lime: "from-lime-100 via-white to-emerald-100",
  orange: "from-orange-100 via-white to-amber-100",
  pink: "from-pink-100 via-white to-rose-100",
  purple: "from-purple-100 via-white to-indigo-100",
  rose: "from-rose-100 via-white to-orange-100",
  sky: "from-sky-100 via-white to-cyan-100",
  teal: "from-teal-100 via-white to-emerald-100",
  violet: "from-violet-100 via-white to-purple-100"
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
        "relative shrink-0 overflow-hidden border border-slate-200 bg-gradient-to-br shadow-sm",
        gradientClasses[character.color],
        selectedSize.shell,
        className
      ].join(" ")}
      aria-label={`${character.characterName} ${character.code} 캐릭터 아바타`}
    >
      <div className="absolute inset-0 bg-white/45" />

      <div className="relative z-10 flex h-full min-h-[inherit] flex-col items-center justify-center gap-1 text-center text-slate-900">
        <span className={selectedSize.emoji}>{character.emoji}</span>
        {showName && (
          <span className={["font-black leading-tight tracking-normal", selectedSize.name].join(" ")}>
            {character.characterName}
          </span>
        )}
        <span className={["rounded-full border border-slate-200 bg-white/80 font-black leading-none text-slate-600 backdrop-blur", selectedSize.code].join(" ")}>
          {character.code}
        </span>
      </div>

      {imageLoaded && imagePath && (
        <img
          src={imagePath}
          alt={`${character.characterName} 캐릭터`}
          className="absolute inset-0 z-20 h-full w-full object-contain p-1"
          onError={() => setImageLoaded(false)}
        />
      )}
    </div>
  );
}
