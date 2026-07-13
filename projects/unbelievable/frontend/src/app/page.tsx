import React from "react";
import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  FileUp,
  GitCompare,
  ListChecks,
  Map,
  Radar,
  Search,
  ShieldCheck,
  Sparkles,
  Target,
} from "lucide-react";
import PageShell from "../components/PageShell";
import { ButtonLink } from "../components/Button";
import Card from "../components/Card";

const journeySteps = [
  {
    title: "자가진단",
    desc: "내가 생각하는 미디어 소비 성향을 먼저 기록합니다.",
    icon: ListChecks,
  },
  {
    title: "Takeout 업로드",
    desc: "검색 기록, 시청 기록, 숏츠 후보, 광고 제외 데이터를 정리합니다.",
    icon: FileUp,
  },
  {
    title: "결과 확인",
    desc: "그래프와 관심사 맵으로 현재 소비 패턴을 확인합니다.",
    icon: Radar,
  },
  {
    title: "미션 후 비교",
    desc: "디톡스 미션 이후 다시 분석해 전후 변화를 확인합니다.",
    icon: GitCompare,
  },
];

const reportCards = [
  {
    title: "관심사 지도",
    desc: "검색, 일반 시청, 숏츠 반복 관심사를 분리해서 보여줍니다.",
    icon: Map,
  },
  {
    title: "전후 변화",
    desc: "디톡스 미션 전후의 위험도, 다양성, 주도성을 한눈에 비교합니다.",
    icon: BarChart3,
  },
  {
    title: "데이터 신뢰도",
    desc: "광고 제외 수, 미분류 비율, Takeout 한계를 함께 안내합니다.",
    icon: ShieldCheck,
  },
];

const previewMetrics = [
  { label: "정보 편향 위험도", before: "72점", after: "58점", delta: "-14점" },
  { label: "숏츠 반복 위험", before: "81점", after: "64점", delta: "-17점" },
  { label: "관심사 다양성", before: "42점", after: "61점", delta: "+19점" },
];

export default function LandingPage() {
  return (
    <PageShell active="home">
      <div className="space-y-10">
        <section className="grid gap-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-stretch">
          <div className="rounded-[2rem] border border-slate-200 bg-white px-5 py-8 shadow-sm md:px-8 md:py-10">
            <p className="mb-4 inline-flex items-center gap-2 rounded-full bg-teal-50 px-3 py-1.5 text-xs font-black text-teal-800 ring-1 ring-teal-100">
              <Search size={14} /> YouTube 소비 패턴 분석
            </p>
            <h1 className="max-w-3xl text-4xl font-black leading-[1.08] text-slate-950 md:text-5xl lg:text-6xl">
              내가 보는 YouTube와 YouTube가 만든 나를 비교합니다
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 md:text-lg">
              자가진단과 Google Takeout 분석을 연결해 검색 관심사, 실제 시청 관심사, 숏츠 반복 패턴,
              디톡스 전후 변화를 보기 쉬운 리포트로 정리합니다.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <ButtonLink href="/upload" icon={<FileUp size={18} />} className="sm:min-w-60">
                실제 기록 업로드
              </ButtonLink>
              <ButtonLink href="/survey" icon={<ArrowRight size={18} />} tone="secondary" className="sm:min-w-60">
                자가진단 먼저 하기
              </ButtonLink>
            </div>

            <div className="mt-8 grid gap-3 md:grid-cols-4">
              {journeySteps.map((step, index) => {
                const Icon = step.icon;
                return (
                  <div key={step.title} className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
                    <div className="flex items-center gap-2 text-teal-700">
                      <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-teal-50 text-xs font-black ring-1 ring-teal-100">
                        {index + 1}
                      </span>
                      <Icon size={18} />
                    </div>
                    <h3 className="mt-4 text-base font-black text-slate-950">{step.title}</h3>
                    <p className="mt-2 text-xs font-semibold leading-5 text-slate-600">{step.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>

          <aside className="rounded-[2rem] border border-slate-200 bg-slate-950 p-5 text-white shadow-sm md:p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-300">detox comparison</p>
                <h2 className="mt-2 text-2xl font-black">미션 전후 변화가 핵심입니다</h2>
              </div>
              <Sparkles className="text-teal-300" size={30} />
            </div>

            <div className="mt-6 space-y-3">
              {previewMetrics.map((metric) => (
                <div key={metric.label} className="rounded-2xl border border-white/10 bg-white/8 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-black">{metric.label}</p>
                    <span className="rounded-full bg-teal-300 px-2.5 py-1 text-xs font-black text-slate-950">
                      {metric.delta}
                    </span>
                  </div>
                  <div className="mt-3 grid grid-cols-[1fr_auto_1fr] items-center gap-3 text-sm font-bold">
                    <span className="rounded-xl bg-white/10 px-3 py-2 text-center text-slate-300">{metric.before}</span>
                    <ArrowRight size={16} className="text-teal-300" />
                    <span className="rounded-xl bg-teal-300 px-3 py-2 text-center text-slate-950">{metric.after}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-5 rounded-2xl border border-teal-300/30 bg-teal-300/10 p-4">
              <p className="flex items-center gap-2 text-sm font-black text-teal-200">
                <Target size={17} /> 분석 → 미션 → 재분석
              </p>
              <p className="mt-2 text-sm font-semibold leading-6 text-slate-300">
                단순한 점수표가 아니라, 미션 이후 실제 소비 패턴이 어떻게 달라졌는지 확인하는 흐름을 중심에 둡니다.
              </p>
            </div>
          </aside>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          {reportCards.map((item) => {
            const Icon = item.icon;
            return (
              <Card key={item.title} className="p-5">
                <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-950 text-white">
                  <Icon size={18} />
                </div>
                <h3 className="text-base font-black text-slate-950">{item.title}</h3>
                <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">{item.desc}</p>
              </Card>
            );
          })}
        </section>

        <section className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm md:p-7">
          <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-700">readable report</p>
              <h2 className="mt-2 text-3xl font-black text-slate-950">처음에는 그래프, 세부 근거는 필요할 때만</h2>
              <p className="mt-3 text-sm font-semibold leading-6 text-slate-600">
                결과 화면은 핵심 그래프와 요약을 먼저 보여주고, 관심사 맵·계산 근거·데이터 신뢰도는 접을 수 있는 섹션으로 분리합니다.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {["핵심 그래프", "전후 비교", "세부 근거"].map((item) => (
                <div key={item} className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
                  <CheckCircle2 className="text-teal-700" size={18} />
                  <p className="mt-3 text-sm font-black text-slate-950">{item}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </PageShell>
  );
}
