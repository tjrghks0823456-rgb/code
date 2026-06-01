"use client";

import React, { Suspense, useEffect, useMemo, useState } from "react";
import { AlertTriangle, ArrowRight, RefreshCcw, Search, Sparkles } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "../../components/Button";
import Card from "../../components/Card";
import PageShell from "../../components/PageShell";
import RadarChart from "../../components/RadarChart";
import ResultCard from "../../components/ResultCard";
import ScoreCard from "../../components/ScoreCard";
import SectionTitle from "../../components/SectionTitle";
import { categoryShares, reportInsights, searchKeywords } from "../../data/insightMock";
import { getDsaoCharacter } from "../../data/dsaoCharacters";
import { loadSelfSurveyResult, SelfSurveyResult } from "../../utils/surveyStorage";

type ApiData = any;

function getRiskLabel(score: number) {
  if (score < 20) return "안정";
  if (score < 40) return "낮음";
  if (score < 60) return "주의";
  if (score < 80) return "높음";
  return "매우 높음";
}

function axisSummary(code?: string) {
  const value = (code || "PNML").toUpperCase();
  return [
    value.includes("D") ? "직접 탐색" : "추천 흐름",
    value.includes("W") ? "넓은 관심" : "집중 관심",
    value.includes("M") ? "안정 정보" : "강한 자극",
    value.includes("L") ? "롱폼 몰입" : "숏폼 속도"
  ];
}

