"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import RadarChart from "../../components/RadarChart";
import { loadSelfSurveyResult, SelfSurveyResult } from "../../utils/surveyStorage";

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const runId = searchParams.get("run_id") || "prototype-run-id";
  
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [selfSurvey, setSelfSurvey] = useState<SelfSurveyResult | null>(null);

  useEffect(() => {
    // Load local self-survey result
    const survey = loadSelfSurveyResult();
    setSelfSurvey(survey);

    // In a real application, fetches from GET /api/v1/dashboard/summary?run_id=runId
    // For this prototype, we simulate a mock fetch loading the parsed schema details
    setTimeout(() => {
      setData({
        bias_risk_score: 62.4,
        weighted_health: 37.6,
        mbti: {
          code: "LLLH",
          name: "도파민 추적자",
          tags: ["#자극", "#쇼츠", "#재미", "#알고리즘중독"]
        },
        actual_dsao: {
          code: "PNSF",
          name: "알고리즘 도파민 루프",
          scores: {
            D: 31.0, P: 69.0,
            W: 35.0, N: 65.0,
            S: 80.0, M: 20.0,
            F: 75.0, L: 25.0
          }
        },
        meta_gap: {
          TDS: { name: "주제 다양성", survey: 70.0, actual: 35.0, gap: 35.0 },
          SBS: { name: "출처 균형", survey: 60.0, actual: 40.0, gap: 20.0 },
          EBS: { name: "감정 균형", survey: 50.0, actual: 48.0, gap: 2.0 },
          VOS: { name: "관점 개방성", survey: 65.0, actual: 52.0, gap: 13.0 },
          SMS: { name: "유해/자극 안전", survey: 80.0, actual: 20.0, gap: 60.0 },
          UAS: { name: "사용자 주도성", survey: 55.0, actual: 31.0, gap: 24.0 }
        },
        misconception: {
          index: 42.5,
          worst_axis_code: "SMS",
          worst_axis_name: "유해/자극 안전",
          worst_gap_value: 60.0,
          message: "주관적으로 생각했던 소비 양상과 실제 데이터 상의 '유해/자극 안전' 영역(쇼츠, 자극성 썸네일 노출) 사이에 큰 인지 편차가 감지되었습니다."
        }
      });
      setLoading(false);
    }, 1000);
  }, [runId]);

  if (loading) {
    return (
      <div className="min-height-screen bg-slate-950 flex flex-col items-center justify-center text-white">
        <span className="animate-spin text-3xl mb-4">🌀</span>
        <p className="text-slate-400 font-semibold">데이터 분석 결과 구성 중...</p>
      </div>
    );
  }

  // Formatting chart data
  const chartData = Object.keys(data.meta_gap).map(key => ({
    subject: data.meta_gap[key].name,
    "주관적_인식": data.meta_gap[key].survey,
    "실제_분석값": data.meta_gap[key].actual
  }));

  // Signal Light (Traffic light) based on bias risk score
  const getSignalColor = (score: number) => {
    if (score < 20) return { bg: "bg-emerald-500", text: "text-emerald-400", label: "안전 (Clean)" };
    if (score < 40) return { bg: "bg-green-500", text: "text-green-400", label: "양호 (Mild)" };
    if (score < 60) return { bg: "bg-yellow-500", text: "text-yellow-400", label: "주의 (Warning)" };
    if (score < 80) return { bg: "bg-orange-500", text: "text-orange-400", label: "경고 (Danger)" };
    return { bg: "bg-red-500", text: "text-red-400", label: "위험 (Critical)" };
  };

  const signal = getSignalColor(data.bias_risk_score);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-body">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Navbar */}
        <div className="flex justify-between items-center border-b border-slate-900 pb-6">
          <div>
            <h1 className="text-2xl font-extrabold text-white font-heading tracking-tight">SH.SON_UNBELIEVABLE</h1>
            <p className="text-xs text-slate-400">데이터 기반 디지털 콘텐츠 성향 모니터링 리포트</p>
          </div>
          <button 
            onClick={() => router.push("/mission?plan_id=prototype-plan-id")}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-purple-500/20"
          >
            🎯 디톡스 미션 센터 진입
          </button>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Left Block: Signal & MBTI Card */}
          <div className="space-y-6 md:col-span-1">
            
            {/* 5-Level Signal Card */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden backdrop-blur-md">
              <h3 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-4">종합 편향 위험도</h3>
              <div className="flex items-center gap-4">
                <div className={`w-6 h-6 rounded-full ${signal.bg} animate-pulse shadow-[0_0_20px_rgba(239,68,68,0.5)]`} />
                <div>
                  <div className="text-3xl font-extrabold text-white">{data.bias_risk_score}점</div>
                  <div className={`text-sm font-bold mt-1 ${signal.text}`}>{signal.label}</div>
                </div>
              </div>
              <p className="text-xs text-slate-400 mt-4 leading-relaxed">전체 6축 인지 지표의 가중합을 계산한 결과 귀하의 뇌는 현재 상당 부분 알고리즘 수동 노출로 인해 편향성이 임계치에 도달했습니다.</p>
            </div>

            {/* 16-Type MBTI Card */}
            <div className="bg-gradient-to-br from-purple-900/30 to-indigo-900/20 border border-slate-800 rounded-3xl p-6 shadow-2xl backdrop-blur-md relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full blur-2xl" />
              <h3 className="text-xs uppercase tracking-wider text-purple-400 font-semibold mb-4">미디어 소비성향 유형 (소비 MBTI)</h3>
              <h2 className="text-2xl font-black text-white font-heading tracking-tight">{data.mbti.name}</h2>
              <div className="flex flex-wrap gap-2 mt-4">
                {data.mbti.tags.map((t: string) => (
                  <span key={t} className="text-[10px] bg-purple-500/10 text-purple-300 px-3 py-1 rounded-full border border-purple-500/20 font-semibold">
                    {t}
                  </span>
                ))}
              </div>
              <p className="text-xs text-slate-400 mt-4 leading-relaxed">주제 다양성과 자극 민감도를 조합하여 판정한 결과, 알고리즘 피드를 타고 자극적인 도파민 콘텐츠만 맹목적으로 찾아다니는 성향이 뚜렷하게 관찰되었습니다.</p>
            </div>
            
          </div>

          {/* Right Block: Overlay Radar Chart (Meta-gap) */}
          <div className="md:col-span-2">
            <RadarChart data={chartData} />
          </div>

        </div>

        {/* [NEW] 자가진단 vs 실제 데이터 분석 DSAO 비교 카드 및 메타인지 갭 */}
        {selfSurvey && data.actual_dsao && (
          <div className="bg-slate-900/20 border border-slate-800/80 rounded-3xl p-6 md:p-8 backdrop-blur-md shadow-2xl space-y-6">
            <div className="flex items-center gap-3 mb-2 border-b border-slate-900 pb-4">
              <span className="text-xl">📊</span>
              <div>
                <h2 className="text-lg font-bold text-white font-heading">자가진단과 실제 분석 비교 및 메타인지 갭</h2>
                <p className="text-xs text-slate-400">스스로 응답했던 자가진단(주관)과 YouTube 시청기록 분석(객관)의 동일 DSAO 지표 대조군입니다.</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* 주관적 자가진단 DSAO */}
              <div className="bg-slate-950/40 border border-slate-850 p-5 rounded-2xl relative">
                <span className="absolute top-4 right-4 text-[9px] uppercase font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded">
                  자가 주관 진단
                </span>
                <h3 className="text-xs text-slate-500 font-bold uppercase tracking-wider">주관 인식 코드</h3>
                <h4 className="text-3xl font-black text-white mt-1 font-heading tracking-tight">{selfSurvey.resultCode}</h4>
                <h5 className="text-sm font-bold text-slate-350 mt-0.5">{selfSurvey.resultName}</h5>
                
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
              <div className="bg-slate-950/40 border border-slate-850 p-5 rounded-2xl relative">
                <span className="absolute top-4 right-4 text-[9px] uppercase font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2 py-0.5 rounded">
                  실제 데이터 측정
                </span>
                <h3 className="text-xs text-slate-500 font-bold uppercase tracking-wider">실제 분석 코드</h3>
                <h4 className="text-3xl font-black text-white mt-1 font-heading tracking-tight">{data.actual_dsao.code}</h4>
                <h5 className="text-sm font-bold text-slate-350 mt-0.5">{data.actual_dsao.name}</h5>
                
                <div className="mt-4 space-y-2 text-xs text-slate-400">
                  <div className="flex justify-between border-b border-slate-900 pb-1.5">
                    <span>1. 탐색 방식:</span>
                    <span className="font-semibold text-slate-200">{data.actual_dsao.code.includes("D") ? "직접 운전형 (D)" : "추천 탑승형 (P)"}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-900 pb-1.5">
                    <span>2. 관심 범위:</span>
                    <span className="font-semibold text-slate-200">{data.actual_dsao.code.includes("W") ? "폭넓은 탐색형 (W)" : "집중 몰입형 (N)"}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-900 pb-1.5">
                    <span>3. 자극 성향:</span>
                    <span className="font-semibold text-slate-200">{data.actual_dsao.code.includes("M") ? "안정 정보형 (M)" : "고자극 반응형 (S)"}</span>
                  </div>
                  <div className="flex justify-between pb-0.5">
                    <span>4. 시청 호흡:</span>
                    <span className="font-semibold text-slate-200">{data.actual_dsao.code.includes("L") ? "롱폼 몰입형 (L)" : "숏폼 속도형 (F)"}</span>
                  </div>
                </div>
              </div>

            </div>

            {/* Meta-gap comparison text summary */}
            <div className="bg-slate-950/20 border border-slate-850 rounded-2xl p-5">
              <div className="flex items-start gap-3">
                <span className="text-lg text-purple-400">💡</span>
                <div className="space-y-1">
                  <h4 className="text-xs font-bold text-slate-350">메타인지 인지 부조화 경향성 리포트</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {selfSurvey.resultCode === data.actual_dsao.code 
                      ? `귀하가 생각한 성향(${selfSurvey.resultCode})과 실제 시청 기록 데이터 분석 성향이 정확히 일치합니다! 자신의 미디어 소비 패턴에 대해 우수한 메타인지를 유지하고 계십니다.`
                      : `귀하의 주관적 성향 인식([${selfSurvey.resultName}])과 실제 시청 데이터 측정 유형([${data.actual_dsao.name}]) 사이에 격차가 존재합니다. 추천 엔진 노출 비중 및 시청 호흡에서 자기도 모르게 알고리즘 수동 선택의 비중이 컸음을 의미하는 '메타인지 갭' 상태입니다.`}
                  </p>
                </div>
              </div>
            </div>

          </div>
        )}

        {/* 6-Axis Scores List */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {Object.keys(data.meta_gap).map(key => {
            const axis = data.meta_gap[key];
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
                    <span>주관적 예측</span>
                    <span>{axis.survey}점</span>
                  </div>
                  <div className="flex justify-between text-xs text-slate-300 font-bold">
                    <span>실제 측정값</span>
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
      <div className="min-height-screen bg-slate-950 flex flex-col items-center justify-center text-white">
        <span className="animate-spin text-3xl mb-4">🌀</span>
        <p className="text-slate-400 font-semibold">데이터 분석 결과 구성 중...</p>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}
