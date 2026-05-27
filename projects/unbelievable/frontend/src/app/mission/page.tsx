"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

function MissionContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const planId = searchParams.get("plan_id") || "mvp-active-plan";

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [apiError, setApiError] = useState(false);
  const [inputs, setInputs] = useState<Record<string, string>>({});

  useEffect(() => {
    // Attempt to fetch from local FastAPI backend
    const fetchPlan = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/v1/detox/plan?user_id=00000000-0000-0000-0000-000000000001");
        if (res.ok) {
          const json = await res.json();
          if (json.active) {
            setData(json);
            setLoading(false);
            return;
          }
        }
      } catch (err) {
        console.warn("Backend server not running or connection failed. Using high-fidelity mock fallback.");
        setApiError(true);
      }

      // High-Fidelity Mock fallback using the aligned lightweight low-barrier schema
      setTimeout(() => {
        setData({
          active: true,
          plan_id: planId,
          reverse_queries: [
            { query_text: "역사 및 세계사 핵심 정리 다큐", expected_topic: "History", why_this_helps: "IT 및 정보 위주의 관심사에서 인문학 교양으로 영역을 다양하게 넓혀 줍니다." },
            { query_text: "현대 미술 쉽게 감상하는 법", expected_topic: "Arts", why_this_helps: "새로운 시각적 자극과 예술적 뇌 영역을 활성화시킵니다." },
            { query_text: "미디어 소비 조절과 디지털 웰빙", expected_topic: "Lifestyle", why_this_helps: "수동적 추천 노출에서 주체적인 사용 패턴 개선 방향을 직접 인지하도록 돕습니다." }
          ],
          missions: [
            {
              id: "m-1",
              title: "영상 재생 전 '클릭 의도' 멈춤 및 선택",
              description: "영상을 클릭하여 시청하기 전, 내가 이 영상을 왜 누르는지 이유를 가볍게 골라보세요.",
              success_condition: "선택 즉시 완료",
              effort_level: "low",
              input_type: "choice",
              choices: ["정보 습득", "오락 및 기분전환", "무의식적 습관", "심심함"],
              completed: false,
              log_id: "log-1"
            },
            {
              id: "m-2",
              title: "오늘 본 최선/최악의 제목 한 줄 남기기",
              description: "오늘 본 콘텐츠 중 가장 가치 있었던 영상 제목이나 가장 호기심만 유도했던 낚시성 제목 하나를 적어보세요.",
              success_condition: "한 줄 작성 시 완료",
              effort_level: "low",
              input_type: "text",
              completed: false,
              log_id: "log-2"
            },
            {
              id: "m-3",
              title: "낯선 카테고리 하나 구경하기",
              description: "평소 전혀 보지 않던 '교양/다큐' 섹션 영상을 하나 클릭하고 무엇에 관한 것인지 확인해 보세요.",
              success_condition: "선택만 하면 완료",
              effort_level: "low",
              input_type: "choice",
              choices: ["역사/문학", "예술/디자인", "우주/자연과학", "경제/비즈니스"],
              completed: false,
              log_id: "log-3"
            }
          ]
        });
        setLoading(false);
      }, 1000);
    };

    fetchPlan();
  }, [planId]);

  const toggleMission = async (index: number, selectedInput?: string) => {
    if (!data) return;

    const targetMission = data.missions[index];
    const newStatus = selectedInput ? true : !targetMission.completed;

    // Optimistic Update
    const updatedMissions = [...data.missions];
    updatedMissions[index] = { ...targetMission, completed: newStatus };
    setData({ ...data, missions: updatedMissions });

    // Try PATCH API request if backend is alive
    try {
      await fetch(`http://localhost:8000/api/v1/detox/mission/${targetMission.log_id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ completed: newStatus })
      });
    } catch (err) {
      console.warn("Failed to patch mission status to backend, running on local offline state.");
    }
  };

  const handleTextSubmit = (index: number) => {
    const targetMission = data.missions[index];
    const textVal = inputs[targetMission.id];
    if (!textVal || !textVal.trim()) return;
    
    toggleMission(index, textVal);
  };

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 1500);
  };

  if (loading) {
    return (
      <div className="min-height-screen bg-slate-950 flex flex-col items-center justify-center text-white">
        <span className="animate-spin text-3xl mb-4">⏳</span>
        <p className="text-slate-400 font-semibold">추천 디톡스 루틴 설계안 구성 중...</p>
      </div>
    );
  }

  // Progress computation
  const completedCount = data.missions.filter((m: any) => m.completed).length;
  const progressPercent = Math.round((completedCount / data.missions.length) * 100);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-body">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Top Navbar */}
        <div className="flex justify-between items-center border-b border-slate-900 pb-6">
          <div>
            <h1 className="text-2xl font-extrabold text-white font-heading tracking-tight">🎯 DETOX MISSION CENTER</h1>
            <p className="text-xs text-slate-400">의식적인 균형 시청을 돕는 대체 키워드 및 행동 설계 루틴 본부</p>
          </div>
          <button 
            onClick={() => router.push("/dashboard")}
            className="px-5 py-2.5 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-350 hover:text-white font-bold rounded-xl transition-all text-xs"
          >
            ← 대시보드로 복귀
          </button>
        </div>

        {/* Dashboard layout */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Left Panel: Reverse Query Prescriptions */}
          <div className="md:col-span-1 space-y-6">
            <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-2xl backdrop-blur-md relative overflow-hidden">
              <div className="absolute top-0 right-0 w-20 h-20 bg-purple-500/5 rounded-full blur-2xl" />
              <h3 className="text-sm font-bold text-white mb-1">🔄 대안 키워드 추천 (Reverse Query)</h3>
              <p className="text-xs text-slate-400 mb-6 leading-relaxed">
                평소 시청 이력에서 노출이 적었던 분야의 테마를 도출한 추천 검색어 세트입니다. 해당 키워드를 유튜브 검색창에 직접 입력하여 시청하는 적극적인 정보 탐색을 권장합니다.
              </p>

              <div className="space-y-4">
                {data.reverse_queries.map((item: any, idx: number) => (
                  <div key={idx} className="bg-slate-950/60 border border-slate-850 p-4 rounded-2xl relative group hover:border-purple-500/30 transition-all">
                    <span className="text-[10px] uppercase font-bold text-purple-400 tracking-wider">대안 검색어 {idx + 1}</span>
                    <h4 className="text-sm font-bold text-white mt-1 break-words">{item.query_text}</h4>
                    <p className="text-[10px] text-slate-500 mt-1">{item.why_this_helps}</p>
                    
                    <button 
                      onClick={() => copyToClipboard(item.query_text, idx)}
                      className="mt-3 w-full py-1.5 bg-slate-900 hover:bg-slate-850 border border-slate-800 text-[10px] font-bold text-slate-300 hover:text-white rounded-lg transition-all flex items-center justify-center gap-1.5"
                    >
                      {copiedIndex === idx ? "✓ 복사 완료!" : "📋 텍스트 복사하기"}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Panel: Active Missions & Progress */}
          <div className="md:col-span-2 space-y-6">
            
            {/* Progress Card */}
            <div className="bg-gradient-to-r from-purple-950/20 to-indigo-950/20 border border-slate-800 rounded-3xl p-6 shadow-2xl backdrop-blur-md relative overflow-hidden">
              <div className="flex justify-between items-center mb-3">
                <div>
                  <h3 className="text-xs uppercase tracking-wider text-purple-400 font-semibold">현재 추천 루틴 진척도</h3>
                  <h2 className="text-2xl font-black text-white mt-0.5">{progressPercent}% 달성</h2>
                </div>
                <div className="text-3xl">🔋</div>
              </div>
              
              {/* HTML Progress Bar */}
              <div className="w-full bg-slate-900 rounded-full h-3 overflow-hidden border border-slate-800">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-indigo-500 h-full rounded-full transition-all duration-500 ease-out shadow-[0_0_10px_rgba(168,85,247,0.5)]"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <p className="text-xs text-slate-400 mt-3 leading-relaxed font-body">
                의무적인 인증 강제가 아닌, 클릭 전 잠시 멈춤을 갖거나 짧은 자기 성찰 기록을 통해 추천 알고리즘의 노출 흐름을 주체적으로 이끌어가는 메타인지 복원 과정입니다.
              </p>
            </div>

            {/* Mission Checklists */}
            <div className="space-y-4">
              {data.missions.map((mission: any, idx: number) => {
                const isChoice = mission.input_type === "choice";
                const isText = mission.input_type === "text";
                
                return (
                  <div 
                    key={mission.id}
                    className={`border rounded-2xl p-6 transition-all duration-350 flex flex-col gap-4 select-none ${
                      mission.completed 
                        ? "bg-purple-950/10 border-purple-500/40 shadow-[0_0_15px_rgba(168,85,247,0.05)]" 
                        : "bg-slate-900/30 border-slate-800 hover:border-slate-700/80 hover:bg-slate-900/40"
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      {/* Interactive custom action status indicator */}
                      <div 
                        onClick={() => !isChoice && !isText && toggleMission(idx)}
                        className={`w-6 h-6 rounded-lg border-2 flex items-center justify-center text-xs transition-all ${
                          !isChoice && !isText ? "cursor-pointer" : ""
                        } ${
                          mission.completed 
                            ? "bg-purple-600 border-purple-500 text-white" 
                            : "border-slate-700 text-transparent"
                        }`}
                      >
                        ✓
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex justify-between items-center gap-2">
                          <h4 className={`text-base font-bold transition-all ${mission.completed ? "text-slate-400 line-through" : "text-white"}`}>
                            {mission.title}
                          </h4>
                          <span className="text-[9px] font-semibold uppercase tracking-wider text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded shrink-0">
                            가벼운 미션 {idx + 1}
                          </span>
                        </div>
                        <p className={`text-xs mt-1.5 leading-relaxed transition-all ${mission.completed ? "text-slate-500" : "text-slate-400"}`}>
                          {mission.description}
                        </p>
                      </div>
                    </div>

                    {/* Aligned Lightweight Interactive Forms (No forced capture verification) */}
                    {!mission.completed && (
                      <div className="mt-2 pl-10 border-l border-slate-850 space-y-3">
                        {isChoice && mission.choices && (
                          <div className="flex flex-wrap gap-2">
                            {mission.choices.map((choice: string) => (
                              <button
                                key={choice}
                                onClick={() => {
                                  setInputs(prev => ({ ...prev, [mission.id]: choice }));
                                  toggleMission(idx, choice);
                                }}
                                className="px-3.5 py-1.5 bg-slate-950 hover:bg-purple-950/20 border border-slate-800 hover:border-purple-500/50 rounded-xl text-xs text-slate-355 hover:text-purple-300 font-medium transition-all"
                              >
                                {choice}
                              </button>
                            ))}
                          </div>
                        )}

                        {isText && (
                          <div className="flex gap-2 max-w-md">
                            <input
                              type="text"
                              value={inputs[mission.id] || ""}
                              onChange={(e) => setInputs(prev => ({ ...prev, [mission.id]: e.target.value }))}
                              placeholder="가벼운 성찰 소감을 입력해 보세요 (예: 생각 환기 완료)"
                              className="flex-1 bg-slate-950 border border-slate-850 rounded-xl px-3.5 py-2 text-xs text-slate-300 focus:outline-none focus:border-purple-500/50"
                            />
                            <button
                              onClick={() => handleTextSubmit(idx)}
                              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-300 hover:text-white rounded-xl transition-all"
                            >
                              한 줄 남기기
                            </button>
                          </div>
                        )}
                      </div>
                    )}

                    {mission.completed && (isChoice || isText) && (
                      <div className="mt-1 pl-10 text-[10px] text-emerald-400 font-semibold flex items-center gap-1.5">
                        <span>✓</span> 자율적 체크 기록 완료
                        {inputs[mission.id] && (
                          <span className="text-slate-500 font-normal">({inputs[mission.id]})</span>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Re-analyze CTA */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 text-center space-y-4 backdrop-blur-md">
              <h4 className="text-sm font-bold text-white">행동을 무사히 관찰해 보셨나요?</h4>
              <p className="text-xs text-slate-400 max-w-lg mx-auto leading-relaxed">
                가벼운 미션과 대안 추천 검색어 시청을 며칠간 이행한 뒤, 다시 새로운 YouTube 데이터를 추출하여 재분석을 트리거하면, 이전 분석 결과 대비 변화 추이를 관찰해 볼 수 있습니다.
              </p>
              <button 
                onClick={() => router.push("/upload")}
                className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-emerald-500/10 inline-flex items-center gap-1.5 text-xs"
              >
                🔄 루틴 적용 후 새로운 시청기록 대조하기
              </button>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
}

export default function MissionPage() {
  return (
    <Suspense fallback={
      <div className="min-height-screen bg-slate-950 flex flex-col items-center justify-center text-white">
        <span className="animate-spin text-3xl mb-4">⏳</span>
        <p className="text-slate-400 font-semibold">추천 디톡스 루틴 설계안 구성 중...</p>
      </div>
    }>
      <MissionContent />
    </Suspense>
  );
}
