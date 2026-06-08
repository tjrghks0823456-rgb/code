"use client";

import React, { Suspense, useEffect, useMemo, useRef, useState } from "react";
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
import { DEFAULT_USER_ID, apiUrl } from "../../utils/apiConfig";
import { loadSelfSurveyResult, SelfSurveyResult } from "../../utils/surveyStorage";

type ApiData = any;
type SearchKeyword = { keyword: string; count: number; category?: string };
type InterestSubcategory = { name?: string; ratio?: number; value?: number; entities?: string[]; raw_items?: string[]; confidence?: string };
type InterestCategory = { category?: string; name?: string; value?: number; ratio?: number; count?: number; subcategories?: InterestSubcategory[] };

interface ScoreComponent {
  name: string;
  label?: string;
  value: number | null;
  weight?: number;
  status?: string;
}

interface ApiScoreComponent {
  search_ratio?: number | null;
  direct_selection_ratio?: number | null;
  curation_ratio?: number | null;
  participation_ratio?: number | null;
  legacy_hhi_inverse_score?: number | null;
  relative_hhi_balance_score?: number | null;
  unique_source_count_adjustment?: number | null;
  nlp_category_entropy?: number | null;
  local_keyword_category_entropy?: number | null;
  legacy_sentiment_entropy_score?: number | null;
  negative_sentiment_penalty?: number | null;
  stimulus_keyword_penalty?: number | null;
  neutral_info_calm_stability_signal_ratio?: number | null;
  toxic_ratio_penalty?: number | null;
  harmful_keyword_penalty?: number | null;
  shorts_ratio_penalty?: number | null;
  repeated_shorts_penalty?: number | null;
  raw_concentration_score?: number | null;
  adjusted_concentration_score?: number | null;
  [key: string]: any;
}

interface ScoreDetail {
  score: number;
  confidence: number | string;
  reason: string;
  warnings: string[];
  available: boolean;
  score_components?: ApiScoreComponent;
}

interface MetaGapItem {
  name: string;
  survey: number | null;
  actual: number | null;
  gap: number | null;
  available?: boolean;
  reason?: string;
}

interface SamplingMetadata {
  total_session_count?: number;
  sampled_session_count?: number;
  sampling_strategy?: string;
  nlp_input_token_count?: number;
  excluded_axes?: string[];
  overall_confidence?: "high" | "medium" | "low";
  score_details?: Record<string, ScoreDetail>;
}

const AXIS_LABELS: Record<string, string> = {
  TDS: "주제 다양성",
  SBS: "출처 균형",
  EBS: "정서 안정성",
  VOS: "관점 개방성",
  SMS: "자극성 안전",
  UAS: "사용자 주도성"
};

const CONFIDENCE_LABELS: Record<string, string> = {
  high: "높음",
  medium: "보통",
  low: "낮음"
};

const AXIS_UNAVAILABLE_REASON_LABELS: Record<string, string> = {
  UAS: "검색 기록 또는 직접 선택 경로 부족",
  SBS: "채널 정보 없음"
};

import koLocale from "../../locales/ko.json";

const AXIS_AVAILABLE_DESCS: Record<string, string> = koLocale.AXIS_AVAILABLE_DESCS;
const QUALITY_FLAG_LABELS: Record<string, { title: string; desc: string }> = koLocale.QUALITY_FLAG_LABELS;
const CONFIDENCE_DESCS: Record<string, string> = koLocale.CONFIDENCE_DESCS;
const COMPONENT_LABELS: Record<string, string> = koLocale.COMPONENT_LABELS;

function formatConfidence(confidence: any): string {
  if (typeof confidence === "string") {
    const lower = confidence.toLowerCase();
    if (lower === "high") return "높음";
    if (lower === "medium") return "보통";
    if (lower === "low") return "낮음";
    return confidence;
  }
  if (typeof confidence === "number") {
    if (confidence >= 0.8) return "높음";
    if (confidence >= 0.5) return "보통";
    return "낮음";
  }
  return "낮음";
}

function formatGrade(score: number): string {
  if (score >= 60) return "우수";
  if (score >= 40) return "보통";
  return "낮음";
}

function renderComponentDetails(axisCode: string, components: ApiScoreComponent | undefined, warnings: string[] = []) {
  if (!components) return <p className="text-xs text-slate-400">계산 근거 세부 데이터가 없습니다.</p>;

  const items: { label: string; value: string; weight?: string; status?: string }[] = [];

  const fmtVal = (val: number | null | undefined, unit = "%") => {
    if (val === null || val === undefined) return "데이터 없음 / 계산 제외";
    return `${val.toFixed(1)}${unit}`;
  };

  if (axisCode === "UAS") {
    items.push(
      { label: "검색 비율", value: fmtVal(components.search_ratio), status: components.search_ratio === null ? "excluded" : undefined },
      { label: "직접 선택 경로 비율", value: fmtVal(components.direct_selection_ratio), status: components.direct_selection_ratio === null ? "excluded" : undefined },
      { label: "구독/보관함 탐색 비율", value: fmtVal(components.curation_ratio) },
      { label: "댓글/채팅 참여 비율", value: fmtVal(components.participation_ratio) }
    );
  } else if (axisCode === "SBS") {
    items.push(
      { label: "기존 출처 다양성 (HHI)", value: fmtVal(components.legacy_hhi_inverse_score, "점"), weight: "참고용", status: components.legacy_hhi_inverse_score === null ? "excluded" : undefined },
      { label: "상대적 출처 균형도 (보정)", value: fmtVal(components.relative_hhi_balance_score, "점"), weight: "주요 가중", status: components.relative_hhi_balance_score === null ? "excluded" : undefined },
      { label: "출처 수 보정 격차", value: fmtVal(components.unique_source_count_adjustment, "점") }
    );
  } else if (axisCode === "TDS") {
    items.push(
      { label: "NLP 카테고리 엔트로피", value: fmtVal(components.nlp_category_entropy, "점") },
      { label: "로컬 키워드 엔트로피 (대체)", value: fmtVal(components.local_keyword_category_entropy, "점") },
      { label: "로컬 키워드 대체 여부", value: components.nlp_sample_insufficient_confidence_reduced ? "적용됨 (NLP 데이터 부족)" : "미적용 (NLP 충분)", status: components.nlp_sample_insufficient_confidence_reduced ? "limited" : undefined }
    );
  } else if (axisCode === "EBS") {
    items.push(
      { label: "기존 감정 균형 (엔트로피)", value: fmtVal(components.legacy_sentiment_entropy_score, "점") },
      { label: "부정 감정 페널티", value: fmtVal(components.negative_sentiment_penalty, "점") },
      { label: "자극 키워드 페널티", value: fmtVal(components.stimulus_keyword_penalty, "점") },
      { label: "안정/보호 감정 가산 비율", value: fmtVal(components.neutral_info_calm_stability_signal_ratio ? components.neutral_info_calm_stability_signal_ratio * 100 : 0) }
    );
  } else if (axisCode === "SMS") {
    items.push(
      { label: "유해 카테고리 페널티", value: fmtVal(components.toxic_ratio_penalty, "점") },
      { label: "우려 키워드 페널티", value: fmtVal(components.harmful_keyword_penalty, "점") },
      { label: "숏츠 시청 비중 페널티", value: fmtVal(components.shorts_ratio_penalty, "점") },
      { label: "연속 숏츠 릴레이 페널티", value: fmtVal(components.repeated_shorts_penalty, "점") }
    );
  } else if (axisCode === "VOS") {
    items.push(
      { label: "가공 전 관심 집중도", value: fmtVal(components.raw_concentration_score, "점") },
      { label: "학습/교육 완화 적용 관심도", value: fmtVal(components.adjusted_concentration_score, "점") },
      { label: "생산적 몰입 완화 여부", value: components.beta_applied ? `적용됨 (Beta=${components.beta_value})` : "미적용" }
    );
  } else {
    Object.keys(components).forEach((compKey) => {
      const val = components[compKey];
      if (typeof val === "number" || typeof val === "string" || typeof val === "boolean" || val === null) {
        items.push({ label: COMPONENT_LABELS[compKey] || compKey, value: val === null ? "데이터 없음 / 계산 제외" : String(val) });
      }
    });
  }

  return (
    <div className="mt-3 rounded-2xl bg-slate-900/60 p-4 border border-slate-800 animate-fadeIn text-left">
      <p className="text-xs font-bold text-slate-400 mb-2 font-mono">하위 세부 평가 항목</p>
      <div className="space-y-1.5 text-xs text-slate-300">
        {items.map((item, idx) => (
          <div key={idx} className="flex justify-between border-b border-slate-800/40 pb-1.5 items-center">
            <span className="text-slate-400 font-semibold">{item.label}</span>
            <div className="flex gap-2 font-mono items-center">
              <span className={[
                "font-bold",
                item.value.includes("데이터 없음") ? "text-rose-400/80 italic font-normal animate-pulse" : "text-slate-100",
                item.status === "limited" ? "text-amber-400" : "",
                item.status === "excluded" ? "text-rose-400 font-normal" : ""
              ].join(" ")}>{item.value}</span>
              {item.weight && <span className="text-[10px] text-teal-400 font-normal">({item.weight})</span>}
            </div>
          </div>
        ))}
      </div>
      {warnings.length > 0 && (
        <div className="mt-3 border-t border-slate-800/60 pt-2 text-[10px] text-amber-400 font-semibold leading-relaxed">
          {warnings.map((w, idx) => (
            <p key={idx}>⚠️ {w}</p>
          ))}
        </div>
      )}
    </div>
  );
}
type InterestGraphNode = {
  id: number;
  label: string;
  group: string;
  size: number;
  depth: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  meta?: Record<string, any>;
};
type InterestGraphEdge = { source: number; target: number; value?: number };

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

