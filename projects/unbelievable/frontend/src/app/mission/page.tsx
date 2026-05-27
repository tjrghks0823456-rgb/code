"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

function MissionContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const planId = searchParams.get("plan_id") || "prototype-plan-id";

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [apiError, setApiError] = useState(false);

  useEffect(() => {
    // Attempt to fetch from local FastAPI backend
    const fetchPlan = async () => {
      try {
        const res = await fetch("http://localhost:8000/detox/plan");
        if (res.ok) {
          const json = await res.json();
          if (json.active) {
            setData(json);
            setLoading(false);
            return;
          }
        }
      } catch (err) {
        console.warn("Backend server not running or connection failed. Using high-fidelity mock data.");
        setApiError(true);
      }

      // High-Fidelity Mock fallback for the prototype
      setTimeout(() => {
        setData({
          active: true,
          plan_id: planId,
          reverse_queries: [
            { query: "환경 다큐멘터리 침묵의 봄", desc: "도파민 자극이 없는 고요한 자연 상태 시청 유도" },
            { query: "미시 경제 대공황의 진실", desc: "자극적 뉴스 채널 대신 학술적이고 객관적인 관점 보충" },
            { query: "도파민 디톡스 실천 일지 30일", desc: "미디어 중독 해결을 위한 타인의 성찰 다큐멘터리" }
          ],
          missions: [
            {
              id: "m-1",
              title: "알고리즘 추천 피드 차단하기",
              description: "유튜브 첫 화면의 추천 리스트를 무시하고 오직 상단 검색창에 'Reverse Query'만을 입력하여 수동 시청하세요.",
              completed: false,
              log_id: "log-1"
            },
            {
              id: "m-2",
              title: "쇼츠/짧은 동영상 시청 중단",
              description: "5초 이하의 가짜 도파민 중독을 깨기 위해 오늘 단 하루는 세로형 숏폼(Shorts) 메뉴를 절대 터치하지 마세요.",
              completed: false,
              log_id: "log-2"
            },
            {
              id: "m-3",
              title: "30분 이상 긴 호흡 영상 관람",
              description: "유익한 고전 인문학이나 다큐멘터리 등 호흡이 길고 차분한 영상을 30분 이상 건너뛰지 않고 진득하게 감상하세요.",
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

  const toggleMission = async (index: number) => {
    if (!data) return;

    const targetMission = data.missions[index];
    const newStatus = !targetMission.completed;

    // Optimistic Update
    const updatedMissions = [...data.missions];
    updatedMissions[index] = { ...targetMission, completed: newStatus };
    setData({ ...data, missions: updatedMissions });

    // Try PATCH API request if backend is alive
    if (!apiError) {
      try {
        await fetch(`http://localhost:8000/detox/mission/${targetMission.log_id}`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ completed: newStatus })
        });
      } catch (err) {
        console.warn("Failed to patch mission status to backend, running on prototype offline state.");
      }
    }
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
        <p className="text-slate-400 font-semibold">디톡스 처방 설계안 수집 중...</p>
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
            <p className="text-xs text-slate-400">당신의 알고리즘 노출 정화 및 의식적 뇌 관리 본부</p>
          </div>
          <button 
            onClick={() => router.push("/dashboard")}
            className="px-5 py-2.5 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white font-bold rounded-xl transition-all"
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
              <h3 className="text-sm font-bold text-white mb-1">🔄 Reverse Query 처방</h3>
              <p className="text-xs text-slate-400 mb-6 leading-relaxed">
                당신의 평소 시청 데이터에서 가장 결핍된 주제를 도출하여, 유튜브 추천 피드를 깨뜨릴 대체 검색어 세트입니다. 복사하여 유튜브에 검색해 보세요.
              </p>

              <div className="space-y-4">
                {data.reverse_queries.map((item: any, idx: number) => (
                  <div key={idx} className="bg-slate-950/60 border border-slate-850 p-4 rounded-2xl relative group hover:border-purple-500/30 transition-all">
                    <span className="text-[10px] uppercase font-bold text-purple-400 tracking-wider">대안 검색어 {idx + 1}</span>
                    <h4 className="text-sm font-bold text-white mt-1 break-words">{item.query}</h4>
                    <p className="text-[10px] text-slate-500 mt-1">{item.desc}</p>
                    
                    <button 
                      onClick={() => copyToClipboard(item.query, idx)}
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
                  <h3 className="text-xs uppercase tracking-wider text-purple-400 font-semibold">현재 디톡스 진척도</h3>
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
              <p className="text-xs text-slate-400 mt-3 leading-relaxed">
                모든 행동 강령에 체크하고, 뇌가 자극의 중독 루프에서 탈피할 수 있도록 강인한 메타인지의 통제력을 회복해 나갑니다.
              </p>
            </div>

            {/* Mission Checklists */}
            <div className="space-y-4">
              {data.missions.map((mission: any, idx: number) => (
                <div 
                  key={mission.id}
                  onClick={() => toggleMission(idx)}
                  className={`border rounded-2xl p-6 cursor-pointer transition-all duration-350 flex items-start gap-4 select-none ${
                    mission.completed 
                      ? "bg-purple-950/10 border-purple-500/40 shadow-neon-purple/10" 
                      : "bg-slate-900/30 border-slate-800 hover:border-slate-700/80 hover:bg-slate-900/40"
                  }`}
                >
                  {/* Neon custom checkbox */}
                  <div className={`w-6 h-6 rounded-lg border-2 flex items-center justify-center text-xs transition-all ${
                    mission.completed 
                      ? "bg-purple-600 border-purple-500 text-white shadow-neon-purple" 
                      : "border-slate-700 text-transparent"
                  }`}>
                    ✓
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex justify-between items-center">
                      <h4 className={`text-base font-bold transition-all ${mission.completed ? "text-slate-400 line-through" : "text-white"}`}>
                        {mission.title}
                      </h4>
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded">
                        행동 지침 {idx + 1}
                      </span>
                    </div>
                    <p className={`text-xs mt-1.5 leading-relaxed transition-all ${mission.completed ? "text-slate-500" : "text-slate-400"}`}>
                      {mission.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Re-analyze CTA */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 text-center space-y-4 backdrop-blur-md">
              <h4 className="text-sm font-bold text-white">행동을 무사히 수행하셨나요?</h4>
              <p className="text-xs text-slate-400 max-w-lg mx-auto">
                디톡스 처방 및 추천 검색어 시청을 수일간 이행한 뒤, 다시 새로운 YouTube 기록 파일을 추출하여 재분석을 트리거하면, 예전 분석값 대비 정량적 변화 상태를 보여주는 '추적 시각화 리포트'가 활성화됩니다.
              </p>
              <button 
                onClick={() => router.push("/upload")}
                className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-emerald-500/10 inline-flex items-center gap-1.5"
              >
                🔄 디톡스 적용 후 재분석 파일 제출하기
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
        <p className="text-slate-400 font-semibold">디톡스 처방 설계안 수집 중...</p>
      </div>
    }>
      <MissionContent />
    </Suspense>
  );
}
