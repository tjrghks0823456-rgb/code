"use client";

import React, { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "../../components/Button";
import Card from "../../components/Card";
import PageShell from "../../components/PageShell";
import PersonaCard from "../../components/PersonaCard";
import SectionTitle from "../../components/SectionTitle";
import { dsaoCharacterList, getDsaoCharacter } from "../../data/dsaoCharacters";
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

  const selectedCharacter = getDsaoCharacter(myType || "DWML");

  return (
    <PageShell active="types">
      <div className="space-y-8">
        <section className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <SectionTitle
            eyebrow="persona guide"
            title="16가지 미디어 성향 유형"
            description="코드보다 캐릭터와 한 줄 설명이 먼저 보이도록 정리했습니다. 같은 구조의 카드로 비교하기 쉽게 맞췄습니다."
          />
          <Button type="button" tone="secondary" icon={<ArrowLeft size={18} />} onClick={() => router.back()}>
            이전 화면
          </Button>
        </section>

        <Card className="p-6 md:p-8">
          <div className="grid gap-5 md:grid-cols-[1fr_auto_1fr] md:items-center">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-700">나의 유형</p>
              <h2 className="mt-2 text-2xl font-black text-slate-950">{selectedCharacter.characterName}</h2>
              <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">{selectedCharacter.shortDescription}</p>
            </div>
            <div className="rounded-full border border-slate-200 bg-[#fbfaf7] px-4 py-2 text-sm font-black text-slate-500">
              vs
            </div>
            <div>
              <p className="text-xs font-black uppercase tracking-[0.18em] text-slate-400">평균 사용자</p>
              <h2 className="mt-2 text-2xl font-black text-slate-950">추천 피드 유람형</h2>
              <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
                여러 주제를 둘러보지만 피드 흐름에 따라 관심사가 빠르게 바뀌는 경향이 있습니다.
              </p>
            </div>
          </div>
        </Card>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {dsaoCharacterList.map((item) => (
            <PersonaCard key={item.code} character={item} selected={item.code === myType} />
          ))}
        </div>
      </div>
    </PageShell>
  );
}
