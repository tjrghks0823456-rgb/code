import React from "react";
import { ArrowRight, Gauge, Map, RefreshCcw, Search, ShieldCheck, Sparkles } from "lucide-react";
import PageShell from "../components/PageShell";
import { ButtonLink } from "../components/Button";
import Card from "../components/Card";
import CharacterAvatar from "../components/CharacterAvatar";
import SectionTitle from "../components/SectionTitle";
import ScoreCard from "../components/ScoreCard";
import { categoryShares, reportInsights, resultPreviewStats, searchKeywords } from "../data/insightMock";

const interestChips = ["쇼츠", "게임", "뉴스", "야구", "음악", "공부", "먹방", "AI", "자기계발", "이슈"];

const featureCards = [
  {
    title: "관심사 지도",
    desc: "검색어와 시청 기록을 분리해서 내가 직접 찾은 것과 피드가 밀어준 것을 보여줍니다.",
    icon: <Map size={20} />
  },
  {
    title: "알고리즘 속 나",
    desc: "자가진단 결과와 실제 기록을 비교해 내 생각과 기록의 차이를 확인합니다.",
    icon: <Sparkles size={20} />
  },
  {
    title: "관심사 쏠림 정도",
    desc: "특정 주제 반복 노출이 강한지, 새로운 관점이 충분히 섞였는지 요약합니다.",
    icon: <Gauge size={20} />
  },
  {
    title: "리셋 미션",
    desc: "숙제처럼 무겁지 않은 작은 행동으로 오늘의 추천 흐름을 환기합니다.",
    icon: <RefreshCcw size={20} />
  }
];

export default function LandingPage() {
  return (
    <PageShell active="home">
      <section className="report-grid overflow-hidden rounded-[2rem] border border-slate-200 bg-white px-5 py-8 shadow-sm md:px-10 md:py-12">
        <div className="grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
          <div>
            <p className="mb-4 inline-flex items-center gap-2 rounded-full bg-teal-50 px-3 py-1.5 text-xs font-black text-teal-800 ring-1 ring-teal-100">
              <Search size={14} /> 내 알고리즘 속 미디어 성향 테스트
            </p>
            <h1 className="max-w-3xl text-4xl font-black leading-[1.08] text-slate-950 md:text-6xl">
              유튜브가 보는 나는 어떤 사람일까?
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 md:text-lg">
              최근 시청 기록과 자가진단을 비교해 내가 직접 찾은 관심사와 알고리즘이 보여준 관심사의 차이를 리포트로 정리합니다.
            </p>

            <div className="mt-7 flex flex-col gap-3 sm:flex-row">
              <ButtonLink href="/survey" icon={<ArrowRight size={18} />}>
                내 알고리즘 진단하기
              </ButtonLink>
              <ButtonLink href="/types" tone="secondary" icon={<Sparkles size={18} />}>
                유형 먼저 구경하기
              </ButtonLink>
            </div>

            <div className="mt-8 flex flex-wrap gap-2">
              {interestChips.map((chip) => (
                <span key={chip} className="interest-chip rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-bold text-slate-600 shadow-sm">
                  {chip}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-[2rem] border border-slate-200 bg-[#fbfaf7] p-5 shadow-sm">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-slate-400">preview report</p>
                <h2 className="mt-2 text-2xl font-black text-slate-950">내 알고리즘 리포트</h2>
                <p className="mt-2 text-sm leading-6 text-slate-600">자가진단 후 실제 기록 분석으로 더 정확해져요.</p>
              </div>
              <CharacterAvatar code="DWML" size="md" showName={false} />
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3">
              {resultPreviewStats.map((item) => (
                <div key={item.label} className="rounded-3xl border border-slate-200 bg-white p-4">
                  <p className="text-xs font-bold text-slate-500">{item.label}</p>
                  <p className="mt-1 text-2xl font-black text-slate-950">{item.value}</p>
                  <p className="mt-1 text-[11px] font-bold text-teal-700">{item.caption}</p>
                </div>
              ))}
            </div>

            <div className="mt-5 rounded-3xl border border-slate-200 bg-white p-4">
              <div className="mb-3 flex items-center justify-between">
                <p className="text-sm font-black text-slate-950">최근 관심 키워드 TOP5</p>
                <ShieldCheck size={18} className="text-teal-700" />
              </div>
              <div className="space-y-3">
                {searchKeywords.map((item, index) => (
                  <div key={item.keyword} className="flex items-center gap-3">
                    <span className="w-5 text-xs font-black text-slate-400">{index + 1}</span>
                    <span className="flex-1 text-sm font-bold text-slate-700">{item.keyword}</span>
                    <span className="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-black text-slate-500">
                      {item.category}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-5 rounded-3xl border border-teal-100 bg-teal-50 p-4">
              <p className="text-sm font-black text-slate-950">오늘의 리셋 미션</p>
              <p className="mt-2 text-sm font-semibold leading-6 text-slate-700">
                추천 영상 말고 직접 검색해서 하나 고르기
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-14">
        <SectionTitle
          eyebrow="what you get"
          title="처음엔 테스트처럼 가볍게, 결과는 리포트처럼 선명하게"
          description="딱딱한 분석 용어를 줄이고 사용자가 바로 이해할 수 있는 결과 중심 화면으로 정리했습니다."
          align="center"
        />
        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {featureCards.map((item) => (
            <Card key={item.title} className="min-h-48">
              <div className="mb-5 inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-950 text-white">
                {item.icon}
              </div>
              <h3 className="text-lg font-black text-slate-950">{item.title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">{item.desc}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="mt-14 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <div>
          <SectionTitle
            eyebrow="interest map"
            title="검색어 관심사 맵"
            description="실제 검색 기록 연동 전에는 더미 데이터로 UI를 구성했습니다. 원문 전체를 노출하기보다 카테고리와 요약 중심으로 보여줍니다."
          />
          <div className="mt-6 space-y-3">
            {reportInsights.map((text) => (
              <p key={text} className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold leading-6 text-slate-600">
                {text}
              </p>
            ))}
          </div>
        </div>
        <div className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-black text-slate-950">검색어 비중 버블</h3>
            <div className="mt-5 flex min-h-48 flex-wrap items-center justify-center gap-3">
              {searchKeywords.map((item) => (
                <span
                  key={item.keyword}
                  className="interest-chip rounded-full border border-slate-200 bg-white px-4 py-2 font-black text-slate-700 shadow-sm"
                  style={{ fontSize: `${Math.max(13, item.count + 2)}px` }}
                >
                  {item.keyword}
                </span>
              ))}
            </div>
          </Card>
          <div className="grid gap-4 md:grid-cols-2">
            {categoryShares.map((item) => (
              <ScoreCard
                key={item.name}
                label={item.name}
                value={`${item.value}%`}
                caption="최근 관심 카테고리 비중"
                tone={`${item.tone} text-white`}
              />
            ))}
          </div>
        </div>
      </section>
    </PageShell>
  );
}
