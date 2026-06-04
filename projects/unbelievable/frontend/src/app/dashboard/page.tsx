"use client";

import React, { Suspense, useEffect, useMemo, useState } from "react";
import { AlertTriangle, ArrowRight, Clock3, Flame, RefreshCcw, Repeat2, Search, Sparkles } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "../../components/Button";
import Card from "../../components/Card";
import PageShell from "../../components/PageShell";
import RadarChart from "../../components/RadarChart";
import ResultCard from "../../components/ResultCard";
import ScoreCard from "../../components/ScoreCard";
import SectionTitle from "../../components/SectionTitle";
import { getDsaoCharacter } from "../../data/dsaoCharacters";
import { API_BASE_URL, DEFAULT_USER_ID } from "../../utils/apiConfig";
import { loadSelfSurveyResult, SelfSurveyResult } from "../../utils/surveyStorage";

type ApiData = any;
type SearchKeyword = { keyword: string; count: number; category?: string };
type InterestSubcategory = { name?: string; ratio?: number; value?: number; entities?: string[]; raw_items?: string[]; confidence?: string };
type InterestCategory = { category?: string; name?: string; value?: number; ratio?: number; count?: number; subcategories?: InterestSubcategory[] };

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

function shortLabel(value: any, max = 8) {
  const text = String(value || "").trim();
  if (text.length <= max) return text || "미분류";
  return `${text.slice(0, max)}...`;
}

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
        const res = await fetch(`${API_BASE_URL}/api/v1/dashboard/summary?run_id=${runId}&user_id=${DEFAULT_USER_ID}`);
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
      const res = await fetch(`${API_BASE_URL}/api/v1/detox/generate?run_id=${runId}&user_id=${DEFAULT_USER_ID}`, {
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
  const insights = processedData.insights || {};
  const searchKeywords: SearchKeyword[] = Array.isArray(insights.search_keywords) ? insights.search_keywords : [];
  const excludedAdCount = Number(insights.excluded_ad_count || processedData.data_coverage?.excluded_ad_count || 0);
  const searchInterestMap = insights.search_interest_map || {};
  const standardVideoInterestMap = insights.standard_video_interest_map || {};
  const shortsInterestMap = insights.shorts_interest_map || {};
  const interestGapReport = insights.interest_gap_report || {};
  const interestAiSummary = insights.interest_ai_summary || {};
  const interestMismatchScore = Math.round(Number(interestGapReport.interest_mismatch_score || 0));
  const flowCandidates = Array.isArray(interestGapReport.recommendation_flow_candidate_categories)
    ? interestGapReport.recommendation_flow_candidate_categories
    : (Array.isArray(interestGapReport.algorithm_drift_categories) ? interestGapReport.algorithm_drift_categories : []);
  const topFlowCandidate = flowCandidates.length > 0
    ? flowCandidates[0]
    : null;
  const topInterestCategories = (map: any) => {
    const distribution: InterestCategory[] = Array.isArray(map?.category_distribution) ? map.category_distribution : [];
    return distribution.slice(0, 3).map((item) => item.category || item.name).filter(Boolean);
  };
  const renderInterestMindMap = (label: string, map: any, emptyText: string, tone: "search" | "video" | "shorts") => {
    const distribution = Array.isArray(map?.category_distribution) ? map.category_distribution : [];
    const palette = {
      search: { bg: "#effaf2", center: "#177a3a", node: "#45b96a", leaf: "#a4dfb4", line: "#43a464", text: "#ffffff", leafText: "#14532d" },
      video: { bg: "#eef8fb", center: "#0f766e", node: "#22a6a0", leaf: "#a7e6df", line: "#148f86", text: "#ffffff", leafText: "#134e4a" },
      shorts: { bg: "#fff1f2", center: "#be123c", node: "#fb7185", leaf: "#fecdd3", line: "#e11d48", text: "#ffffff", leafText: "#881337" }
    }[tone];
    const center = { x: 450, y: 250 };
    const positions = [
      { x: 450, y: 86 },
      { x: 690, y: 145 },
      { x: 700, y: 355 },
      { x: 450, y: 420 },
      { x: 200, y: 355 },
      { x: 210, y: 145 }
    ];

    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-4">
        <div className="mb-3 flex items-center justify-between gap-3">
          <p className="text-sm font-black text-slate-950">{label}</p>
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-black text-slate-500">
            {distribution.length > 0 ? `${distribution.length}개 대분류` : "데이터 없음"}
          </span>
        </div>
        {distribution.length > 0 ? (
          <div className="overflow-x-auto rounded-2xl" style={{ backgroundColor: palette.bg }}>
            <svg viewBox="0 0 900 500" role="img" aria-label={`${label} 마인드맵`} className="min-w-[760px]">
              <rect width="900" height="500" fill={palette.bg} />
              <circle cx="84" cy="250" r="12" fill={palette.leaf} opacity="0.45" />
              <circle cx="816" cy="250" r="12" fill={palette.leaf} opacity="0.45" />
              {distribution.slice(0, 6).map((category: InterestCategory, index: number) => {
                const position = positions[index];
                const name = category.category || category.name || "미분류";
                const ratio = Math.round(Number(category.ratio ?? category.value ?? 0));
                const radius = Math.max(46, Math.min(74, 46 + ratio * 0.55));
                const dx = position.x - center.x;
                const dy = position.y - center.y;
                const length = Math.max(1, Math.sqrt(dx * dx + dy * dy));
                const ux = dx / length;
                const uy = dy / length;
                const px = -uy;
                const py = ux;
                const subs = Array.isArray(category.subcategories) ? category.subcategories.slice(0, 3) : [];
                return (
                  <g key={`${name}-${index}`}>
                    <line x1={center.x} y1={center.y} x2={position.x} y2={position.y} stroke={palette.line} strokeWidth="3" opacity="0.72" />
                    {subs.map((sub: InterestSubcategory, subIndex: number) => {
                      const spread = (subIndex - (subs.length - 1) / 2) * 70;
                      const leafX = position.x + ux * 92 + px * spread;
                      const leafY = position.y + uy * 92 + py * spread;
                      return (
                        <g key={`${name}-${sub.name}-${subIndex}`}>
                          <line x1={position.x} y1={position.y} x2={leafX} y2={leafY} stroke={palette.line} strokeWidth="2" opacity="0.55" />
                          <ellipse cx={leafX} cy={leafY} rx="52" ry="25" fill={palette.leaf} stroke={palette.line} strokeWidth="1.4" />
                          <text x={leafX} y={leafY - 2} textAnchor="middle" fontSize="15" fontWeight="800" fill={palette.leafText}>{shortLabel(sub.name, 7)}</text>
                          <text x={leafX} y={leafY + 15} textAnchor="middle" fontSize="10" fontWeight="700" fill={palette.leafText} opacity="0.72">{sub.confidence || "low"}</text>
                        </g>
                      );
                    })}
                    <circle cx={position.x} cy={position.y} r={radius} fill={palette.node} stroke={palette.line} strokeWidth="2" />
                    <text x={position.x} y={position.y - 5} textAnchor="middle" fontSize="20" fontWeight="900" fill={palette.text}>{shortLabel(name, 7)}</text>
                    <text x={position.x} y={position.y + 18} textAnchor="middle" fontSize="13" fontWeight="800" fill={palette.text} opacity="0.9">{ratio}%</text>
                  </g>
                );
              })}
              <circle cx={center.x} cy={center.y} r="82" fill={palette.center} />
              <text x={center.x} y={center.y - 6} textAnchor="middle" fontSize="28" fontWeight="900" fill="white">{label.replace(" 맵", "")}</text>
              <text x={center.x} y={center.y + 24} textAnchor="middle" fontSize="14" fontWeight="700" fill="white" opacity="0.82">Interest Map</text>
            </svg>
          </div>
        ) : (
          <div className="rounded-2xl px-4 py-10 text-center" style={{ backgroundColor: palette.bg }}>
            <div className="mx-auto flex h-28 w-28 items-center justify-center rounded-full text-center text-sm font-black text-white" style={{ backgroundColor: palette.center }}>
              데이터 부족
            </div>
            <p className="mt-4 text-sm font-bold text-slate-500">{emptyText}</p>
          </div>
        )}
      </div>
    );
  };
  const reportInsights: string[] = Array.isArray(insights.report_insights) ? insights.report_insights : [];
  const directInterestSummary = insights.direct_interest_summary || "검색 기록 부족";
  const recommendationFlowSummary = insights.recommendation_flow_summary || insights.algorithm_interest_summary || "분류 데이터 부족";
  const diversity = Math.round(Number(metaGap.TDS?.actual || 0));
  const misconceptionIndex = Math.round(Number(processedData.misconception?.index || 0));
  const shortsAnalysis = insights.shorts_analysis || {};
  const shortsCount = Number(shortsAnalysis.shorts_count || 0);
  const shortsRisk = Math.round(Number(processedData.shorts_stimulation_risk ?? shortsAnalysis.shorts_stimulation_risk ?? 0));
  const finalDetoxRisk = Math.round(Number(processedData.final_detox_risk ?? riskScore));
  const timeBucketLabels: Record<string, string> = {
    dawn: "새벽",
    morning: "오전",
    afternoon: "오후",
    night: "밤",
    unknown: "불명"
  };

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
            title="손석환님의 미디어 성향 리포트입니다"
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

        <div className="grid gap-4 md:grid-cols-5">
          <ScoreCard label="관심사 쏠림" value={`${riskScore}점`} caption={`${getRiskLabel(riskScore)} 단계`} tone="bg-rose-500 text-white" />
          <ScoreCard label="생각과 기록 차이" value={`${misconceptionIndex}점`} caption={processedData.misconception?.worst_axis_name || "메타인지 갭"} tone="bg-amber-500 text-white" />
          <ScoreCard label="관심사 다양성" value={`${diversity}점`} caption="시청 기록 기준" tone="bg-sky-500 text-white" />
          <ScoreCard label="사용자 주도성" value={`${userAgency}%`} caption="직접 탐색 비중" tone="bg-teal-600 text-white" />
          <ScoreCard label="최종 디톡스 위험" value={`${finalDetoxRisk}점`} caption="정보 편향+숏츠 루프" tone="bg-slate-900 text-white" />
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

        <Card className="p-6 md:p-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.18em] text-rose-700">shorts analysis</p>
              <h2 className="mt-2 text-2xl font-black text-slate-950">숏츠 자극 소비 루프</h2>
              <p className="mt-2 max-w-2xl text-sm font-semibold leading-6 text-slate-600">
                숏츠는 일반 관심사 영향 점수에 직접 섞지 않고, 짧은 영상의 연속 소비와 반복 주제 신호로 별도 해석합니다.
              </p>
            </div>
            <div className="rounded-2xl bg-rose-50 px-4 py-3 text-right">
              <p className="text-[10px] font-black uppercase tracking-[0.16em] text-rose-500">stimulation risk</p>
              <p className="mt-1 text-3xl font-black text-rose-700">{shortsRisk}점</p>
            </div>
          </div>

          {shortsCount > 0 ? (
            <>
              <div className="mt-6 grid gap-3 md:grid-cols-5">
                <div className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
                  <div className="flex items-center gap-2 text-rose-700">
                    <Flame size={18} />
                    <span className="text-xs font-black">루프 지표</span>
                  </div>
                  <p className="mt-3 text-2xl font-black text-slate-950">{Math.round(Number(shortsAnalysis.dopamine_loop_score || 0))}점</p>
                  <p className="mt-1 text-xs font-bold text-slate-500">
                    최대 {shortsAnalysis.max_loop_length || 0}개 연속 · 의미 루프 {shortsAnalysis.meaningful_loop_count || 0}개
                  </p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
                  <div className="flex items-center gap-2 text-indigo-700">
                    <Sparkles size={18} />
                    <span className="text-xs font-black">수동 소비 추정</span>
                  </div>
                  <p className="mt-3 text-2xl font-black text-slate-950">{Math.round(Number(shortsAnalysis.passive_feed_score || 0))}점</p>
                  <p className="mt-1 text-xs font-bold text-slate-500">
                    {shortsAnalysis.passive_feed_level || "low"} · 검색 {shortsAnalysis.active_search_count || 0}건 참고
                  </p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
                  <div className="flex items-center gap-2 text-amber-700">
                    <Repeat2 size={18} />
                    <span className="text-xs font-black">반복 스크롤</span>
                  </div>
                  <p className="mt-3 text-2xl font-black text-slate-950">{Math.round(Number(shortsAnalysis.repeated_topic_score || 0))}점</p>
                  <p className="mt-1 text-xs font-bold text-slate-500">
                    {shortsAnalysis.scroll_repetition_level || "low"} · 반복 키워드 {shortsAnalysis.repeated_keyword_count || 0}개
                  </p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
                  <div className="flex items-center gap-2 text-sky-700">
                    <Clock3 size={18} />
                    <span className="text-xs font-black">시간대 집중</span>
                  </div>
                  <p className="mt-3 text-2xl font-black text-slate-950">{Math.round(Number(shortsAnalysis.time_concentration_score || 0))}점</p>
                  <p className="mt-1 text-xs font-bold text-slate-500">
                    피크 {timeBucketLabels[shortsAnalysis.peak_shorts_time_bucket] || shortsAnalysis.peak_shorts_time_bucket || "불명"} · 심야 {shortsAnalysis.late_night_shorts_ratio || 0}%
                  </p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
                  <p className="text-xs font-black text-slate-500">숏츠 비중</p>
                  <p className="mt-3 text-2xl font-black text-slate-950">{shortsCount}개</p>
                  <p className="mt-1 text-xs font-bold text-slate-500">
                    전체 시청 대비 {Number(shortsAnalysis.shorts_ratio_percent ?? (shortsAnalysis.shorts_ratio || 0) * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              <div className="mt-5 grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
                <div className="rounded-2xl border border-slate-200 bg-white p-4">
                  <p className="text-sm font-black text-slate-950">숏츠 반복 키워드</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {Array.isArray(shortsAnalysis.top_shorts_keywords) && shortsAnalysis.top_shorts_keywords.length > 0 ? (
                      shortsAnalysis.top_shorts_keywords.map((item: any) => (
                        <span key={`${item.keyword}-${item.count}`} className="rounded-full bg-rose-50 px-3 py-1.5 text-xs font-black text-rose-700">
                          {item.keyword} {item.count}회
                        </span>
                      ))
                    ) : (
                      <span className="text-sm font-bold text-slate-500">반복 키워드가 충분하지 않습니다.</span>
                    )}
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-white p-4">
                  <p className="text-sm font-black text-slate-950">시간대별 숏츠</p>
                  <div className="mt-3 grid grid-cols-4 gap-2">
                    {Object.entries(shortsAnalysis.shorts_by_time_bucket || {}).map(([bucket, count]) => (
                      <div key={bucket} className="rounded-xl bg-[#fbfaf7] px-3 py-2 text-center">
                        <p className="text-[10px] font-black text-slate-400">{timeBucketLabels[bucket] || bucket}</p>
                        <p className="mt-1 text-lg font-black text-slate-900">{Number(count || 0)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {Array.isArray(shortsAnalysis.warnings) && shortsAnalysis.warnings.length > 0 && (
                <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3">
                  <p className="text-xs font-black uppercase tracking-[0.16em] text-amber-700">analysis notes</p>
                  <div className="mt-2 space-y-1">
                    {shortsAnalysis.warnings.slice(0, 3).map((warning: string) => (
                      <p key={warning} className="text-xs font-bold leading-5 text-amber-800">{warning}</p>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="mt-6 rounded-2xl border border-dashed border-slate-200 bg-[#fbfaf7] px-4 py-6 text-sm font-bold leading-6 text-slate-500">
              {shortsAnalysis.shorts_detection_note || "이번 업로드에서 /shorts/ URL로 식별된 숏츠 이벤트가 0건입니다. 실제 숏츠 소비가 없다는 확정은 아니며, Takeout 저장 방식 또는 이전 run_id 여부를 확인해야 합니다."}
              <span className="mt-2 block text-xs text-slate-400">일반 영상, 검색, 구독 정보 분석은 그대로 유지됩니다.</span>
            </div>
          )}
        </Card>

        <Card className="p-6 md:p-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-700">interest comparison</p>
              <h2 className="mt-2 text-2xl font-black text-slate-950">관심사 비교 리포트</h2>
              <p className="mt-2 max-w-2xl text-sm font-semibold leading-6 text-slate-600">
                Google Takeout만으로 추천 경로를 100% 확정할 수 없기 때문에, 검색 기록 대비 실제 시청에서 더 많이 나타난 주제를 후보로만 표시합니다.
              </p>
              {excludedAdCount > 0 && (
                <p className="mt-2 text-xs font-black text-teal-700">
                  Google 광고 및 프로모션성 Takeout 항목 {excludedAdCount}개는 분석에서 제외되었습니다.
                </p>
              )}
            </div>
            <div className="rounded-2xl bg-teal-50 px-4 py-3 text-right">
              <p className="text-[10px] font-black uppercase tracking-[0.16em] text-teal-600">mismatch</p>
              <p className="mt-1 text-3xl font-black text-teal-800">{interestMismatchScore}점</p>
            </div>
          </div>
          <div className="mt-6 grid gap-3 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
              <p className="text-xs font-black uppercase tracking-[0.14em] text-slate-400">직접 검색 관심 TOP 3</p>
              <p className="mt-2 text-lg font-black leading-7 text-slate-950">
                {topInterestCategories(searchInterestMap).join(" · ") || "데이터 부족"}
              </p>
              <p className="mt-1 text-xs font-bold text-slate-500">사용자가 직접 입력한 검색어만 반영합니다.</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
              <p className="text-xs font-black uppercase tracking-[0.14em] text-slate-400">실제 시청 관심 TOP 3</p>
              <p className="mt-2 text-lg font-black leading-7 text-slate-950">
                {topInterestCategories(standardVideoInterestMap).join(" · ") || "데이터 부족"}
              </p>
              <p className="mt-1 text-xs font-bold text-slate-500">실제로 시청한 일반 영상 기반 관심사입니다.</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
              <p className="text-xs font-black uppercase tracking-[0.14em] text-slate-400">숏츠 반복 관심 TOP 3</p>
              <p className="mt-2 text-lg font-black leading-7 text-slate-950">
                {topInterestCategories(shortsInterestMap).join(" · ") || "데이터 부족"}
              </p>
              <p className="mt-1 text-xs font-bold text-slate-500">직접 검색 의도가 아니라 짧은 영상 반복 노출 패턴입니다.</p>
            </div>
          </div>
          {topFlowCandidate && (
            <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-bold leading-6 text-amber-800">
              <p className="font-black">추천 흐름 영향 후보</p>
              <p className="mt-1">
                {topFlowCandidate.category}는 검색 기록 대비 실제 시청에서 더 많이 나타난 주제입니다. 후보 점수는 {Math.round(Number(topFlowCandidate.candidate_score || 0))}점입니다.
              </p>
            </div>
          )}
          <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm font-black text-slate-950">AI 해석 요약</p>
              <span className="w-fit rounded-full bg-slate-100 px-3 py-1 text-[10px] font-black uppercase tracking-[0.12em] text-slate-500">
                {interestAiSummary.mode === "gemini" ? "gemini" : "rule based"}
              </span>
            </div>
            <p className="mt-3 text-sm font-bold leading-6 text-slate-700">
              {interestAiSummary.summary || "관심사 해석 데이터가 부족합니다."}
            </p>
            <div className="mt-3 grid gap-2 md:grid-cols-3">
              <p className="rounded-2xl bg-[#fbfaf7] px-3 py-2 text-xs font-bold leading-5 text-slate-600">
                {interestAiSummary.search_intent_read || "검색 의도 데이터가 부족합니다."}
              </p>
              <p className="rounded-2xl bg-[#fbfaf7] px-3 py-2 text-xs font-bold leading-5 text-slate-600">
                {interestAiSummary.watch_exposure_read || "일반 영상 노출 데이터가 부족합니다."}
              </p>
              <p className="rounded-2xl bg-[#fbfaf7] px-3 py-2 text-xs font-bold leading-5 text-slate-600">
                {interestAiSummary.shorts_read || "숏츠 데이터가 부족합니다."}
              </p>
            </div>
            <p className="mt-3 rounded-2xl bg-teal-50 px-3 py-2 text-xs font-black leading-5 text-teal-800">
              {interestAiSummary.next_action_hint || "다음 시청 전 검색어를 먼저 정해 추천 흐름을 끊어보세요."}
            </p>
          </div>
          <div className="mt-4 grid gap-4">
            {renderInterestMindMap("검색 기반 맵", searchInterestMap, "검색어로 인정 가능한 데이터가 부족합니다.", "search")}
            {renderInterestMindMap("일반 시청 기반 맵", standardVideoInterestMap, "일반 영상 데이터가 부족합니다.", "video")}
            {renderInterestMindMap("숏츠 반복 맵", shortsInterestMap, shortsInterestMap.shorts_detection_note || "숏츠 데이터는 /shorts/ URL 기준으로만 확인됩니다.", "shorts")}
          </div>
        </Card>

        <div className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <RadarChart data={chartData} scoreWarnings={scoreWarnings} />

          <div className="space-y-4">
            {renderInterestMindMap("검색어 관심사 맵", searchInterestMap, "검색어로 인정 가능한 데이터가 부족합니다.", "search")}
            <Card className="p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-black uppercase tracking-[0.16em] text-teal-700">search evidence</p>
                  <h3 className="mt-1 text-lg font-black text-slate-950">실제 검색어 근거</h3>
                </div>
                {excludedAdCount > 0 && (
                  <span className="rounded-full bg-teal-50 px-3 py-1 text-[11px] font-black text-teal-700">
                    광고 {excludedAdCount}건 제외
                  </span>
                )}
              </div>
              <div className="mt-4 grid gap-2 sm:grid-cols-2">
                {searchKeywords.length > 0 ? (
                  searchKeywords.slice(0, 8).map((item, index) => (
                    <div key={item.keyword} className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-[#fbfaf7] px-3 py-2">
                      <span className="text-[11px] font-black text-slate-400">{index + 1}</span>
                      <span className="min-w-0 flex-1 truncate text-xs font-black text-slate-800">{item.keyword}</span>
                      <span className="text-[11px] font-bold text-slate-500">{item.count}회</span>
                    </div>
                  ))
                ) : (
                  <div className="rounded-2xl border border-dashed border-slate-200 bg-[#fbfaf7] px-4 py-5 text-sm font-bold text-slate-500">
                    검색 기록이 부족해 키워드 근거를 표시하지 못했습니다.
                  </div>
                )}
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 bg-white p-4">
                  <p className="text-xs font-black uppercase tracking-[0.16em] text-slate-400">내가 직접 찾은 관심사</p>
                  <p className="mt-3 text-sm font-bold leading-6 text-slate-700">{directInterestSummary}</p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-white p-4">
                  <p className="text-xs font-black uppercase tracking-[0.16em] text-slate-400">추천 흐름 영향 후보</p>
                  <p className="mt-3 text-sm font-bold leading-6 text-slate-700">{recommendationFlowSummary}</p>
                </div>
              </div>
              <p className="mt-4 text-xs font-semibold leading-5 text-slate-500">
                분석 데이터는 결과 생성 목적 외에는 사용하지 않아요.
              </p>
            </Card>
          </div>
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