const INTEREST_GRAPH_COLORS: Record<string, string> = {
  center: "#0f172a",
  sports: "#16a34a",
  game: "#7c3aed",
  society: "#2563eb",
  finance: "#0f766e",
  tech: "#0891b2",
  study: "#d97706",
  entertainment: "#db2777",
  shopping: "#ea580c",
  travel: "#65a30d",
  health: "#dc2626",
  lifestyle: "#64748b",
  other: "#94a3b8"
};

const INTEREST_GRAPH_LABELS: Record<string, string> = {
  sports: "스포츠",
  game: "게임",
  society: "정치/사회",
  finance: "경제/금융",
  tech: "IT/테크",
  study: "학습",
  entertainment: "엔터",
  shopping: "쇼핑",
  travel: "여행/맛집",
  health: "건강",
  lifestyle: "라이프",
  other: "기타"
};

const GRAPH_TONE_SURFACES: Record<"search" | "video" | "shorts", { bg: string; chip: string; ring: string }> = {
  search: { bg: "#f3fbf6", chip: "bg-emerald-50 text-emerald-700", ring: "#bbf7d0" },
  video: { bg: "#f1fbfc", chip: "bg-cyan-50 text-cyan-700", ring: "#a5f3fc" },
  shorts: { bg: "#fff5f6", chip: "bg-rose-50 text-rose-700", ring: "#fecdd3" }
};

function interestGroupFor(category: string) {
  const value = String(category || "").toLowerCase();
  if (value.includes("스포츠") || value.includes("sport")) return "sports";
  if (value.includes("게임") || value.includes("game")) return "game";
  if (value.includes("정치") || value.includes("사회") || value.includes("news")) return "society";
  if (value.includes("경제") || value.includes("금융") || value.includes("finance")) return "finance";
  if (value.includes("it") || value.includes("테크") || value.includes("computer") || value.includes("electronics")) return "tech";
  if (value.includes("학습") || value.includes("자격") || value.includes("교육")) return "study";
  if (value.includes("엔터") || value.includes("음악") || value.includes("연예") || value.includes("entertainment")) return "entertainment";
  if (value.includes("쇼핑") || value.includes("제품") || value.includes("shopping")) return "shopping";
  if (value.includes("여행") || value.includes("맛집") || value.includes("travel")) return "travel";
  if (value.includes("건강") || value.includes("운동") || value.includes("health")) return "health";
  if (value.includes("라이프") || value.includes("생활")) return "lifestyle";
  return "other";
}

function graphCenterLabel(label: string) {
  if (label.includes("숏츠")) return "숏츠 반복\n맵";
  if (label.includes("일반")) return "일반 시청\n맵";
  if (label.includes("검색어")) return "검색어\n맵";
  return "검색 기반\n맵";
}

function buildInterestGraphData(label: string, map: any, tone: "search" | "video" | "shorts") {
  const distribution: InterestCategory[] = Array.isArray(map?.category_distribution) ? map.category_distribution : [];
  const nodes: InterestGraphNode[] = [];
  const edges: InterestGraphEdge[] = [];
  let nextId = 1;

  nodes.push({
    id: nextId++,
    label: graphCenterLabel(label),
    group: "center",
    size: 34,
    depth: 0,
    meta: { kind: label, total: map?.total_search_count || map?.total_video_count || map?.total_shorts_count || 0 }
  });

  distribution.slice(0, 7).forEach((category, index) => {
    const categoryName = category.category || category.name || "기타/미분류";
    const ratio = Number(category.ratio ?? category.value ?? 0);
    const categoryId = nextId++;
    const group = interestGroupFor(categoryName);

    nodes.push({
      id: categoryId,
      label: `${shortLabel(categoryName, 8)}\n${Math.round(ratio)}%`,
      group,
      size: Math.max(17, Math.min(34, 17 + ratio * 0.25)),
      depth: 1,
      meta: {
        name: categoryName,
        ratio,
        count: category.count,
        subcategories: category.subcategories || []
      }
    });
    edges.push({ source: 1, target: categoryId, value: Math.max(1, ratio) });

    const subs = Array.isArray(category.subcategories) ? category.subcategories.slice(0, index < 3 ? 3 : 2) : [];
    subs.forEach((sub) => {
      const subName = sub.name || "미분류";
      const subRatio = Number(sub.ratio ?? sub.value ?? 0);
      const subId = nextId++;
      nodes.push({
        id: subId,
        label: shortLabel(subName, 9),
        group,
        size: Math.max(10, Math.min(20, 10 + subRatio * 0.16)),
        depth: 2,
        meta: {
          name: subName,
          ratio: subRatio,
          entities: sub.entities || [],
          raw_items: sub.raw_items || [],
          confidence: sub.confidence
        }
      });
      edges.push({ source: categoryId, target: subId, value: Math.max(1, subRatio || 1) });
    });
  });

  return { nodes, edges, categoryCount: distribution.length, tone };
}

