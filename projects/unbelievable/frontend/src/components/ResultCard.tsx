import React from "react";
import CharacterAvatar from "./CharacterAvatar";
import { DsaoCharacter } from "../data/dsaoCharacters";

type ResultCardProps = {
  character: DsaoCharacter;
  code: string;
  summary?: string;
};

export default function ResultCard({ character, code, summary }: ResultCardProps) {
  return (
    <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-sm">
      <div className="grid gap-6 p-6 md:grid-cols-[auto_1fr] md:p-8">
        <CharacterAvatar code={code} size="lg" showName={false} />
        <div className="min-w-0">
          <p className="text-xs font-black uppercase tracking-[0.2em] text-teal-700">미디어 성향 유형</p>
          <h2 className="mt-2 text-3xl font-black leading-tight text-slate-950 md:text-4xl">
            {character.characterName}
          </h2>
          <p className="mt-2 text-lg font-bold text-slate-700">{character.title}</p>
          <div className="mt-3 inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-black text-slate-600">
            {code}
          </div>
          <p className="mt-5 max-w-2xl text-sm leading-6 text-slate-600">
            {summary || character.shortDescription}
          </p>
        </div>
      </div>
    </section>
  );
}

