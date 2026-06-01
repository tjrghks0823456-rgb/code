"use client";

import React, { useMemo, useState } from "react";
import { ArrowLeft, ArrowRight, Check, RotateCcw, Upload } from "lucide-react";
import { useRouter } from "next/navigation";
import PageShell from "../../components/PageShell";
import { Button } from "../../components/Button";
import Card from "../../components/Card";
import ResultCard from "../../components/ResultCard";
import SectionTitle from "../../components/SectionTitle";
import { getDsaoCharacter } from "../../data/dsaoCharacters";
import { saveSelfSurveyResult, SelfSurveyResult } from "../../utils/surveyStorage";

interface Question {
  id: string;
  text: string;
  axis: "D" | "P" | "W" | "N" | "S" | "M" | "F" | "L";
}

const QUESTIONS: Question[] = [
  { id: "q1", text: "보고 싶은 영상은 추천보다 직접 찾아보는 편인가요?", axis: "D" },
  { id: "q2", text: "추천 피드를 따라가다 원래 보려던 것과 다른 영상을 오래 보나요?", axis: "P" },
  { id: "q3", text: "관심 있는 채널이나 주제를 정해두고 검색해 들어가나요?", axis: "D" },
  { id: "q4", text: "자동재생이나 다음 영상 흐름을 편하게 따라가는 편인가요?", axis: "P" },
  { id: "q5", text: "평소 여러 분야의 콘텐츠를 골고루 둘러보나요?", axis: "W" },
  { id: "q6", text: "한 번 관심이 생긴 주제는 관련 영상을 계속 이어서 보나요?", axis: "N" },
  { id: "q7", text: "뉴스, 취미, 학습, 예능처럼 카테고리를 자주 넘나드나요?", axis: "W" },
  { id: "q8", text: "특정 주제나 장르가 내 시청 기록에서 큰 비중을 차지하나요?", axis: "N" },
  { id: "q9", text: "자극적인 제목이나 썸네일이 있으면 궁금해서 눌러보나요?", axis: "S" },
  { id: "q10", text: "논쟁, 갈등, 분노를 다룬 콘텐츠를 자주 보게 되나요?", axis: "S" },
  { id: "q11", text: "자극적인 콘텐츠보다 차분한 설명이나 정보성 영상을 선호하나요?", axis: "M" },
  { id: "q12", text: "재미나 충격보다 신뢰도와 설명의 균형을 더 중요하게 보나요?", axis: "M" },
  { id: "q13", text: "짧은 영상이나 쇼츠를 빠르게 넘겨보는 편인가요?", axis: "F" },
  { id: "q14", text: "긴 영상보다 짧고 핵심만 있는 콘텐츠가 더 편한가요?", axis: "F" },
  { id: "q15", text: "관심 있는 주제라면 20분 이상의 긴 영상도 끝까지 보나요?", axis: "L" },
  { id: "q16", text: "하나의 주제를 깊게 이해하려고 긴 해설 영상이나 강의를 보나요?", axis: "L" }
];

const MODULES = [
  {
    name: "탐색 방식",
    code: "D/P",
    desc: "직접 검색하는지, 추천 흐름을 타는지 확인합니다."
  },
  {
    name: "관심 범위",
    code: "W/N",
    desc: "여러 주제를 넓게 보는지, 한 주제에 깊게 머무는지 확인합니다."
  },
  {
    name: "자극 성향",
    code: "S/M",
    desc: "강한 자극에 끌리는지, 안정적인 정보 흐름을 선호하는지 확인합니다."
  },
  {
    name: "시청 호흡",
    code: "F/L",
    desc: "짧은 숏폼 리듬인지, 긴 롱폼 몰입형인지 확인합니다."
  }
];

const scaleLabels = ["전혀 아니다", "아니다", "보통", "그렇다", "매우 그렇다"];

function getAxisSummary(code: string) {
  return [
    code.includes("D") ? "직접 탐색형" : "추천 탑승형",
    code.includes("W") ? "넓은 관심형" : "집중 관심형",
    code.includes("M") ? "안정 선호형" : "자극 반응형",
    code.includes("L") ? "롱폼 몰입형" : "숏폼 속도형"
  ];
}

