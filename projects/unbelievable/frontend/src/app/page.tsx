import React from "react";
import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  FileUp,
  ListChecks,
  Map,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import PageShell from "../components/PageShell";
import { ButtonLink } from "../components/Button";
import Card from "../components/Card";
import CharacterAvatar from "../components/CharacterAvatar";

const flowSteps = [
  {
    title: "자가진단",
    desc: "16문항으로 내가 생각하는 미디어 소비 습관을 먼저 확인합니다.",
    icon: <ListChecks size={18} />,
  },
  {
    title: "기록 업로드",
    desc: "Google Takeout의 YouTube 기록을 올려 실제 소비 패턴을 분석합니다.",
    icon: <FileUp size={18} />,
  },
  {
    title: "비교 리포트",
    desc: "직접 검색, 실제 시청, 숏츠 반복 관심사를 나눠서 보여줍니다.",
    icon: <BarChart3 size={18} />,
  },
];

const reportHighlights = [
  {
    title: "관심사 맵",
    desc: "검색 기반 관심과 실제 시청 관심을 분리해서 확인합니다.",
    icon: <Map size={18} />,
  },
  {
    title: "생각과 기록 차이",
    desc: "자가진단 결과와 실제 기록 사이의 메타인지 격차를 보여줍니다.",
    icon: <Sparkles size={18} />,
  },
  {
    title: "분석 참고 안내",
    desc: "광고 제외, 타임스탬프 품질, 미분류 비율을 함께 안내합니다.",
    icon: <ShieldCheck size={18} />,
  },
];

const sampleKeywords = ["류현진 인터뷰", "이강인", "MBC 뉴스", "노트북 추천", "AI"];

export default function LandingPage() {
  return (
    <PageShell active="home">
      <section className="grid gap-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-start">
        <div className="space-y-8">
          <div className="rounded-[2rem] border border-slate-200 bg-white px-5 py-8 shadow-sm md:px-8 md:py-10">
            <p className="mb-4 inline-flex items-center gap-2 rounded-full bg-teal-50 px-3 py-1.5 text-xs font-black text-teal-800 ring-1 ring-teal-100">
              <Search size={14} /> 내 알고리즘 속 미디어 성향 테스트
            </p>
            <h1 className="max-w-3xl text-4xl font-black leading-[1.08] text-slate-950 md:text-5xl lg:text-6xl">
              내가 보는 유튜브와 유튜브가 보는 나를 비교합니다
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 md:text-lg">
              가벼운 자가진단과 실제 YouTube 기록 분석을 연결해, 내가 직접 찾은 관심사와 실제로 많이 소비한 관심사의 차이를 한 화면에서 정리합니다.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <ButtonLink href="/survey" icon={<ArrowRight size={18} />} className="sm:min-w-60">
                자가진단부터 시작하기
              </ButtonLink>
              <ButtonLink href="/upload" icon={<FileUp size={18} />} tone="secondary" className="sm:min-w-60">
                기록만 바로 분석하기
              </ButtonLink>
            </div>

            <p className="mt-5 text-xs font-semibold leading-relaxed text-slate-500">
              자가진단 없이도 기록 분석은 가능합니다. 둘 다 완료하면 생각과 실제 기록 사이의 차이를 더 선명하게 볼 수 있습니다.
            </p>

            <div className="mt-8 grid gap-3 md:grid-cols-3">
              {flowSteps.map((step, index) => (
                <div key={step.title} className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
                  <div className="flex items-center gap-2 text-teal-700">
                    <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-teal-50 text-xs font-black ring-1 ring-teal-100">
                      {index + 1}
                    </span>
                    {step.icon}
                  </div>
                  <h3 className="mt-4 text-base font-black text-slate-950">{step.title}</h3>
                  <p className="mt-2 text-xs font-semibold leading-5 text-slate-600">{step.desc}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {reportHighlights.map((item) => (
              <Card key={item.title} className="p-5">
                <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-950 text-white">
                  {item.icon}
                </div>
                <h3 className="text-base font-black text-slate-950">{item.title}</h3>
                <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">{item.desc}</p>
              </Card>
            ))}
          </div>
        </div>

        <aside className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm md:p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.18em] text-slate-400">report preview</p>
              <h2 className="mt-2 text-2xl font-black text-slate-950">결과는 이렇게 정리돼요</h2>
              <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
                처음에는 요약 그래프를 먼저 보고, 세부 근거는 필요한 항목을 눌러 확인하는 흐름을 목표로 합니다.
              </p>
            </div>
            <CharacterAvatar code="DWML" size="md" showName={false} />
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
              <p className="text-xs font-bold text-slate-500">관심사 불일치</p>
              <p className="mt-1 text-3xl font-black text-slate-950">42점</p>
              <p className="mt-1 text-[11px] font-black text-teal-700">검색 vs 시청 비교</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
              <p className="text-xs font-bold text-slate-500">광고 제외</p>
              <p className="mt-1 text-3xl font-black text-slate-950">자동</p>
              <p className="mt-1 text-[11px] font-black text-teal-700">품질 요약 제공</p>
            </div>
          </div>

          <div className="mt-5 rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
            <div className="mb-3 flex items-center justify-between">
              <p className="text-sm font-black text-slate-950">예시 검색어</p>
              <CheckCircle2 size={18} className="text-teal-700" />
            </div>
            <div className="flex flex-wrap gap-2">
              {sampleKeywords.map((keyword) => (
                <span key={keyword} className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-black text-slate-700 shadow-sm">
                  {keyword}
                </span>
              ))}
            </div>
          </div>

          <div className="mt-5 rounded-2xl border border-teal-100 bg-teal-50 p-4">
            <p className="text-sm font-black text-slate-950">추천 흐름 영향 후보</p>
            <p className="mt-2 text-sm font-semibold leading-6 text-slate-700">
              Google Takeout만으로 추천 경로를 확정하지 않고, 검색 대비 많이 소비된 주제를 후보로만 표시합니다.
            </p>
          </div>
        </aside>
      </section>
    </PageShell>
  );
}
