import React from "react";
import CharacterAvatar from "./CharacterAvatar";
import { DsaoCharacter } from "../data/dsaoCharacters";

type PersonaCardProps = {
  character: DsaoCharacter;
  selected?: boolean;
};

export default function PersonaCard({ character, selected = false }: PersonaCardProps) {
  return (
    <article
      className={[
        "flex h-full flex-col rounded-3xl border bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md",
        selected ? "border-slate-950 ring-4 ring-slate-950/10" : "border-slate-200"
      ].join(" ")}
    >
      <div className="flex items-start gap-4">
        <CharacterAvatar code={character.code} size="md" showName={false} />
        <div className="min-w-0">
          <p className="text-xs font-black uppercase tracking-[0.16em] text-slate-400">{character.code}</p>
          <h3 className="mt-1 text-lg font-black leading-tight text-slate-950">{character.characterName}</h3>
          <p className="mt-1 text-sm font-bold text-slate-600">{character.title}</p>
        </div>
      </div>
      <p className="mt-4 text-sm leading-6 text-slate-600">{character.shortDescription}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {character.tags.slice(0, 3).map((tag) => (
          <span key={tag} className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-bold text-slate-600">
            {tag}
          </span>
        ))}
      </div>
    </article>
  );
}

