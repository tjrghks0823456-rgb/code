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
import { API_BASE_URL, DEFAULT_USER_ID } from "../../utils/apiConfig";
import { loadSelfSurveyResult, SelfSurveyResult } from "../../utils/surveyStorage";

type ApiData = any;
type SearchKeyword = { keyword: string; count: number; category?: string };
type InterestSubcategory = { name?: string; ratio?: number; value?: number; entities?: string[]; raw_items?: string[]; confidence?: string };
type InterestCategory = { category?: string; name?: string; value?: number; ratio?: number; count?: number; subcategories?: InterestSubcategory[] };
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

function buildInterestGraphData(label: string, map: any, tone: "search" | "video" | "shorts") {
  const distribution: InterestCategory[] = Array.isArray(map?.category_distribution) ? map.category_distribution : [];
  const nodes: InterestGraphNode[] = [];
  const edges: InterestGraphEdge[] = [];
  let nextId = 1;

  nodes.push({
    id: nextId++,
    label: `${label.replace(" 맵", "")}\nInterest`,
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

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <p className="text-sm font-black text-slate-950">{label}</p>
        <span className={["rounded-full px-2.5 py-1 text-[10px] font-black", surface.chip].join(" ")}>
          {graphData.categoryCount > 0 ? `${graphData.categoryCount}개 대분류` : "데이터 없음"}
        </span>
      </div>
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