export default function SurveyPage() {
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<SelfSurveyResult | null>(null);

  const pageQuestions = useMemo(
    () => QUESTIONS.slice(currentPage * 4, (currentPage + 1) * 4),
    [currentPage]
  );
  const answeredCount = Object.keys(answers).length;
  const progressPercent = result ? 100 : Math.round((answeredCount / QUESTIONS.length) * 100);
  const isPageComplete = pageQuestions.every((q) => answers[q.id] !== undefined);
  const allQuestionsAnswered = QUESTIONS.every((q) => answers[q.id] !== undefined);

  const handleAnswerSelect = (qId: string, score: number) => {
    setAnswers((prev) => ({ ...prev, [qId]: score }));
  };

  const calculateResult = () => {
    const D = (answers.q1 || 3) + (answers.q3 || 3);
    const P = (answers.q2 || 3) + (answers.q4 || 3);
    const W = (answers.q5 || 3) + (answers.q7 || 3);
    const N = (answers.q6 || 3) + (answers.q8 || 3);
    const S = (answers.q9 || 3) + (answers.q10 || 3);
    const M = (answers.q11 || 3) + (answers.q12 || 3);
    const F = (answers.q13 || 3) + (answers.q14 || 3);
    const L = (answers.q15 || 3) + (answers.q16 || 3);

    const resultCode = `${D >= P ? "D" : "P"}${W >= N ? "W" : "N"}${M >= S ? "M" : "S"}${L >= F ? "L" : "F"}`;
    const character = getDsaoCharacter(resultCode);
    const surveyResult: SelfSurveyResult = {
      answers,
      axisScores: { D, P, W, N, S, M, F, L },
      axisMargins: { DP: D - P, WN: W - N, SM: M - S, FL: L - F },
      resultCode,
      resultName: character.title,
      createdAt: new Date().toISOString(),
      schemaVersion: "1.0.0"
    };

    saveSelfSurveyResult(surveyResult);
    setResult(surveyResult);
    setCurrentPage(4);
  };

  const handleRetake = () => {
    setAnswers({});
    setResult(null);
    setCurrentPage(0);
  };

  if (result) {
    const character = getDsaoCharacter(result.resultCode);
    const axisSummary = getAxisSummary(result.resultCode);

    return (
      <PageShell active="survey" compact>
        <div className="space-y-8">
          <ResultCard character={character} code={result.resultCode} />

          <div className="grid gap-4 md:grid-cols-4">
            {axisSummary.map((item) => (
              <Card key={item} className="p-4">
                <p className="text-sm font-black text-slate-950">{item}</p>
              </Card>
            ))}
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            <Card>
              <h3 className="text-lg font-black text-slate-950">강점 3가지</h3>
              <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
                {character.strengths.map((item) => <li key={item}>- {item}</li>)}
              </ul>
            </Card>
            <Card>
              <h3 className="text-lg font-black text-slate-950">주의점 3가지</h3>
              <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
                {character.cautions.slice(0, 3).map((item) => <li key={item}>- {item}</li>)}
              </ul>
            </Card>
            <Card>
              <h3 className="text-lg font-black text-slate-950">추천 행동 3가지</h3>
              <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
                {character.recommendedAction.slice(0, 3).map((item) => <li key={item}>- {item}</li>)}
              </ul>
            </Card>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <Button type="button" tone="secondary" icon={<RotateCcw size={18} />} onClick={handleRetake}>
              다시 진단하기
            </Button>
            <Button type="button" className="sm:flex-1" icon={<Upload size={18} />} onClick={() => router.push("/upload")}>
              실제 소비 데이터 분석하기
            </Button>
          </div>
        </div>
      </PageShell>
    );
  }

  const module = MODULES[currentPage];

  return (
    <PageShell active="survey" compact>
      <div className="mx-auto max-w-3xl">
        <SectionTitle
          eyebrow={`step ${currentPage + 1} of 4`}
          title="내 미디어 성향을 가볍게 확인해볼게요"
          description="검사받는 느낌보다 나를 알아보는 테스트에 가깝게, 문항은 4개씩만 보여줍니다."
        />

        <div className="mt-6 rounded-full border border-slate-200 bg-white p-1">
          <div className="h-3 rounded-full bg-slate-950 transition-all" style={{ width: `${progressPercent}%` }} />
        </div>

        <Card className="mt-6 p-6 md:p-8">
          <div className="flex flex-col justify-between gap-4 border-b border-slate-200 pb-5 md:flex-row md:items-end">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-700">{module.code}</p>
              <h1 className="mt-2 text-3xl font-black text-slate-950">{module.name}</h1>
              <p className="mt-2 text-sm leading-6 text-slate-600">{module.desc}</p>
            </div>
            <p className="text-sm font-bold text-slate-500">{answeredCount} / {QUESTIONS.length} 응답</p>
          </div>

          <div className="mt-6 space-y-5">
            {pageQuestions.map((question, index) => (
              <div key={question.id} className="rounded-3xl border border-slate-200 bg-[#fbfaf7] p-4 md:p-5">
                <div className="flex gap-3">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-2xl bg-slate-950 text-xs font-black text-white">
                    {currentPage * 4 + index + 1}
                  </span>
                  <h2 className="pt-1 text-base font-black leading-6 text-slate-950">{question.text}</h2>
                </div>
                <div className="mt-4 grid grid-cols-5 gap-2">
                  {[1, 2, 3, 4, 5].map((score) => {
                    const selected = answers[question.id] === score;
                    return (
                      <button
                        key={score}
                        type="button"
                        onClick={() => handleAnswerSelect(question.id, score)}
                        className={[
                          "min-h-14 rounded-2xl border px-1 text-center transition",
                          selected
                            ? "border-slate-950 bg-slate-950 text-white"
                            : "border-slate-200 bg-white text-slate-600 hover:border-slate-300"
                        ].join(" ")}
                      >
                        <span className="block text-sm font-black">{score}</span>
                        <span className="mt-1 hidden text-[10px] font-bold sm:block">{scaleLabels[score - 1]}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-7 flex flex-col justify-between gap-3 border-t border-slate-200 pt-5 sm:flex-row">
            <Button
              type="button"
              tone="secondary"
              icon={<ArrowLeft size={18} />}
              disabled={currentPage === 0}
              onClick={() => setCurrentPage((prev) => Math.max(0, prev - 1))}
            >
              이전
            </Button>
            {currentPage < 3 ? (
              <Button
                type="button"
                icon={<ArrowRight size={18} />}
                disabled={!isPageComplete}
                onClick={() => setCurrentPage((prev) => prev + 1)}
              >
                다음
              </Button>
            ) : (
              <Button
                type="button"
                icon={<Check size={18} />}
                disabled={!allQuestionsAnswered}
                onClick={calculateResult}
              >
                결과 확인하기
              </Button>
            )}
          </div>
        </Card>
      </div>
    </PageShell>
  );
}