const riskSignals = [
  { label: "균형", tone: "bg-emerald-500" },
  { label: "반복 증가", tone: "bg-yellow-400" },
  { label: "편향 주의", tone: "bg-orange-500" },
  { label: "강한 필터버블", tone: "bg-rose-600" }
];

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const runId = searchParams.get("run_id");

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<ApiData>(null);
  const [selfSurvey, setSelfSurvey] = useState<SelfSurveyResult | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [generatingPlan, setGeneratingPlan] = useState(false);
  const [detoxError, setDetoxError] = useState<string | null>(null);

  useEffect(() => {
    const survey = loadSelfSurveyResult();
    setSelfSurvey(survey);

    if (!runId) {
      setApiError("분석 ID가 없습니다. 시청 기록 분석을 먼저 완료해주세요.");
      setLoading(false);
      return;
    }

    const fetchSummary = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/dashboard/summary?run_id=${runId}&user_id=00000000-0000-0000-0000-000000000001`);
        if (!res.ok) {
          throw new Error(`대시보드 조회 실패 (HTTP ${res.status})`);
        }
        setData(await res.json());
      } catch (err: any) {
        console.error("Dashboard fetch failed:", err);
        setApiError(err.message || "분석 결과를 불러오지 못했습니다.");
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, [runId]);

  const handleStartDetox = async () => {
    if (!runId) return;
    setGeneratingPlan(true);
    setDetoxError(null);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/detox/generate?run_id=${runId}&user_id=00000000-0000-0000-0000-000000000001`, {
        method: "POST"
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.plan_id) {
          router.push(`/mission?plan_id=${json.plan_id}`);
          return;
        }
        setDetoxError(json.detail || "미션 생성 결과가 비어 있습니다.");
      } else {
        const errorText = await res.text();
        let parsedDetail = "서버 내부 오류가 발생했습니다.";
        try {
          parsedDetail = JSON.parse(errorText).detail || parsedDetail;
        } catch (_) {}
        setDetoxError(`미션 생성 실패 (HTTP ${res.status}): ${parsedDetail}`);
      }
    } catch (err: any) {
      console.error("Detox plan generation failed:", err);
      setDetoxError(`미션 생성 오류: ${err.message || "네트워크 연결을 확인해주세요."}`);
    } finally {
      setGeneratingPlan(false);
    }
  };

  const processedData = useMemo(() => {
    if (!data) return null;
    const clone = JSON.parse(JSON.stringify(data));

    if (!selfSurvey?.axisScores || !clone.meta_gap) {
      return clone;
    }

    const { D, P, W, N, S, M } = selfSurvey.axisScores;
    const safeDiv = (num: number, den: number, fallback = 50) => {
      if (den === 0) return fallback;
      return Math.round((num / den) * 100);
    };

    const surveyValues: Record<string, number> = {
      UAS: safeDiv(D, D + P),
      TDS: safeDiv(W, W + N),
      SMS: safeDiv(M, S + M),
      EBS: 50,
      VOS: safeDiv(W, W + N),
      SBS: 50
    };

    const axisNames: Record<string, string> = {
      TDS: "주제 다양성",
      SBS: "추천 균형",
      EBS: "감정 균형",
      VOS: "관점 개방성",
      SMS: "유해/자극 안전",
      UAS: "사용자 주도성"
    };

    let maxGapValue = -1;
    let worstAxisCode = "TDS";

    Object.keys(clone.meta_gap).forEach((code) => {
      if (surveyValues[code] !== undefined) {
        const surveyValue = surveyValues[code];
        const actualValue = Number(clone.meta_gap[code].actual || 0);
        const gap = surveyValue - actualValue;

        clone.meta_gap[code].survey = surveyValue;
        clone.meta_gap[code].gap = Math.round(gap * 10) / 10;

        if (Math.abs(gap) > maxGapValue) {
          maxGapValue = Math.abs(gap);
          worstAxisCode = code;
        }
      }
    });

    const axisCodes = Object.keys(clone.meta_gap);
    const avgGap = axisCodes.reduce((sum, code) => sum + Math.abs(Number(clone.meta_gap[code].gap || 0)), 0) / Math.max(axisCodes.length, 1);
    const misconceptionIndex = Math.min(100, Math.round(avgGap * 1.5 * 10) / 10);

    clone.misconception = {
      index: misconceptionIndex,
      worst_axis_code: worstAxisCode,
      worst_axis_name: axisNames[worstAxisCode],
      worst_gap_value: clone.meta_gap[worstAxisCode]?.gap || 0,
      message: `내 생각과 실제 기록의 차이가 가장 큰 영역은 ${axisNames[worstAxisCode]}입니다. 추천 흐름을 한 번씩 끊어보면 균형을 회복하는 데 도움이 됩니다.`
    };

    return clone;
  }, [data, selfSurvey]);

  if (loading) {
    return (
      <PageShell active="dashboard" compact>
        <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
          <div className="mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-950" />
          <p className="font-bold text-slate-600">시청 기록 리포트를 구성하는 중입니다.</p>
        </div>
      </PageShell>
    );
  }

  if (apiError || !processedData) {
    return (
      <PageShell active="dashboard" compact>
        <Card className="mx-auto max-w-lg p-8 text-center">
          <AlertTriangle className="mx-auto text-rose-600" size={40} />
          <h1 className="mt-4 text-2xl font-black text-slate-950">분석 결과를 불러올 수 없습니다</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">FastAPI 서버가 실행 중인지, 분석 ID가 올바른지 확인해주세요.</p>
          <p className="mt-4 rounded-2xl bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-700">{apiError}</p>
          <Button type="button" className="mt-5 w-full" onClick={() => router.push("/upload")}>
            시청 기록 분석으로 돌아가기
          </Button>
        </Card>
      </PageShell>
    );
  }

  const metaGap = processedData.meta_gap || {};
  const scoreWarnings = Array.isArray(processedData.score_warnings) ? processedData.score_warnings : [];
  const chartData = Object.keys(metaGap).map((key) => ({
    axisCode: key,
    subject: metaGap[key].name || key,
    자가진단_결과: Number(metaGap[key].survey || 0),
    실제_분석값: Number(metaGap[key].actual || 0)
  }));

  const actualCode = processedData.actual_dsao?.code?.toUpperCase() || "PNML";
  const actualCharacter = getDsaoCharacter(actualCode);
  const selfCharacter = getDsaoCharacter(selfSurvey?.resultCode || actualCode);
  const riskScore = Number(processedData.bias_risk_score || 0);
  const userAgency = Math.round(Number(metaGap.UAS?.actual || 0));
  const diversity = Math.round(Number(metaGap.TDS?.actual || categoryShares.length * 10));
  const misconceptionIndex = Math.round(Number(processedData.misconception?.index || 0));

  return (
    <PageShell active="dashboard">
      <div className="space-y-10">
        {detoxError && (
          <div className="rounded-3xl border border-rose-200 bg-rose-50 p-5 text-sm font-semibold leading-6 text-rose-700">
            {detoxError}
          </div>
        )}

        <section className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <SectionTitle
            eyebrow="analysis report"
            title="손석환님의 알고리즘 리포트입니다"
            description="내가 직접 찾은 관심사와 시청 기록이 보여주는 관심사를 나란히 비교했습니다."
          />
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button type="button" tone="secondary" icon={<Search size={18} />} onClick={() => router.push("/types")}>
              유형 비교
            </Button>
            <Button type="button" icon={<RefreshCcw size={18} />} disabled={generatingPlan} onClick={handleStartDetox}>
              {generatingPlan ? "미션 생성 중" : "오늘의 리셋 미션"}
            </Button>
          </div>
        </section>

        <div className="grid gap-4 md:grid-cols-4">
          <ScoreCard label="관심사 쏠림" value={`${riskScore}점`} caption={`${getRiskLabel(riskScore)} 단계`} tone="bg-rose-500 text-white" />
          <ScoreCard label="생각과 기록 차이" value={`${misconceptionIndex}점`} caption={processedData.misconception?.worst_axis_name || "메타인지 갭"} tone="bg-amber-500 text-white" />
          <ScoreCard label="관심사 다양성" value={`${diversity}점`} caption="시청 기록 기준" tone="bg-sky-500 text-white" />
          <ScoreCard label="사용자 주도성" value={`${userAgency}%`} caption="직접 탐색 비중" tone="bg-teal-600 text-white" />
        </div>

        <Card className="p-5">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-700">bias signal</p>
              <h2 className="mt-1 text-xl font-black text-slate-950">
                현재 관심사 편향 상태는 {riskScore < 40 ? "초록 단계" : riskScore < 60 ? "노랑 단계" : riskScore < 80 ? "주황 단계" : "빨강 단계"}입니다.
              </h2>
              <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
                최근 검색어와 시청 기록이 특정 주제에 반복적으로 집중되는지 신호등처럼 표시합니다.
              </p>
            </div>
            <div className="grid min-w-72 grid-cols-4 gap-2">
              {riskSignals.map((signal, index) => {
                const active = riskScore >= index * 25;
                return (
                  <div key={signal.label} className="text-center">
                    <div className={["mx-auto h-4 rounded-full", active ? signal.tone : "bg-slate-200"].join(" ")} />
                    <p className="mt-2 text-[10px] font-black text-slate-500">{signal.label}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </Card>

        <div className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <RadarChart data={chartData} scoreWarnings={scoreWarnings} />

          <Card className="p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-700">search map</p>
                <h2 className="mt-2 text-2xl font-black text-slate-950">검색어 관심사 맵</h2>
              </div>
              <Sparkles className="text-teal-700" size={24} />
            </div>
            <div className="mt-5 space-y-3">
              {searchKeywords.map((item, index) => (
                <div key={item.keyword} className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-[#fbfaf7] px-4 py-3">
                  <span className="text-xs font-black text-slate-400">{index + 1}</span>
                  <span className="flex-1 text-sm font-black text-slate-800">{item.keyword}</span>
                  <span className="text-xs font-bold text-slate-500">{item.count}회</span>
                </div>
              ))}
            </div>
            <div className="mt-5 rounded-3xl border border-slate-200 bg-[#fbfaf7] p-4">
              <p className="text-sm font-black text-slate-950">검색어 비중 버블</p>
              <div className="mt-4 flex flex-wrap items-center gap-2">
                {searchKeywords.map((item) => (
                  <span
                    key={item.keyword}
                    className="rounded-full bg-white px-3 py-1.5 font-black text-slate-700 shadow-sm"
                    style={{ fontSize: `${Math.max(12, item.count + 1)}px` }}
                  >
                    {item.keyword}
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-5 space-y-3">
              {categoryShares.map((item) => (
                <div key={item.name}>
                  <div className="mb-1 flex justify-between text-xs font-black text-slate-500">
                    <span>{item.name}</span>
                    <span>{item.value}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-100">
                    <div className={["h-full rounded-full", item.tone].join(" ")} style={{ width: `${item.value}%` }} />
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <div className="rounded-3xl border border-slate-200 bg-white p-4">
                <p className="text-xs font-black uppercase tracking-[0.16em] text-slate-400">내가 직접 찾은 관심사</p>
                <p className="mt-3 text-sm font-bold leading-6 text-slate-700">자기계발 · 디지털 디톡스 · 노트북 추천</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-white p-4">
                <p className="text-xs font-black uppercase tracking-[0.16em] text-slate-400">알고리즘이 많이 보여준 관심사</p>
                <p className="mt-3 text-sm font-bold leading-6 text-slate-700">쇼츠 · 이슈 영상 · 자극형 콘텐츠</p>
              </div>
            </div>
            <p className="mt-5 text-xs font-semibold leading-5 text-slate-500">
              분석 데이터는 결과 생성 목적 외에는 사용하지 않아요.
            </p>
          </Card>
        </div>

        {selfSurvey && (
          <Card className="p-6 md:p-8">
            <div className="mb-6">
              <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-700">core comparison</p>
              <h2 className="mt-2 text-2xl font-black text-slate-950">자가진단 결과 vs 실제 분석 결과</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">내가 생각한 성향과 기록에서 드러난 성향을 비교합니다.</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-3xl border border-slate-200 bg-[#fbfaf7] p-5">
                <p className="text-xs font-black uppercase tracking-[0.18em] text-slate-400">자가진단</p>
                <h3 className="mt-2 text-2xl font-black text-slate-950">{selfCharacter.characterName}</h3>
                <p className="mt-1 text-sm font-bold text-slate-600">{selfSurvey.resultCode} · {selfCharacter.title}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {axisSummary(selfSurvey.resultCode).map((item) => (
                    <span key={item} className="rounded-full bg-white px-3 py-1 text-xs font-bold text-slate-600">{item}</span>
                  ))}
                </div>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-[#fbfaf7] p-5">
                <p className="text-xs font-black uppercase tracking-[0.18em] text-slate-400">실제 시청 기록</p>
                <h3 className="mt-2 text-2xl font-black text-slate-950">{actualCharacter.characterName}</h3>
                <p className="mt-1 text-sm font-bold text-slate-600">{actualCode} · {actualCharacter.title}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {axisSummary(actualCode).map((item) => (
                    <span key={item} className="rounded-full bg-white px-3 py-1 text-xs font-bold text-slate-600">{item}</span>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        )}

        <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
          <ResultCard
            character={actualCharacter}
            code={actualCode}
            summary={processedData.misconception?.message || actualCharacter.shortDescription}
          />

          <Card className="p-6 md:p-8">
            <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-700">insight summary</p>
            <h2 className="mt-2 text-2xl font-black text-slate-950">짧은 해석</h2>
            <div className="mt-5 space-y-3">
              {reportInsights.map((item) => (
                <p key={item} className="rounded-2xl bg-[#fbfaf7] px-4 py-3 text-sm font-semibold leading-6 text-slate-600">
                  {item}
                </p>
              ))}
              <p className="rounded-2xl bg-[#fbfaf7] px-4 py-3 text-sm font-semibold leading-6 text-slate-600">
                {processedData.misconception?.message || "특정 주제 반복 노출과 직접 탐색 비중을 함께 보면 내 알고리즘의 방향을 더 선명하게 볼 수 있어요."}
              </p>
            </div>
            <Button type="button" className="mt-6 w-full" icon={<ArrowRight size={18} />} disabled={generatingPlan} onClick={handleStartDetox}>
              알고리즘 환기 미션 만들기
            </Button>
          </Card>
        </div>

        <section>
          <SectionTitle title="6개 지표별 차이" description="차이가 큰 항목만 먼저 확인하면 충분합니다." />
          <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Object.keys(metaGap).map((key) => {
              const axis = metaGap[key];
              const gap = Number(axis.gap || 0);
              return (
                <Card key={key} className="p-5">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-base font-black text-slate-950">{axis.name || key}</h3>
                    <span className={["rounded-full px-2.5 py-1 text-[10px] font-black", gap >= 0 ? "bg-rose-100 text-rose-700" : "bg-teal-100 text-teal-700"].join(" ")}>
                      {gap >= 0 ? `+${gap}` : gap}점
                    </span>
                  </div>
                  <div className="mt-4 space-y-2 text-sm font-semibold text-slate-600">
                    <p>자가진단: {Math.round(Number(axis.survey || 0))}점</p>
                    <p>실제 기록: {Math.round(Number(axis.actual || 0))}점</p>
                  </div>
                </Card>
              );
            })}
          </div>
        </section>
      </div>
    </PageShell>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={
      <PageShell active="dashboard" compact>
        <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
          <div className="mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-950" />
          <p className="font-bold text-slate-600">대시보드를 준비하는 중입니다.</p>
        </div>
      </PageShell>
    }>
      <DashboardContent />
    </Suspense>
  );
}
