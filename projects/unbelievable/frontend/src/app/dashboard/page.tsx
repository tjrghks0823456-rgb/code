"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import CharacterAvatar from "../../components/CharacterAvatar";
import RadarChart from "../../components/RadarChart";
import { getDsaoCharacter } from "../../data/dsaoCharacters";
import { loadSelfSurveyResult, SelfSurveyResult } from "../../utils/surveyStorage";

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const runId = searchParams.get("run_id");
  
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [selfSurvey, setSelfSurvey] = useState<SelfSurveyResult | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [generatingPlan, setGeneratingPlan] = useState(false);
  const [detoxError, setDetoxError] = useState<string | null>(null);

  useEffect(() => {
    // Load local self-survey result
    const survey = loadSelfSurveyResult();
    setSelfSurvey(survey);

    if (!runId) {
      setApiError("분석 ID(run_id)가 전달되지 않았습니다. 시청 기록 분석을 먼저 마쳐주세요.");
      setLoading(false);
      return;
    }

    const fetchSummary = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/dashboard/summary?run_id=${runId}&user_id=00000000-0000-0000-0000-000000000001`);
        if (!res.ok) {
          throw new Error(`데이터 조회 실패 (HTTP 상태코드 ${res.status})`);
        }
        const json = await res.json();
        setData(json);
      } catch (err: any) {
        console.error("Dashboard fetch failed:", err);
        setApiError(err.message || "서버에서 분석 결과를 불러오지 못했습니다.");
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
        } else {
          setDetoxError(json.detail || "디톡스 미션 플랜 생성에 실패했습니다. 백엔드에서 빈 결과를 반환했습니다.");
        }
      } else {
        const errorText = await res.text();
        let parsedDetail = "서버 내부 오류가 발생했습니다.";
        try {
          const parsed = JSON.parse(errorText);
          parsedDetail = parsed.detail || parsedDetail;
        } catch (_) {}
        setDetoxError(`디톡스 플랜 생성 실패 (HTTP 상태코드 ${res.status}): ${parsedDetail}`);
      }
    } catch (err: any) {
      console.error("Detox plan generation failed:", err);
      setDetoxError(`디톡스 플랜 생성 에러: ${err.message || "네트워크 연결을 확인해주세요."}`);
    } finally {
      setGeneratingPlan(false);
    }
  };

  // 1. Process local survey scores and override backend meta_gap if available
  const processedData = React.useMemo(() => {
    if (!data) return null;
    
    // Deep clone to avoid mutating the original fetched data
    const clone = JSON.parse(JSON.stringify(data));
    
    if (!selfSurvey || !selfSurvey.axisScores) {
      return clone;
    }
    
    const { D, P, W, N, S, M } = selfSurvey.axisScores;
    
    const safeDiv = (num: number, den: number, fallback = 50) => {
      if (den === 0) return fallback;
      return Math.round((num / den) * 100);
    };

    // [Requirement 2: MVP temporary mapping]
    // This mapping converts the 8-axis (DP/WN/SM/FL) self-survey values from localStorage
    // to match the 6-axis structure used by the dashboard:
    // UAS = D / (D + P) * 100
    // TDS = W / (W + N) * 100
    // SMS = M / (S + M) * 100
    // EBS = 50 (default fallback for MVP)
    // VOS = W / (W + N) * 100
    // SBS = 50 (default fallback for MVP)
    //
    // Note: This is an MVP-only local mapping. When Supabase Survey DB is connected,
    // this logic should be migrated to the backend database / api routes so that
    // meta_gap is calculated server-side directly.
    const surveyValues: Record<string, number> = {
      UAS: safeDiv(D, D + P),
      TDS: safeDiv(W, W + N),
      SMS: safeDiv(M, S + M),
      EBS: 50,
      VOS: safeDiv(W, W + N),
      SBS: 50
    };

    // Recompute meta_gap and misconception based on local survey values
    let maxGapValue = -1;
    let worstAxisCode = "TDS";
    
    const axis_names: Record<string, string> = {
      TDS: "주제 다양성",
      SBS: "출처 균형",
      EBS: "감정 균형",
      VOS: "관점 개방성",
      SMS: "유해/자극 안전",
      UAS: "사용자 주도성"
    };

    Object.keys(clone.meta_gap).forEach(code => {
      if (surveyValues[code] !== undefined) {
        const s_val = surveyValues[code];
        const a_val = clone.meta_gap[code].actual;
        const gap = s_val - a_val;
        
        clone.meta_gap[code].survey = s_val;
        clone.meta_gap[code].gap = Math.round(gap * 10) / 10;
        
        const absGap = Math.abs(gap);
        if (absGap > maxGapValue) {
          maxGapValue = absGap;
          worstAxisCode = code;
        }
      }
    });

    const avgGap = Object.keys(clone.meta_gap).reduce((sum, code) => sum + Math.abs(clone.meta_gap[code].gap), 0) / 6;
    const misconceptionIndex = Math.min(100.0, Math.round(avgGap * 1.5 * 10) / 10);
    
    clone.misconception = {
      index: misconceptionIndex,
      worst_axis_code: worstAxisCode,
      worst_axis_name: axis_names[worstAxisCode],
      worst_gap_value: clone.meta_gap[worstAxisCode].gap,
      message: `스스로 사전 인지했던 점수 대비 실제 YouTube 소비 데이터상으로 '${axis_names[worstAxisCode]}' 영역의 차이가 가장 크게 집계되었습니다. 가벼운 일상 추천 루틴 수정을 통해 성향의 균형을 복원하시는 것을 추천합니다.`
    };

    return clone;
  }, [data, selfSurvey]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-white p-6">
        <span className="animate-spin text-3xl mb-4">🌀</span>
        <p className="text-slate-400 font-semibold">시청 기록 데이터 분석 결과 수집 중...</p>
      </div>
    );
  }

  if (apiError) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 text-slate-100">
        <div className="w-full max-w-md bg-slate-900/60 border border-red-500/20 rounded-3xl p-8 backdrop-blur-md shadow-2xl text-center space-y-6">
          <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center text-2xl text-red-400 mx-auto">
            ⚠️
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">분석 결과를 불러올 수 없습니다</h2>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              백엔드 서버(FastAPI: Port 8000)가 정상 기동 중인지 혹은 유효한 분석 ID가 맞는지 확인해 주세요.
            </p>
            <p className="text-[10px] text-red-500/80 bg-red-950/20 border border-red-900/30 px-3 py-1.5 rounded-lg mt-3 break-words">
              에러 정보: {apiError}
            </p>
          </div>
          <button 
            onClick={() => router.push("/upload")} 
            className="w-full py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white font-bold rounded-xl transition-all text-xs"
          >
            시청 기록 업로드 화면으로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  if (!processedData) return null;

  // Formatting chart data mapping: replacing '주관적_인식' with '자가진단_결과'
  const chartData = Object.keys(processedData.meta_gap).map(key => ({
    subject: processedData.meta_gap[key].name,
    "자가진단_결과": processedData.meta_gap[key].survey,
    "실제_분석값": processedData.meta_gap[key].actual
  }));

  // Signal Light (Traffic light) based on bias risk score
  const getSignalColor = (score: number) => {
    if (score < 20) return { bg: "bg-emerald-500", text: "text-emerald-400", label: "안전 (Clean)" };
    if (score < 40) return { bg: "bg-green-500", text: "text-green-400", label: "양호 (Mild)" };
    if (score < 60) return { bg: "bg-yellow-500", text: "text-yellow-400", label: "주의 (Warning)" };
    if (score < 80) return { bg: "bg-orange-500", text: "text-orange-400", label: "경고 (Danger)" };
    return { bg: "bg-red-500", text: "text-red-400", label: "위험 (Critical)" };
  };

  const signal = getSignalColor(processedData.bias_risk_score);
  
  // Look up character properties based on calculated actual code
  const actualCode = processedData.actual_dsao?.code?.toUpperCase() || "PNML";
  const character = getDsaoCharacter(actualCode);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-body">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Detox Generation API Error Alert */}
        {detoxError && (
          <div className="bg-red-950/20 border border-red-500/30 rounded-3xl p-6 backdrop-blur-md flex flex-col md:flex-row justify-between items-start md:items-center gap-4 animate-in fade-in slide-in-from-top-4 duration-300">
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-red-400 flex items-center gap-2">
                <span>⚠️</span> 디톡스 미션 생성 실패
              </h4>
              <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
                실제 API(FastAPI: Port 8000)를 통한 디톡스 미션 플랜 실시간 생성에 실패했습니다. 서버 상태 또는 API Key를 점검하세요.<br />
                <span className="text-[10px] text-red-400 font-mono">오류메시지: {detoxError}</span>
              </p>
            </div>
            <div className="flex gap-2 w-full md:w-auto">
              <button
                onClick={handleStartDetox}
                className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-300 font-bold rounded-xl text-xs transition-all w-full md:w-auto"
              >
                다시 시도
              </button>
              <button
                onClick={() => router.push("/mission?demo=true")}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 font-bold rounded-xl text-xs transition-all w-full md:w-auto"
              >
                시연용 데이터로 보기
              </button>
            </div>
          </div>
        )}

        {/* Navbar */}
        <div className="flex justify-between items-center border-b border-slate-900 pb-6">
          <div>
            <h1 className="text-2xl font-extrabold text-white font-heading tracking-tight">SH.SON_UNBELIEVABLE</h1>
            <p className="text-xs text-slate-400">데이터 기반 디지털 콘텐츠 성향 모니터링 리포트</p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => router.push("/types")}
              className="px-5 py-3 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-white font-bold rounded-xl transition-all text-xs"
            >
              🌐 다른 유형 둘러보기
            </button>
            <button 
              onClick={handleStartDetox}
              disabled={generatingPlan}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-purple-500/20 text-xs flex items-center justify-center gap-1.5"
            >
              {generatingPlan ? (
                <>
                  <span className="animate-spin">⏳</span> 추천 미션 설계 중...
                </>
              ) : (
                <>🎯 디톡스 미션 센터 진입</>
              )}
            </button>
          </div>
        </div>
 
        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Left Block: Signal & MBTI Card */}
          <div className="space-y-6 md:col-span-1">
            
            {/* 5-Level Signal Card */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden backdrop-blur-md">
              <h3 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-4">종합 편향 위험도</h3>
              <div className="flex items-center gap-4">
                <div className={`w-6 h-6 rounded-full ${signal.bg} animate-pulse shadow-2xl`} />
                <div>
                  <div className="text-3xl font-extrabold text-white">{processedData.bias_risk_score}점</div>
                  <div className={`text-sm font-bold mt-1 ${signal.text}`}>{signal.label}</div>
                </div>
              </div>
              <p className="text-xs text-slate-400 mt-4 leading-relaxed">
                전체 6축 인지 지표의 가중합을 계산한 결과입니다. 현재 시청 이력에서 알고리즘 자동 추천 노출로 인해 축적된 편향 상태를 시각화합니다.
              </p>
            </div>
 
            {/* 16-Type MBTI Card */}
            <div className="bg-gradient-to-br from-purple-900/30 to-indigo-900/20 border border-slate-800 rounded-3xl p-6 shadow-2xl backdrop-blur-md relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full blur-2xl" />
              <h3 className="text-xs uppercase tracking-wider text-purple-400 font-semibold mb-4">미디어 소비성향 유형 (소비 MBTI)</h3>
              <h2 className="text-2xl font-black text-white font-heading tracking-tight">{processedData.mbti.name}</h2>
              <div className="flex flex-wrap gap-2 mt-4">
                {processedData.mbti.tags.map((t: string) => (
                  <span key={t} className="text-[10px] bg-purple-500/10 text-purple-300 px-3 py-1 rounded-full border border-purple-500/20 font-semibold">
                    {t}
                  </span>
                ))}
              </div>
              <p className="text-xs text-slate-400 mt-4 leading-relaxed">
                주제 다양성과 자극 민감도를 종합 판정한 고유 성향 카드입니다. 실제 데이터 기반의 카테고리 고착 상태를 나타냅니다.
              </p>
            </div>
            
          </div>
 
          {/* Right Block: Overlay Radar Chart (Meta-gap) */}
          <div className="md:col-span-2">
            <RadarChart data={chartData} />
          </div>
 
        </div>
 
        {/* Dynamic DSAO Character Profile Card */}
        <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 md:p-8 backdrop-blur-md shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 rounded-full blur-3xl" />
          <div className="flex flex-col lg:flex-row justify-between items-start gap-6 mb-6 border-b border-slate-900 pb-6">
            <div className="flex flex-col sm:flex-row items-start gap-5">
              <CharacterAvatar code={actualCode} size="lg" showName={false} />
              <div>
                <span className="text-xs font-semibold tracking-wider text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-full uppercase">
                  실제 데이터 기반 알고리즘 유형 캐릭터
                </span>
                <h2 className="text-3xl font-black text-white mt-4 font-heading tracking-tight flex flex-wrap items-center gap-2">
                  {character.characterName}
                  <span className="text-sm font-semibold text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                    {actualCode}
                  </span>
                </h2>
                <p className="text-sm font-bold text-slate-300 mt-1">{character.name}</p>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed max-w-2xl">
                  {character.visualConcept}
                </p>
              </div>
            </div>
            <div className="flex flex-wrap gap-1.5 lg:justify-end">
              {character.tags.map(tag => (
                <span key={tag} className="text-[10px] bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 px-2.5 py-1 rounded-full font-bold">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1 space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">유형 한 줄 요약</span>
              <p className="text-sm text-slate-400 leading-relaxed font-medium">
                {character.oneLiner}
              </p>
            </div>
            
            <div className="md:col-span-1 space-y-2 border-t md:border-t-0 md:border-l border-slate-900 pt-4 md:pt-0 md:pl-6">
              <span className="text-xs font-bold text-amber-500 uppercase tracking-wider">⚠️ 주의할 점</span>
              <p className="text-xs text-slate-400 leading-relaxed">
                {character.attention}
              </p>
            </div>
            
            <div className="md:col-span-1 space-y-2 border-t md:border-t-0 md:border-l border-slate-900 pt-4 md:pt-0 md:pl-6">
              <span className="text-xs font-bold text-emerald-500 uppercase tracking-wider">🌱 추천 회복 방향</span>
              <p className="text-xs text-slate-400 leading-relaxed">
                {character.recovery}
              </p>
            </div>
          </div>
        </div>
 
        {/* 자가진단 vs 실제 데이터 분석 DSAO 비교 카드 및 메타인지 갭 */}
        {selfSurvey && processedData.actual_dsao && (
          <div className="bg-slate-900/20 border border-slate-800/80 rounded-3xl p-6 md:p-8 backdrop-blur-md shadow-2xl space-y-6">
            <div className="flex items-center gap-3 mb-2 border-b border-slate-900 pb-4">
              <span className="text-xl">📊</span>
              <div>
                <h2 className="text-lg font-bold text-white font-heading">사전 자가진단과 실제 분석 결과 대조 및 메타인지 갭</h2>
                <p className="text-xs text-slate-400">스스로 사전 진행한 자가진단(예측)과 YouTube 실제 시청기록 분석(사후) 지표 간의 대조군입니다.</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* 자가진단 결과 DSAO */}
              <div className="bg-slate-950/40 border border-slate-800 p-5 rounded-2xl relative">
                <span className="absolute top-4 right-4 text-[9px] uppercase font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded">
                  사전 자가진단 결과
                </span>
                <h3 className="text-xs text-slate-500 font-bold uppercase tracking-wider">자가진단 예측 코드</h3>
                <h4 className="text-3xl font-black text-white mt-1 font-heading tracking-tight">{selfSurvey.resultCode}</h4>
                <h5 className="text-sm font-bold text-slate-400 mt-0.5">{selfSurvey.resultName}</h5>
                
                <div className="mt-4 space-y-2 text-xs text-slate-400">
                  <div className="flex justify-between border-b border-slate-900 pb-1.5">
                    <span>1. 탐색 방식:</span>
                    <span className="font-semibold text-slate-200">{selfSurvey.resultCode.includes("D") ? "직접 운전형 (D)" : "추천 탑승형 (P)"}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-900 pb-1.5">
                    <span>2. 관심 범위:</span>
                    <span className="font-semibold text-slate-200">{selfSurvey.resultCode.includes("W") ? "폭넓은 탐색형 (W)" : "집중 몰입형 (N)"}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-900 pb-1.5">
                    <span>3. 자극 성향:</span>
                    <span className="font-semibold text-slate-200">{selfSurvey.resultCode.includes("M") ? "안정 정보형 (M)" : "고자극 반응형 (S)"}</span>
                  </div>
                  <div className="flex justify-between pb-0.5">
                    <span>4. 시청 호흡:</span>
                    <span className="font-semibold text-slate-200">{selfSurvey.resultCode.includes("L") ? "롱폼 몰입형 (L)" : "숏폼 속도형 (F)"}</span>
                  </div>
                </div>
              </div>
 
              {/* 객관적 실제 분석 DSAO */}
              <div className="bg-slate-950/40 border border-slate-800 p-5 rounded-2xl relative">
                <span className="absolute top-4 right-4 text-[9px] uppercase font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2 py-0.5 rounded">
                  실제 데이터 분석 결과
                </span>
                <h3 className="text-xs text-slate-500 font-bold uppercase tracking-wider">실제 분석 사후 코드</h3>
                <h4 className="text-3xl font-black text-white mt-1 font-heading tracking-tight">{processedData.actual_dsao.code}</h4>
                <h5 className="text-sm font-bold text-slate-400 mt-0.5">{processedData.actual_dsao.name}</h5>
                
                <div className="mt-4 space-y-2 text-xs text-slate-400">
                  <div className="flex justify-between border-b border-slate-900 pb-1.5">
                    <span>1. 탐색 방식:</span>
                    <span className="font-semibold text-slate-200">{processedData.actual_dsao.code.includes("D") ? "직접 운전형 (D)" : "추천 탑승형 (P)"}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-900 pb-1.5">
                    <span>2. 관심 범위:</span>
                    <span className="font-semibold text-slate-200">{processedData.actual_dsao.code.includes("W") ? "폭넓은 탐색형 (W)" : "집중 몰입형 (N)"}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-900 pb-1.5">
                    <span>3. 자극 성향:</span>
                    <span className="font-semibold text-slate-200">{processedData.actual_dsao.code.includes("M") ? "안정 정보형 (M)" : "고자극 반응형 (S)"}</span>
                  </div>
                  <div className="flex justify-between pb-0.5">
                    <span>4. 시청 호흡:</span>
                    <span className="font-semibold text-slate-200">{processedData.actual_dsao.code.includes("L") ? "롱폼 몰입형 (L)" : "숏폼 속도형 (F)"}</span>
                  </div>
                </div>
              </div>
 
            </div>
 
            {/* Meta-gap comparison text summary */}
            <div className="bg-slate-950/20 border border-slate-800 rounded-2xl p-5">
              <div className="flex items-start gap-3">
                <span className="text-lg text-purple-400">💡</span>
                <div className="space-y-1">
                  <h4 className="text-xs font-bold text-slate-400">메타인지 격차 경향성 리포트</h4>
                  <p className="text-xs text-slate-400 leading-relaxed font-body">
                    {selfSurvey.resultCode === processedData.actual_dsao.code 
                      ? `귀하가 사전 진단한 예측 성향(${selfSurvey.resultCode})과 실제 시청 기록 데이터 분석 성향이 일치합니다! 자신의 미디어 소비 패턴에 대해 우수한 메타인지를 유지하고 계십니다.`
                      : `귀하의 사전 자가진단 예측 유형([${selfSurvey.resultName}])과 실제 시청 데이터 사후 측정 유형([${processedData.actual_dsao.name}]) 사이에 격차가 존재합니다. 추천 엔진 노출 비중 및 시청 호흡에서 자기도 모르게 수동 노출의 비중이 컸음을 나타내는 '메타인지 갭' 상태입니다.`}
                  </p>
                </div>
              </div>
            </div>
 
          </div>
        )}
 
        {/* 6-Axis Scores List */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {Object.keys(processedData.meta_gap).map(key => {
            const axis = processedData.meta_gap[key];
            return (
              <div key={key} className="bg-slate-900/20 border border-slate-800/80 rounded-2xl p-6 transition-all hover:border-slate-700/80 hover:bg-slate-900/30">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="text-sm font-bold text-slate-300">{axis.name}</h4>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${axis.gap > 0 ? "bg-red-500/10 text-red-400 border border-red-500/20" : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"}`}>
                    {axis.gap > 0 ? `과대평가 +${axis.gap}점` : `과소평가 ${axis.gap}점`}
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs text-slate-500">
                    <span>자가진단 예측</span>
                    <span>{axis.survey}점</span>
                  </div>
                  <div className="flex justify-between text-xs text-slate-300 font-bold">
                    <span>실제 데이터 분석 결과</span>
                    <span className="text-purple-400">{axis.actual}점</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-white">
        <span className="animate-spin text-3xl mb-4">🌀</span>
        <p className="text-slate-400 font-semibold">시청 기록 데이터 분석 결과 구성 중...</p>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}
