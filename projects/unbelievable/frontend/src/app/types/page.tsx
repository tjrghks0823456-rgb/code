"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import CharacterAvatar from "../../components/CharacterAvatar";
import { dsaoCharacterList } from "../../data/dsaoCharacters";
import { loadSelfSurveyResult } from "../../utils/surveyStorage";

export default function TypesPage() {
  const router = useRouter();
  const [myType, setMyType] = useState<string | null>(null);

  useEffect(() => {
    const survey = loadSelfSurveyResult();
    if (survey?.resultCode) {
      setMyType(survey.resultCode);
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 md:p-12 font-body relative">
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[10%] right-[20%] w-[35%] h-[35%] rounded-full bg-slate-900/30 blur-[120px]" />
      </div>

      <div className="max-w-6xl mx-auto space-y-8 relative z-10">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-900 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold text-white font-heading tracking-tight">
              DSAO 16유형 캐릭터 도감
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              시청 기록에서 관찰된 콘텐츠 소비 경향을 캐릭터 카드로 가볍게 비교해 보세요.
            </p>
          </div>
          <button
            onClick={() => router.back()}
            className="px-5 py-2.5 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white font-bold rounded-xl transition-all text-xs"
          >
            이전 화면으로 복귀
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {dsaoCharacterList.map((item) => {
            const isMyType = item.code === myType;

            return (
              <div
                key={item.code}
                className={`rounded-2xl p-5 border transition-all duration-300 relative flex min-h-[380px] flex-col justify-between ${
                  isMyType
                    ? "bg-purple-900/10 border-purple-500/60 shadow-[0_0_20px_rgba(168,85,247,0.15)] ring-1 ring-purple-500/25 scale-[1.02]"
                    : "bg-slate-900/30 border-slate-800/80 hover:border-slate-700/80 hover:bg-slate-900/40"
                }`}
              >
                {isMyType && (
                  <span className="absolute top-4 right-4 text-[8px] font-black uppercase bg-purple-500/20 text-purple-300 border border-purple-500/40 px-2 py-0.5 rounded-full tracking-wider">
                    My Type
                  </span>
                )}

                <div>
                  <div className="flex items-start gap-4">
                    <CharacterAvatar code={item.code} size="md" showName={false} />
                    <div className="min-w-0 pt-1">
                      <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-widest">
                        {item.code}
                      </span>
                      <h3 className="text-base font-bold text-white mt-1 font-heading leading-snug">
                        {item.name}
                      </h3>
                      <p className="text-xs font-semibold text-purple-300 mt-1">
                        캐릭터 {item.characterName}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1.5 mt-4">
                    {item.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-[8px] bg-slate-950 border border-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-medium"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  <p className="text-[11px] text-slate-400 mt-4 leading-relaxed border-t border-slate-800/60 pt-3">
                    {item.oneLiner}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-dashed border-slate-800/50 bg-slate-950/20 p-2.5 rounded-xl">
                  <span className="text-[9px] font-bold text-indigo-400 uppercase tracking-wider block">
                    소비 양상 예시
                  </span>
                  <p className="text-[10px] text-slate-500 mt-1 leading-relaxed">
                    {item.consumptionPattern}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