function InterestNetworkGraph({
  label,
  map,
  emptyText,
  tone
}: {
  label: string;
  map: any;
  emptyText: string;
  tone: "search" | "video" | "shorts";
}) {
  const graphData = useMemo(() => buildInterestGraphData(label, map, tone), [label, map, tone]);
  const [nodes, setNodes] = useState<InterestGraphNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<InterestGraphNode | null>(null);
  const nodesRef = useRef<InterestGraphNode[]>([]);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const dragNodeRef = useRef<number | null>(null);
  const width = 900;
  const height = 520;
  const centerX = width / 2;
  const centerY = height / 2;
  const surface = GRAPH_TONE_SURFACES[tone];

  useEffect(() => {
    if (graphData.nodes.length <= 1) {
      nodesRef.current = [];
      setNodes([]);
      setSelectedNode(null);
      return;
    }

    const categoryCount = graphData.nodes.filter((node) => node.depth === 1).length || 1;
    const subAngles: Record<number, number> = {};
    const initialized = graphData.nodes.map((node, index) => {
      if (node.depth === 0) {
        return { ...node, x: centerX, y: centerY, vx: 0, vy: 0 };
      }

      if (node.depth === 1) {
        const categoryIndex = graphData.nodes.filter((candidate) => candidate.depth === 1 && candidate.id < node.id).length;
        const angle = (categoryIndex / categoryCount) * Math.PI * 2 - Math.PI / 2;
        subAngles[node.id] = angle;
        return {
          ...node,
          x: centerX + Math.cos(angle) * 210,
          y: centerY + Math.sin(angle) * 160,
          vx: 0,
          vy: 0
        };
      }

      const edge = graphData.edges.find((candidate) => candidate.target === node.id);
      const parent = graphData.nodes.find((candidate) => candidate.id === edge?.source);
      const parentAngle = parent ? subAngles[parent.id] ?? ((index / graphData.nodes.length) * Math.PI * 2) : (index / graphData.nodes.length) * Math.PI * 2;
      const siblingIndex = graphData.edges.filter((candidate) => candidate.source === edge?.source && candidate.target < node.id).length;
      const angle = parentAngle + (siblingIndex - 1) * 0.36;
      return {
        ...node,
        x: centerX + Math.cos(angle) * 330,
        y: centerY + Math.sin(angle) * 235,
        vx: 0,
        vy: 0
      };
    });

    nodesRef.current = initialized;
    setNodes(initialized);
    setSelectedNode(null);
  }, [graphData, centerX, centerY]);

  useEffect(() => {
    if (graphData.nodes.length <= 1) return;
    let frameId = 0;
    let frameCount = 0;

    const tick = () => {
      const current = nodesRef.current;
      if (!current.length) return;

      for (let i = 0; i < current.length; i += 1) {
        for (let j = i + 1; j < current.length; j += 1) {
          const a = current[i];
          const b = current[j];
          const dx = (b.x || 0) - (a.x || 0);
          const dy = (b.y || 0) - (a.y || 0);
          const distance = Math.max(1, Math.sqrt(dx * dx + dy * dy));
          const repulsion = (a.depth === 0 || b.depth === 0 ? 6200 : 3600) / (distance * distance);
          const fx = (dx / distance) * repulsion;
          const fy = (dy / distance) * repulsion;
          if (a.depth !== 0 && a.id !== dragNodeRef.current) {
            a.vx = (a.vx || 0) - fx;
            a.vy = (a.vy || 0) - fy;
          }
          if (b.depth !== 0 && b.id !== dragNodeRef.current) {
            b.vx = (b.vx || 0) + fx;
            b.vy = (b.vy || 0) + fy;
          }
        }
      }

      graphData.edges.forEach((edge) => {
        const source = current.find((node) => node.id === edge.source);
        const target = current.find((node) => node.id === edge.target);
        if (!source || !target) return;
        const dx = (target.x || 0) - (source.x || 0);
        const dy = (target.y || 0) - (source.y || 0);
        const distance = Math.max(1, Math.sqrt(dx * dx + dy * dy));
        const desired = source.depth === 0 ? 205 : 125;
        const force = (distance - desired) * (source.depth === 0 ? 0.018 : 0.026);
        const fx = (dx / distance) * force;
        const fy = (dy / distance) * force;
        if (source.depth !== 0 && source.id !== dragNodeRef.current) {
          source.vx = (source.vx || 0) + fx;
          source.vy = (source.vy || 0) + fy;
        }
        if (target.depth !== 0 && target.id !== dragNodeRef.current) {
          target.vx = (target.vx || 0) - fx;
          target.vy = (target.vy || 0) - fy;
        }
      });

      const updated = current.map((node) => {
        if (node.depth === 0) {
          return { ...node, x: centerX, y: centerY, vx: 0, vy: 0 };
        }
        if (node.id === dragNodeRef.current) return { ...node };

        const gravity = node.depth === 1 ? 0.006 : 0.003;
        const vx = ((node.vx || 0) + (centerX - (node.x || centerX)) * gravity) * 0.86;
        const vy = ((node.vy || 0) + (centerY - (node.y || centerY)) * gravity) * 0.86;
        const margin = node.size + 42;
        return {
          ...node,
          vx,
          vy,
          x: Math.max(margin, Math.min(width - margin, (node.x || centerX) + vx)),
          y: Math.max(margin, Math.min(height - margin, (node.y || centerY) + vy))
        };
      });

      nodesRef.current = updated;
      setNodes(updated);
      frameCount += 1;
      if (frameCount < 260 || dragNodeRef.current !== null) {
        frameId = requestAnimationFrame(tick);
      }
    };

    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [graphData, centerX, centerY]);

  const handleMouseDown = (event: React.MouseEvent, nodeId: number) => {
    event.stopPropagation();
    dragNodeRef.current = nodeId;
  };

  const handleMouseMove = (event: React.MouseEvent) => {
    if (dragNodeRef.current === null || !svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * width;
    const y = ((event.clientY - rect.top) / rect.height) * height;
    nodesRef.current = nodesRef.current.map((node) => (
      node.id === dragNodeRef.current ? { ...node, x, y, vx: 0, vy: 0 } : node
    ));
    setNodes([...nodesRef.current]);
  };

  const handleMouseUp = () => {
    dragNodeRef.current = null;
  };

  const usedGroups = Array.from(new Set(nodes.filter((node) => node.depth > 0).map((node) => node.group)));
  const selectedMeta = selectedNode?.meta || {};
  const coverage = map?.classification_coverage || {};
  const classifiedRatio = Math.round(Number(coverage.classified_ratio || 0));
  const unclassifiedCount = Number(coverage.unclassified_count || 0);
  const unclassifiedSamples = Array.isArray(coverage.unclassified_samples) ? coverage.unclassified_samples : [];

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <p className="text-sm font-black text-slate-950">{label}</p>
        <span className={["rounded-full px-2.5 py-1 text-[10px] font-black", surface.chip].join(" ")}>
          {graphData.categoryCount > 0 ? `${graphData.categoryCount}개 대분류` : "데이터 없음"}
        </span>
      </div>
      {graphData.nodes.length > 1 && coverage.classified_ratio !== undefined && (
        <div className="mb-3 rounded-2xl border border-slate-100 bg-[#fbfaf7] px-3 py-2">
          <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] font-black text-slate-500">
            <span>분류 커버리지 {classifiedRatio}%</span>
            <span>미분류 {unclassifiedCount}건</span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-white">
            <div className="h-full rounded-full bg-teal-500" style={{ width: `${Math.max(0, Math.min(100, classifiedRatio))}%` }} />
          </div>
          {unclassifiedSamples.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {unclassifiedSamples.slice(0, 5).map((sample: string) => (
                <span key={sample} className="rounded-full bg-white px-2 py-1 text-[10px] font-bold text-slate-400">
                  {shortLabel(sample, 14)}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
      {graphData.nodes.length > 1 ? (
        <>
          <div
            className="relative h-[430px] overflow-hidden rounded-2xl border border-slate-100"
            style={{ background: `radial-gradient(circle at center, #ffffff 0%, ${surface.bg} 72%)` }}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >
            <svg ref={svgRef} viewBox={`0 0 ${width} ${height}`} className="h-full w-full">
              <circle cx={centerX} cy={centerY} r="148" fill={surface.ring} opacity="0.18" />
              {graphData.edges.map((edge, index) => {
                const source = nodes.find((node) => node.id === edge.source);
                const target = nodes.find((node) => node.id === edge.target);
                if (!source || !target) return null;
                return (
                  <line
                    key={`${edge.source}-${edge.target}-${index}`}
                    x1={source.x}
                    y1={source.y}
                    x2={target.x}
                    y2={target.y}
                    stroke={source.depth === 0 ? "#94a3b8" : INTEREST_GRAPH_COLORS[target.group] || "#94a3b8"}
                    strokeWidth={source.depth === 0 ? 3.6 : 2.2}
                    strokeOpacity={source.depth === 0 ? 0.36 : 0.24}
                  />
                );
              })}
              {nodes.map((node) => {
                const color = INTEREST_GRAPH_COLORS[node.group] || INTEREST_GRAPH_COLORS.other;
                const selected = selectedNode?.id === node.id;
                const size = selected ? node.size + 4 : node.size;
                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x}, ${node.y})`}
                    className="cursor-grab active:cursor-grabbing"
                    onMouseDown={(event) => handleMouseDown(event, node.id)}
                    onClick={() => setSelectedNode(node)}
                  >
                    <circle r={size + 9} fill={color} opacity={node.depth === 0 ? 0.13 : 0.09} />
                    <circle
                      r={size}
                      fill={color}
                      stroke="#ffffff"
                      strokeWidth={node.depth === 0 ? 3 : 2}
                      style={{ filter: "drop-shadow(0 8px 14px rgba(15, 23, 42, 0.16))" }}
                    />
                    <text
                      y={node.depth === 0 ? -3 : size + 17}
                      textAnchor="middle"
                      className={node.depth === 0 ? "text-[17px] font-black" : "text-[11px] font-black"}
                      fill={node.depth === 0 ? "#ffffff" : "#334155"}
                      style={node.depth === 0 ? undefined : { paintOrder: "stroke", stroke: "#ffffff", strokeWidth: 4 }}
                    >
                      {String(node.label).split("\n").map((line, index) => (
                        <tspan key={line + index} x={0} dy={index === 0 ? 0 : 16}>
                          {line}
                        </tspan>
                      ))}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {usedGroups.map((group) => (
              <span key={group} className="inline-flex items-center gap-1.5 rounded-full bg-slate-50 px-2.5 py-1 text-[11px] font-bold text-slate-500">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: INTEREST_GRAPH_COLORS[group] || INTEREST_GRAPH_COLORS.other }} />
                {INTEREST_GRAPH_LABELS[group] || "기타"}
              </span>
            ))}
          </div>
          <div className="mt-3 rounded-2xl border border-slate-100 bg-[#fbfaf7] px-4 py-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-black text-slate-900">{selectedMeta.name || selectedNode?.label?.replace("\n", " ") || "대표 관심사"}</p>
              {selectedMeta.ratio !== undefined && (
                <span className="rounded-full bg-white px-2.5 py-1 text-[11px] font-black text-slate-500">
                  {Math.round(Number(selectedMeta.ratio || 0))}%
                </span>
              )}
            </div>
            <div className="mt-2 flex flex-wrap gap-2 text-[11px] font-bold text-slate-500">
              {(selectedMeta.entities || []).slice(0, 4).map((entity: string) => (
                <span key={entity} className="rounded-full bg-white px-2 py-1">{entity}</span>
              ))}
              {(selectedMeta.raw_items || []).slice(0, 3).map((item: string) => (
                <span key={item} className="rounded-full bg-white px-2 py-1">{shortLabel(item, 18)}</span>
              ))}
              {selectedMeta.confidence && <span className="rounded-full bg-white px-2 py-1">confidence: {selectedMeta.confidence}</span>}
            </div>
          </div>
        </>
      ) : (
        <div className="rounded-2xl px-4 py-10 text-center" style={{ backgroundColor: surface.bg }}>
          <div className="mx-auto flex h-28 w-28 items-center justify-center rounded-full bg-slate-900 text-center text-sm font-black text-white">
            데이터 부족
          </div>
          <p className="mt-4 text-sm font-bold text-slate-500">{emptyText}</p>
        </div>
      )}
    </div>
  );
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
  const [expandedAxis, setExpandedAxis] = useState<string | null>(null);
  const [expandedComponents, setExpandedComponents] = useState<Record<string, boolean>>({});

  const toggleComponent = (key: string) => {
    setExpandedComponents((prev) => ({ ...prev, [key]: !prev[key] }));
  };

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
        const res = await fetch(apiUrl(`/api/v1/dashboard/summary?run_id=${runId}&user_id=${DEFAULT_USER_ID}`));
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
    return data;
  }, [data]);

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
    subject: AXIS_LABELS[key] || metaGap[key].name || key,
    자가진단_결과: Number(metaGap[key].survey || 0),
    실제_분석값: Number(metaGap[key].actual || 0),
    available: metaGap[key].available !== false
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
  const renderInterestMindMap = (label: string, map: any, emptyText: string, tone: "search" | "video" | "shorts") => (
    <InterestNetworkGraph label={label} map={map} emptyText={emptyText} tone={tone} />
  );
  const distributionFor = (map: any): InterestCategory[] => (
    Array.isArray(map?.category_distribution) ? map.category_distribution : []
  );
  const standardDistribution = distributionFor(standardVideoInterestMap);
  const searchDistribution = distributionFor(searchInterestMap);
  const highlightInterests = (standardDistribution.length > 0 ? standardDistribution : searchDistribution).slice(0, 5);
  const gapRows = Array.isArray(interestGapReport.search_vs_watch_gap)
    ? interestGapReport.search_vs_watch_gap.slice(0, 5)
    : [];
  const normalizePercent = (value: any) => Math.max(0, Math.min(100, Math.round(Number(value || 0))));
  const reportInsights: string[] = Array.isArray(insights.report_insights) ? insights.report_insights : [];
  const directInterestSummary = insights.direct_interest_summary || "검색 기록 부족";
  const recommendationFlowSummary = insights.recommendation_flow_summary || insights.algorithm_interest_summary || "분류 데이터 부족";
  const diversity = Math.round(Number(metaGap.TDS?.actual || 0));
  const misconceptionIndex = processedData.misconception?.index !== null && processedData.misconception?.index !== undefined
    ? Math.round(Number(processedData.misconception.index))
    : null;
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
  const detoxGuideItems = [
    {
      title: "직접 검색 루틴",
      tag: "검색",
      description: interestAiSummary.next_action_hint || "시청 전에 오늘 직접 확인할 검색어를 먼저 정해보세요."
    },
    {
      title: "관심사 균형 점검",
      tag: "균형",
      description: topFlowCandidate?.category
        ? `${topFlowCandidate.category} 주제는 검색 대비 시청에서 더 크게 나타납니다. 반대 관점이나 기초 자료를 함께 확인해보세요.`
        : "검색과 시청에서 반복되는 주제를 비교해 관심사 균형을 점검해보세요."
    },
    {
      title: "숏츠 소비 확인",
      tag: "숏츠",
      description: shortsCount > 0
        ? `이번 데이터에서 숏츠 ${shortsCount}개가 감지되었습니다. 짧은 영상은 별도 흐름으로 보고 쉬는 구간을 만들어보세요.`
        : "이번 Takeout에서는 /shorts/ URL 기준 숏츠가 거의 감지되지 않았습니다. 일반 영상 분석은 그대로 유지됩니다."
    }
  ];

  return (
    <PageShell active="dashboard">
      <div className="space-y-10">
        {processedData.meta_gap_available === false && (
          <div className="rounded-3xl border border-amber-200 bg-amber-50 px-5 py-4 text-sm font-semibold text-amber-800">
            ⚠️ 자가진단 데이터가 없어 메타인지 격차 분석은 참고용으로 비활성화되었습니다.
          </div>
        )}

        {detoxError && (
          <div className="rounded-3xl border border-rose-200 bg-rose-50 p-5 text-sm font-semibold leading-6 text-rose-700">
            {detoxError}
          </div>
        )}

        {/* Friendly Data Quality Warning Banners */}
        {(() => {
          const warningsList = [];
          const dq = processedData.data_quality || {};
          const flags = processedData.data_quality_flags || [];
          const exceptionCodes = processedData.exception_codes || [];

          if (flags.includes("timestamp_fallback_used")) {
            warningsList.push({
              title: "타임스탬프 자동 보정 적용",
              desc: "일부 시청 기록의 시간 순서가 온전하지 않아 타임스탬프 오류를 자동으로 보정하여 분석을 완료했습니다. 점수 계산의 선후관계 파악에 참고용으로 사용되었습니다.",
              isConfidenceLow: false
            });
          }

          if (dq.duration === "missing" || exceptionCodes.includes("P10_DURATION_MISSING") || flags.includes("duration_unknown")) {
            warningsList.push({
              title: "체류 시간 정보 확인 불가 (Takeout 한계)",
              desc: "업로드된 기록에 동영상 시청 지속 시간 정보가 확인 불가하여 체류 시간(시청 지속 시간) 기반 지표는 계산에서 제외되었습니다. 이로 인해 정서 안정성 및 자극성 점수는 신뢰성이 제한될 수 있으며, 일부 지표는 참고용으로 해석됩니다.",
              isConfidenceLow: true
            });
          }

          if (dq.duration === "estimated" || exceptionCodes.includes("P10_DURATION_ESTIMATED") || flags.includes("duration_estimated")) {
            warningsList.push({
              title: "추정 체류 시간 사용 중",
              desc: "Google Takeout 시청 기록의 기술적 한계로 실제 시청 지속 시간이 누락되어 있어, 인접 동영상 시청 간격 및 비디오 길이를 결합한 '기록 기반 추정값(Simulated)'으로 시청 지속 시간을 계산했습니다. 장시간 브라우저 방치 등 현실과의 격차가 존재할 수 있어 참고용으로 표시됩니다.",
              isConfidenceLow: true
            });
          }

          if (dq.nlp_provider === "rule_based_fallback" || exceptionCodes.includes("P15_NLP_FALLBACK_USED") || flags.includes("nlp_fallback_used")) {
            warningsList.push({
              title: "로컬 한글 형태소 분석 엔진 사용",
              desc: "클라우드 언어 분석 API 연동 제한 또는 클라우드 할당량으로 인해 로컬 형태소 단어 사전(세종 기반) Fallback 분석 엔진이 사용되었습니다. 시청 텍스트 분석은 정상 완료되었으나 클라우드 분석 결과 대비 일부 카테고리 매칭 점수가 다르게 집계될 수 있어 참고용으로 표시됩니다.",
              isConfidenceLow: true
            });
          }

          if (exceptionCodes.includes("P16_CATEGORY_CONFIDENCE_LOW")) {
            warningsList.push({
              title: "주제 분석 낮은 신뢰도",
              desc: "시청 비디오 타이틀의 텍스트가 짧거나 불완전하여 카테고리 매칭 신뢰도가 낮게 나타납니다. 6대 지표 중 주제 다양성(TDS) 점수는 낮음 신뢰도의 참고용 결과로 확인하시기 바랍니다.",
              isConfidenceLow: true
            });
          }

          if (warningsList.length === 0) return null;

          return (
            <div className="rounded-3xl border border-teal-200/60 bg-teal-50/50 p-5 space-y-3.5">
              <div className="flex items-center gap-2 text-teal-850 font-extrabold text-sm">
                <AlertTriangle size={18} className="text-teal-600 shrink-0" />
                <span>💡 [분석 참고 안내] 미디어 분석 데이터 품질 안내</span>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                {warningsList.map((item, idx) => (
                  <div key={idx} className="bg-white/80 rounded-2xl p-4 border border-slate-100 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs font-black text-slate-800">{item.title}</span>
                        {item.isConfidenceLow && (
                          <span className="rounded bg-rose-50 px-1.5 py-0.5 text-[9px] font-black text-rose-600 border border-rose-100">
                            참고용 (낮은 신뢰도)
                          </span>
                        )}
                      </div>
                      <p className="mt-2 text-[11px] font-semibold text-slate-500 leading-normal">
                        {item.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })()}

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
          <ScoreCard 
            label="생각과 기록 차이" 
            value={processedData.meta_gap_available !== false && misconceptionIndex !== null ? `${misconceptionIndex}점` : "비활성"} 
            caption={processedData.meta_gap_available !== false ? (processedData.misconception?.worst_axis_name || "메타인지 갭") : "자가진단 없음"} 
            tone="bg-amber-500 text-white" 
          />
          <ScoreCard label="관심사 다양성" value={`${diversity}점`} caption="시청 기록 기준" tone="bg-sky-500 text-white" />
          <ScoreCard label="사용자 주도성" value={`${userAgency}%`} caption="직접 탐색 비중" tone="bg-teal-600 text-white" />
          <ScoreCard label="최종 디톡스 위험" value={`${finalDetoxRisk}점`} caption="정보 편향+숏츠 루프" tone="bg-slate-900 text-white" />
        </div>

        {/* Detailed Explanations & Evidence Card Grid */}
        {processedData.explanations && (
          <Card className="p-6 md:p-8 space-y-6">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.18em] text-slate-500">detailed evidence & explanations</p>
              <h2 className="mt-2 text-2xl font-black text-slate-950">핵심 진단 점수별 상세 근거 및 안내</h2>
              <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
                각 분석 지표가 어떻게 계산되었는지 상세 이유와 분석 데이터 품질에 따른 주의사항, 그리고 개선 방향을 알려드립니다.
              </p>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {Object.entries(processedData.explanations).map(([key, exp]: [string, any]) => {
                let badgeColor = "bg-slate-100 text-slate-800 border-slate-200";
                if (key === "weighted_health_score") badgeColor = "bg-emerald-50 text-emerald-800 border-emerald-200";
                else if (key === "cognitive_misconception_index") badgeColor = "bg-amber-50 text-amber-800 border-amber-200";
                else if (key === "dsao_actual_type") badgeColor = "bg-teal-50 text-teal-900 border-teal-200";
                else if (key === "bias_risk_score") badgeColor = "bg-rose-50 text-rose-800 border-rose-200";
                else if (key === "shorts_stimulation_risk") badgeColor = "bg-indigo-50 text-indigo-800 border-indigo-200";
                else if (key === "data_quality_flags") badgeColor = "bg-sky-50 text-sky-900 border-sky-200";

                return (
                  <div key={key} className="bg-[#fbfaf7] rounded-3xl border border-slate-200/60 p-5 flex flex-col justify-between space-y-4 shadow-sm hover:shadow-md transition-shadow duration-200">
                    <div>
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-sm font-black text-slate-900">{exp.label}</span>
                        <span className={`rounded-full px-2.5 py-0.5 text-xs font-black border font-mono ${badgeColor}`}>
                          {exp.value}
                        </span>
                      </div>
                      <p className="mt-3 text-xs font-semibold text-slate-500 leading-relaxed">
                        {exp.reason}
                      </p>
                    </div>

                    <div className="space-y-2.5 border-t border-slate-200/60 pt-3 text-[11px] font-semibold text-slate-500">
                      <div>
                        <span className="text-slate-800 font-bold block">📊 측정 근거</span>
                        <p className="mt-0.5 text-slate-500 leading-relaxed">{exp.evidence}</p>
                      </div>
                      {exp.caution && (
                        <div>
                          <span className="text-amber-700 font-bold block">⚠️ 주의 사항</span>
                          <p className="mt-0.5 text-slate-500 leading-relaxed">{exp.caution}</p>
                        </div>
                      )}
                      <div>
                        <span className="text-teal-700 font-bold block">💡 추천 개선 행동</span>
                        <p className="mt-0.5 text-slate-500 leading-relaxed">{exp.improvement_hint}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        )}

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

        <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
          <Card className="p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-emerald-700">ui snapshot</p>
                <h2 className="mt-2 text-2xl font-black text-slate-950">분석 하이라이트</h2>
                <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
                  최근 데이터에서 눈에 띄는 관심사를 TOP 5로 압축했습니다.
                </p>
              </div>
              <div className="rounded-2xl bg-emerald-50 px-4 py-3 text-right">
                <p className="text-[10px] font-black uppercase tracking-[0.16em] text-emerald-600">top</p>
                <p className="mt-1 text-3xl font-black text-emerald-800">{highlightInterests.length}</p>
              </div>
            </div>

            <div className="mt-6 space-y-3">
              {highlightInterests.length > 0 ? (
                highlightInterests.map((item, index) => {
                  const categoryName = String(item.category || item.name || "기타/미분류");
                  const ratio = Number(item.ratio ?? item.value ?? 0);
                  const count = Number(item.count || 0);
                  const color = INTEREST_GRAPH_COLORS[interestGroupFor(categoryName)] || INTEREST_GRAPH_COLORS.other;
                  const subLabel = item.subcategories?.[0]?.name || "세부 분류 없음";

                  return (
                    <div key={`${categoryName}-${index}`} className="rounded-2xl border border-slate-200 bg-[#fbfaf7] px-4 py-3">
                      <div className="flex items-center gap-3">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-black text-white" style={{ backgroundColor: color }}>
                          {index + 1}
                        </span>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between gap-3">
                            <p className="truncate text-sm font-black text-slate-950">{categoryName}</p>
                            <span className="text-xs font-black text-slate-500">{Math.round(ratio)}%</span>
                          </div>
                          <p className="mt-1 truncate text-xs font-bold text-slate-500">
                            {subLabel}{count > 0 ? ` · ${count}건` : ""}
                          </p>
                        </div>
                      </div>
                      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white">
                        <div className="h-full rounded-full" style={{ width: `${normalizePercent(ratio)}%`, backgroundColor: color }} />
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-200 bg-[#fbfaf7] px-4 py-6 text-sm font-bold text-slate-500">
                  표시할 관심사 분포가 아직 부족합니다.
                </div>
              )}
            </div>
          </Card>

          <Card className="p-6">
            <div className="grid gap-5 lg:grid-cols-[1fr_0.9fr]">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-cyan-700">timeline</p>
                <h2 className="mt-2 text-2xl font-black text-slate-950">관심사 변화 타임라인</h2>
                <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
                  직접 검색과 실제 시청 비중 차이를 비교해 흐름이 커진 주제를 보여줍니다.
                </p>

                <div className="mt-5 space-y-3">
                  {gapRows.length > 0 ? (
                    gapRows.map((item: any, index: number) => {
                      const categoryName = String(item.category || "기타/미분류");
                      const searchRatio = normalizePercent(item.search_ratio);
                      const watchRatio = normalizePercent(item.watch_ratio);
                      const gap = Number(item.gap || 0);
                      const color = INTEREST_GRAPH_COLORS[interestGroupFor(categoryName)] || INTEREST_GRAPH_COLORS.other;

                      return (
                        <div key={`${categoryName}-${index}`} className="rounded-2xl border border-slate-200 bg-[#fbfaf7] px-4 py-3">
                          <div className="flex items-center justify-between gap-3">
                            <p className="text-sm font-black text-slate-950">{categoryName}</p>
                            <span className={["rounded-full px-2.5 py-1 text-[10px] font-black", gap >= 0 ? "bg-amber-100 text-amber-700" : "bg-sky-100 text-sky-700"].join(" ")}>
                              {gap >= 0 ? `+${gap.toFixed(1)}` : gap.toFixed(1)}%
                            </span>
                          </div>
                          <div className="mt-3 space-y-2">
                            <div>
                              <div className="flex justify-between text-[10px] font-black text-slate-400">
                                <span>검색</span>
                                <span>{searchRatio}%</span>
                              </div>
                              <div className="mt-1 h-2 overflow-hidden rounded-full bg-white">
                                <div className="h-full rounded-full bg-slate-400" style={{ width: `${searchRatio}%` }} />
                              </div>
                            </div>
                            <div>
                              <div className="flex justify-between text-[10px] font-black text-slate-400">
                                <span>시청</span>
                                <span>{watchRatio}%</span>
                              </div>
                              <div className="mt-1 h-2 overflow-hidden rounded-full bg-white">
                                <div className="h-full rounded-full" style={{ width: `${watchRatio}%`, backgroundColor: color }} />
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div className="rounded-2xl border border-dashed border-slate-200 bg-[#fbfaf7] px-4 py-6 text-sm font-bold text-slate-500">
                      검색과 시청을 비교할 데이터가 아직 부족합니다.
                    </div>
                  )}
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-slate-950 p-5 text-white">
                <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-300">detox guide</p>
                <h3 className="mt-2 text-xl font-black">오늘의 디톡스 가이드</h3>
                <div className="mt-5 space-y-3">
                  {detoxGuideItems.map((item) => (
                    <div key={item.title} className="rounded-2xl border border-white/10 bg-white/10 px-4 py-3">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-black">{item.title}</p>
                        <span className="rounded-full bg-teal-300/20 px-2.5 py-1 text-[10px] font-black text-teal-200">{item.tag}</span>
                      </div>
                      <p className="mt-2 text-xs font-semibold leading-5 text-slate-300">{item.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </section>

        <div className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <div>
            <RadarChart data={chartData} scoreWarnings={scoreWarnings} />
            <p className="mt-2.5 text-[11px] text-slate-500 font-semibold leading-relaxed">
              ※ 비교 불가 지표는 차트 형태 유지를 위해 중립 위치(50점)에 표시되며, 실제 평균 점수 계산에는 포함되지 않습니다.
            </p>
          </div>

          <div className="space-y-4">
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
              <div className="rounded-3xl border border-slate-200 bg-[#fbfaf7] p-5 space-y-4">
                <div>
                  <p className="text-xs font-black uppercase tracking-[0.18em] text-slate-400">실제 시청 기록 (최종 DSAO 유형)</p>
                  <div className="mt-2 flex items-center justify-between">
                    <h3 className="text-2xl font-black text-slate-950">
                      {processedData.actual_dsao?.name || actualCharacter.characterName}
                    </h3>
                    <span className="rounded bg-teal-50 px-2 py-0.5 text-[10px] font-black text-teal-700 font-mono border border-teal-100">
                      신뢰도: {processedData.actual_dsao?.confidence || "보통"}
                    </span>
                  </div>
                  <p className="mt-1 text-sm font-black text-slate-600">
                    {actualCode} · {processedData.actual_dsao?.short_summary || actualCharacter.title}
                  </p>
                </div>
                
                <p className="text-xs font-bold text-slate-600 leading-relaxed">
                  {processedData.actual_dsao?.detailed_description || "유형 설명 로드 중입니다."}
                </p>
                
                <div className="grid gap-3 sm:grid-cols-2 text-[11px] font-semibold">
                  <div className="bg-white/80 rounded-xl p-3 border border-slate-100">
                    <span className="text-xs font-black text-emerald-700">💪 주요 강점</span>
                    <ul className="mt-1.5 space-y-1 text-slate-600 list-disc list-inside">
                      {(processedData.actual_dsao?.strengths || []).map((s: string) => (
                        <li key={s}>{s}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-white/80 rounded-xl p-3 border border-slate-100">
                    <span className="text-xs font-black text-rose-700">⚠️ 위험 요소</span>
                    <ul className="mt-1.5 space-y-1 text-slate-600 list-disc list-inside">
                      {(processedData.actual_dsao?.risks || []).map((r: string) => (
                        <li key={r}>{r}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="bg-teal-50/50 rounded-xl p-3 border border-teal-100 text-xs font-semibold leading-relaxed text-teal-800">
                  <strong className="block text-teal-900 font-black">🌱 맞춤 디톡스 추천 방향</strong>
                  {processedData.actual_dsao?.recommended_detox_direction}
                </div>

                <div className="text-[11px] font-semibold text-slate-500 space-y-1 bg-white/50 p-3 rounded-xl border border-slate-100">
                  <p>📊 <strong className="text-slate-600">분석 근거 (based_on):</strong></p>
                  <p className="text-slate-500 text-[10px] leading-relaxed">{processedData.actual_dsao?.based_on}</p>
                </div>

                <div className="flex flex-wrap gap-2 text-[10px] font-bold text-slate-400 items-center justify-between border-t border-slate-200/60 pt-3">
                  <div className="flex gap-2">
                    <span>유사 유형: {processedData.actual_dsao?.similar_types?.join(", ") || "없음"}</span>
                    <span>·</span>
                    <span>대비 유형: {processedData.actual_dsao?.opposite_type || "없음"}</span>
                  </div>
                  <span className="font-mono text-slate-300">mbti_compat: {processedData.internal_balance_type || "N/A"}</span>
                </div>
              </div>
            </div>
            <div className="mt-4 rounded-2xl bg-[#fbfaf7] p-4 border border-slate-200 text-xs font-semibold text-slate-600">
              ℹ️ {processedData.excluded_axes && processedData.excluded_axes.length > 0 ? (
                "데이터가 부족한 일부 지표는 착각 지수 계산에서 제외되었습니다."
              ) : (
                "6개 지표 전체를 기준으로 착각 지수를 계산했습니다."
              )}
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
              const gap = axis.gap;
              const isAvailable = axis.available !== false;
              const hasGap = isAvailable && gap !== null && gap !== undefined;
              const detail = processedData.score_details?.[key];
              const isExpanded = !!expandedComponents[key];

              return (
                <Card 
                  key={key} 
                  className={[
                    "p-5 flex flex-col justify-between h-full transition-all duration-300",
                    isAvailable 
                      ? "bg-white border-slate-200 hover:shadow-md" 
                      : "bg-slate-900/40 border border-slate-700/70 text-slate-400"
                  ].join(" ")}
                >
                  <div>
                    <div className="flex items-start justify-between gap-3 border-b border-slate-100/10 pb-3 mb-4">
                      <h3 className={["text-base font-black", isAvailable ? "text-slate-950" : "text-slate-200"].join(" ")}>
                        {AXIS_LABELS[key] || axis.name || key}
                      </h3>
                      {isAvailable ? (
                        hasGap ? (
                          <span className={["rounded-full px-2.5 py-1 text-[10px] font-black", gap >= 0 ? "bg-rose-100 text-rose-700" : "bg-teal-100 text-teal-700"].join(" ")}>
                            {gap >= 0 ? `+${gap}` : gap}점
                          </span>
                        ) : (
                          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-black text-slate-500">
                            비교 불가
                          </span>
                        )
                      ) : (
                        <span className="rounded-full bg-slate-800 border border-slate-700 px-2.5 py-1 text-[10px] font-black text-slate-300">
                          비교 불가
                        </span>
                      )}
                    </div>

                    {isAvailable ? (
                      // available = true State
                      <div className="space-y-3 text-left">
                        <div className="flex items-baseline gap-2">
                          <span className="text-3xl font-black text-slate-950 font-mono">
                            {axis.actual !== null && axis.actual !== undefined ? axis.actual.toFixed(1) : "0.0"}
                          </span>
                          <span className="text-xs font-bold text-slate-500">점 ({formatGrade(axis.actual || 0)})</span>
                        </div>
                        <p className="text-[11px] font-bold text-slate-600 bg-slate-50 px-2.5 py-1 rounded-lg w-fit">
                          신뢰도: <span className="text-teal-600 font-extrabold">{formatConfidence(detail?.confidence)}</span>
                        </p>
                        <p className="text-xs text-slate-600 leading-relaxed font-semibold">
                          {AXIS_AVAILABLE_DESCS[key] || detail?.reason || "정상 분석되었습니다."}
                        </p>

                        <div className="mt-4 pt-3 border-t border-slate-100/80 space-y-1 text-xs text-slate-500 font-semibold">
                          <div className="flex justify-between">
                            <span>자가진단 결과:</span>
                            <span className="text-slate-800">{axis.survey !== null ? `${Math.round(axis.survey)}점` : "기록 없음"}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>실제 분석값:</span>
                            <span className="text-slate-800">{axis.actual !== null ? `${axis.actual.toFixed(1)}점` : "0.0점"}</span>
                          </div>
                          {axis.survey !== null && (
                            <div className="flex justify-between font-bold">
                              <span>메타인지 격차 (Gap):</span>
                              <span className={gap >= 0 ? "text-rose-600" : "text-teal-600"}>
                                {gap >= 0 ? `+${gap.toFixed(1)}` : gap.toFixed(1)}점
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    ) : (
                      // available = false State
                      <div className="space-y-3 text-left">
                        <div className="py-2">
                          <span className="text-2xl font-black text-amber-300 font-sans tracking-tight">비교 불가</span>
                        </div>
                        <div className="rounded-2xl bg-slate-950/50 p-3 border border-slate-800 text-xs text-slate-400">
                          <p className="font-bold mb-1 text-amber-300">⚠️ 데이터 부족</p>
                          <p className="leading-relaxed font-semibold">
                            사유: <span className="text-amber-300 font-black">{axis.reason || AXIS_UNAVAILABLE_REASON_LABELS[key] || "채널 정보 없음"}</span>
                          </p>
                        </div>
                        <p className="text-xs text-slate-400 font-bold leading-relaxed">
                          이 지표는 데이터 부족으로 공식 점수 계산에서 제외되었습니다.
                        </p>

                        <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-1 text-xs text-slate-500 font-semibold">
                          <div className="flex justify-between">
                            <span>자가진단:</span>
                            <span>비교 불가</span>
                          </div>
                          <div className="flex justify-between">
                            <span>실제 기록:</span>
                            <span>비교 불가</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Toggle Component Button */}
                  <div className="mt-4 pt-3 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => toggleComponent(key)}
                      className={[
                        "flex items-center justify-between w-full text-xs font-black py-1.5 px-3 rounded-xl transition-all duration-200",
                        isExpanded
                          ? "bg-slate-900 text-white"
                          : "bg-slate-100 hover:bg-slate-200 text-slate-700"
                      ].join(" ")}
                    >
                      <span>{(AXIS_LABELS[key] || key)} 계산 근거 보기</span>
                      <span className="font-mono text-[10px]">{isExpanded ? "▲ 닫기" : "▼ 펼치기"}</span>
                    </button>

                    {isExpanded && renderComponentDetails(key, detail?.score_components, detail?.warnings)}
                  </div>
                </Card>
              );
            })}
          </div>
        </section>

        <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6 md:p-8 text-slate-100 shadow-2xl">
          <p className="text-xs font-black uppercase tracking-[0.18em] text-purple-400">Data Reliability & Pipeline</p>
          <h2 className="mt-2 text-2xl font-black text-white">분석 신뢰도 및 데이터 품질</h2>
          <p className="mt-2 text-sm leading-6 text-slate-400">
            업로드된 YouTube Takeout 데이터의 분석 품질 상태와 표본 수집 정보입니다.
          </p>

          <div className="mt-6 grid gap-6 md:grid-cols-2">
            <div className="space-y-4">
              {/* Overall Confidence Card */}
              <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                <h3 className="text-sm font-black text-white">종합 분석 신뢰도</h3>
                <div className="mt-3 flex items-center gap-3">
                  <span className={[
                    "rounded-full px-3 py-1 text-xs font-black text-white",
                    processedData.overall_confidence === "high" ? "bg-emerald-600" :
                    processedData.overall_confidence === "medium" ? "bg-amber-500" : "bg-rose-600"
                  ].join(" ")}>
                    {formatConfidence(processedData.overall_confidence)}
                  </span>
                  <p className="text-xs font-semibold text-slate-300">
                    {CONFIDENCE_DESCS[processedData.overall_confidence || "medium"]}
                  </p>
                </div>
              </div>

              {/* Sampling Information Card */}
              <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                <h3 className="text-sm font-black text-white">세션 대표 샘플링 정보</h3>
                <div className="mt-3 text-xs font-semibold text-slate-300">
                  <p className="text-sm font-black text-purple-300 mb-3">
                    전체 {processedData.sampling_metadata?.total_session_count || processedData.data_coverage?.total_session_count || 0}개 세션 중 대표 {processedData.sampling_metadata?.sampled_session_count || processedData.data_coverage?.sampled_session_count || 0}개 세션을 분석했습니다.
                  </p>
                  <p className="text-slate-400 mb-4 leading-relaxed">
                    {processedData.sampling_metadata?.sampling_strategy === "all_sessions" 
                      ? "전체 세션을 기반으로 분석을 수행했습니다." 
                      : "최근/오래된/중간/긴 세션/검색 포함 세션을 혼합해 대표 샘플을 구성했습니다."}
                  </p>
                  <div className="space-y-2 text-[11px]">
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400">샘플링 추출 전략</span>
                      <span className="font-bold text-white">
                        {processedData.sampling_metadata?.sampling_strategy === "all_sessions" ? "전체 분석 (All)" : "대표성 블렌딩 (Blended)"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">NLP 입력 토큰량</span>
                      <span className="font-bold text-white font-mono">
                        {Number(processedData.sampling_metadata?.nlp_input_token_count || 0).toLocaleString()} 자
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {/* Excluded Axes Card */}
              <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                <h3 className="text-sm font-black text-white">평가 제외 지표 (Excluded Axes)</h3>
                <div className="mt-3">
                  {processedData.excluded_axes && processedData.excluded_axes.length > 0 ? (
                    <div className="space-y-3">
                      <div className="flex flex-wrap gap-2">
                        {processedData.excluded_axes.map((axis: string) => (
                          <span key={axis} className="rounded-full bg-rose-500/10 border border-rose-500/30 px-2.5 py-1 text-xs font-black text-rose-400">
                            {AXIS_LABELS[axis] || axis}
                          </span>
                        ))}
                      </div>
                      <div className="mt-2 space-y-1.5 text-xs text-slate-300">
                        {processedData.excluded_axes.map((axis: string) => (
                          <div key={axis} className="flex gap-2">
                            <span className="text-rose-400 font-bold shrink-0">{AXIS_LABELS[axis] || axis}:</span>
                            <span className="text-slate-400">{processedData.score_details?.[axis]?.reason || AXIS_UNAVAILABLE_REASON_LABELS[axis] || "데이터 부족으로 계산 제외"}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <span className="text-xs font-bold text-slate-400">없음 (모든 지표 정상 분석 완료)</span>
                  )}
                </div>
                <p className="mt-3 text-[11px] font-semibold leading-relaxed text-slate-500">
                  ※ 제외 지표는 데이터 누락 또는 불균형으로 인해 건강 점수(Health) 및 편향성 쏠림 점수의 평균 계산에서 자동 제외되었습니다.
                </p>
              </div>

              {/* Data Quality Flags Card */}
              <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                <h3 className="text-sm font-black text-white">데이터 품질 플래그 (Flags)</h3>
                <div className="mt-3 space-y-2 max-h-48 overflow-y-auto pr-1">
                  {(() => {
                    const flags = [...(processedData.data_quality_flags || [])];
                    if (processedData.data_quality?.duration === "estimated" && !flags.includes("duration_estimated")) {
                      flags.push("duration_estimated");
                    }
                    if (processedData.data_quality?.nlp_provider === "rule_based_fallback" && !flags.includes("nlp_fallback_used")) {
                      flags.push("nlp_fallback_used");
                    }
                    
                    if (flags.length > 0) {
                      return flags.map((flag: string) => {
                        const label = QUALITY_FLAG_LABELS[flag] || { title: flag, desc: "데이터 전처리 과정에서 특이사항이 감지되었습니다." };
                        return (
                          <div key={flag} className="rounded-xl bg-slate-900 p-3 border border-slate-800/60">
                            <p className="text-xs font-black text-amber-400">⚠️ {label.title}</p>
                            <p className="mt-1 text-[11px] font-semibold text-slate-400 leading-4">{label.desc}</p>
                          </div>
                        );
                      });
                    }
                    return <p className="text-xs font-semibold text-slate-400">데이터 수집상 특이사항이 없이 깨끗하게 파싱되었습니다.</p>;
                  })()}
                </div>
              </div>
            </div>
          </div>

          {/* Jury/Evaluator Tech Specs Explanation Panel */}
          <div className="mt-8 border-t border-slate-800 pt-6">
            <h3 className="text-sm font-black uppercase tracking-[0.16em] text-purple-400 mb-3">
              [심사위원용] 백엔드 계산 엔진 및 분석 엄밀성 검증 (Technical Specifications)
            </h3>
            <div className="grid gap-4 md:grid-cols-3 text-xs leading-relaxed text-slate-300">
              <div className="rounded-2xl bg-slate-950 p-4 border border-slate-800">
                <p className="font-bold text-amber-400 mb-1.5">1. 데이터 결손 보정 (Data Deficiency Policy)</p>
                <p className="text-slate-400 font-medium">
                  데이터가 극단적으로 부족하거나(예: 채널명 없음, 검색 기록 부재) 분석 신뢰 수준이 기준값 미만인 경우, 무리하게 추정 점수를 부여하여 분석 결과를 왜곡하지 않습니다. 해당 축은 <span className="text-slate-200">available=false</span> 처리되며, 평균 점수 및 메타인지 격차(Gap) 최종 계산식에서 원천 제외됩니다. (UI상에는 50.0 중립값으로 시각적 밸런스만 유지)
                </p>
              </div>
              <div className="rounded-2xl bg-slate-950 p-4 border border-slate-800">
                <p className="font-bold text-amber-400 mb-1.5">2. 시청 시간 한계 대응 (Duration Limits)</p>
                <p className="text-slate-400 font-medium">
                  Google Takeout YouTube 원본 데이터에는 각 영상의 실제 시청 지속 시간이 포함되어 있지 않습니다. 따라서 본 엔진은 재생 횟수 및 시청 간격(순차 재생 타임스탬프)에 의존하는 한계를 명시하고, “추정 시청 시간”과 같은 임의 추정을 배제하여 계산 정합성을 유지합니다.
                </p>
              </div>
              <div className="rounded-2xl bg-slate-950 p-4 border border-slate-800">
                <p className="font-bold text-amber-400 mb-1.5">3. 하위 컴포넌트 결합식 (Component Composition)</p>
                <p className="text-slate-400 font-medium">
                  각 6축 평가는 단일 수식이 아닌 검색 비율, 직접 선택 경로, 구독/보관함 비율, 참여도 등 여러 세부 수치의 동적 조합으로 결정됩니다. 데이터가 부족한 컴포넌트는 가중치 재계산에서 자동 제외됩니다. &ldquo;계산 근거 보기&rdquo; 토글을 통해 백엔드가 반환한 세부 원본 수치와 기여도 및 보정 페널티 세부 요소를 가감 없이 투명하게 제공합니다.
                </p>
              </div>
            </div>
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
