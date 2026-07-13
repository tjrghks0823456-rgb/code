"use client";

import React, { Suspense, useEffect, useMemo, useState } from "react";
import { ArrowLeft, BarChart3, CheckCircle2, Copy, FileUp, RefreshCcw, Target } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "../../components/Button";
import Card from "../../components/Card";
import MissionCard from "../../components/MissionCard";
import PageShell from "../../components/PageShell";
import SectionTitle from "../../components/SectionTitle";
import { DEFAULT_USER_ID, apiUrl } from "../../utils/apiConfig";

const DEMO_PLAN = {
  active: true,
  plan_id: "demo",
  reverse_queries: [
    { query_text: "관심 주제 반대 관점", expected_topic: "균형", why_this_helps: "최근 반복해서 본 주제의 반대 자료를 직접 찾아 추천 흐름을 잠시 끊습니다." },
    { query_text: "긴 영상 다큐 추천", expected_topic: "롱폼", why_this_helps: "짧은 영상 반복 소비를 줄이고 긴 호흡의 콘텐츠를 선택하는 연습입니다." },
    { query_text: "기초 설명 강의", expected_topic: "학습", why_this_helps: "자극적인 제목보다 차분한 설명형 콘텐츠를 직접 선택합니다." },
  ],
  missions: [
    {
      id: "m-1",
      title: "추천 피드 대신 직접 검색 3회 하기",
      description: "오늘은 홈 피드에서 고르지 말고, 보고 싶은 주제를 직접 검색해서 영상 3개를 선택해 보세요.",
      success_condition: "직접 검색 3회",
      effort_level: "low",
      input_type: "choice",
      choices: ["스포츠", "학습", "IT", "뉴스"],
      completed: false,
      log_id: "log-1",
    },
    {
      id: "m-2",
      title: "숏츠 10분 쉬고 롱폼 하나 보기",
      description: "짧은 영상 연속 소비를 멈추고 10분 이상 길이의 영상을 하나 골라 봅니다.",
      success_condition: "롱폼 1개 시청",
      effort_level: "low",
      input_type: "text",
      completed: false,
      log_id: "log-2",
    },
    {
      id: "m-3",
      title: "관심사 맵에 없는 주제 하나 선택",
      description: "검색/시청 맵에 거의 나오지 않은 주제를 하나 골라 새로운 관심사 창을 열어봅니다.",
      success_condition: "새 주제 1개 선택",
      effort_level: "low",
      input_type: "choice",
      choices: ["역사", "운동", "요리", "음악"],
      completed: false,
      log_id: "log-3",
    },
  ],
};

function MissionContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const planId = searchParams.get("plan_id");
  const isDemo = searchParams.get("demo") === "true";

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [inputs, setInputs] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isDemo) {
      setData(DEMO_PLAN);
      setLoading(false);
      return;
    }

    const fetchPlan = async () => {
      try {
        const url = planId
          ? apiUrl(`/api/v1/detox/plan?plan_id=${planId}&user_id=${DEFAULT_USER_ID}`)
          : apiUrl(`/api/v1/detox/plan?user_id=${DEFAULT_USER_ID}`);

        const res = await fetch(url);
        if (!res.ok) {
          const errorText = await res.text();
          let detail = `HTTP ${res.status}`;
          try {
            detail = JSON.parse(errorText).detail || detail;
          } catch (_) {}
          throw new Error(detail);
        }

        const json = await res.json();
        if (json.active) {
          setData(json);
        } else {
          setFetchError("활성화된 미션 플랜이 없습니다. 대시보드에서 먼저 미션을 생성해 주세요.");
        }
      } catch (err: any) {
        console.error("Mission plan fetch failed:", err);
        setFetchError(err.message?.includes("fetch") ? `API 서버(${apiUrl("/")})에 연결할 수 없습니다.` : `미션 조회 실패: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchPlan();
  }, [planId, isDemo]);

  const completedCount = useMemo(() => {
    if (!data?.missions) return 0;
    return data.missions.filter((mission: any) => mission.completed).length;
  }, [data]);

  const progressPercent = data?.missions?.length ? Math.round((completedCount / data.missions.length) * 100) : 0;

  const toggleMission = async (index: number, selectedInput?: string) => {
    if (!data) return;
    const targetMission = data.missions[index];
    const newStatus = selectedInput ? true : !targetMission.completed;

    const updatedMissions = [...data.missions];
    updatedMissions[index] = { ...targetMission, completed: newStatus };
    setData({ ...data, missions: updatedMissions });

    if (!isDemo) {
      try {
        await fetch(apiUrl(`/api/v1/detox/mission/${targetMission.log_id}`), {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ completed: newStatus }),
        });
      } catch (err) {
        console.warn("Failed to patch mission status to backend.", err);
      }
    }
  };

  const handleTextSubmit = (index: number) => {
    const targetMission = data.missions[index];
    const textVal = inputs[targetMission.id];
    if (!textVal?.trim()) return;
    toggleMission(index, textVal);
  };

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 1500);
  };

  const goDashboard = () => {
    const cachedRunId = typeof window !== "undefined" ? localStorage.getItem("latest_run_id") : null;
    router.push(cachedRunId ? `/dashboard?run_id=${cachedRunId}` : "/dashboard");
  };

  if (loading) {
    return (
      <PageShell active="mission" compact>
        <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
          <div className="mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-950" />
          <p className="font-bold text-slate-600">오늘 실행할 디톡스 미션을 준비하는 중입니다.</p>
        </div>
      </PageShell>
    );
  }

  if (fetchError) {
    return (
      <PageShell active="mission" compact>
        <Card className="mx-auto max-w-lg p-8 text-center">
          <Target className="mx-auto text-teal-700" size={40} />
          <h1 className="mt-4 text-2xl font-black text-slate-950">미션 플랜을 불러오지 못했습니다</h1>
          <p className="mt-4 rounded-2xl bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{fetchError}</p>
          <div className="mt-5 flex flex-col gap-3">
            <Button type="button" onClick={goDashboard}>대시보드로 돌아가기</Button>
            <Button type="button" tone="secondary" onClick={() => router.push("/mission?demo=true")}>예시 미션 보기</Button>
          </div>
        </Card>
      </PageShell>
    );
  }

  return (
    <PageShell active="mission">
      <div className="space-y-8">
        {isDemo && (
          <div className="rounded-3xl border border-amber-200 bg-amber-50 px-5 py-4 text-sm font-semibold text-amber-800">
            예시 데이터로 보여주는 화면입니다. 실제 분석 후에는 나의 결과에 맞춘 미션이 생성됩니다.
          </div>
        )}

        <section className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-stretch">
          <Card className="p-6 md:p-7">
            <SectionTitle
              eyebrow="detox mission"
              title="미션은 결과를 바꾸는 실험입니다"
              description="완료 체크 자체보다, 미션 이후 다시 분석했을 때 위험도와 관심사 균형이 어떻게 바뀌는지가 핵심입니다."
            />
            <div className="mt-6 grid gap-3 sm:grid-cols-3">
              {[
                { label: "미션 전", desc: "현재 분석 결과 저장", icon: BarChart3 },
                { label: "미션 수행", desc: "검색/시청 습관 조정", icon: Target },
                { label: "미션 후", desc: "다시 업로드해 비교", icon: RefreshCcw },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.label} className="rounded-2xl border border-slate-200 bg-[#fbfaf7] p-4">
                    <Icon size={18} className="text-teal-700" />
                    <p className="mt-3 text-sm font-black text-slate-950">{item.label}</p>
                    <p className="mt-1 text-xs font-bold leading-5 text-slate-500">{item.desc}</p>
                  </div>
                );
              })}
            </div>
          </Card>

          <Card className="p-6 md:p-7">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-700">progress</p>
                <h2 className="mt-2 text-3xl font-black text-slate-950">오늘의 진행률 {progressPercent}%</h2>
              </div>
              <CheckCircle2 className="text-teal-700" size={34} />
            </div>
            <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-teal-600 transition-all" style={{ width: `${progressPercent}%` }} />
            </div>
            <div className="mt-5 flex flex-col gap-3 sm:flex-row">
              <Button type="button" tone="secondary" icon={<ArrowLeft size={18} />} onClick={goDashboard}>
                결과로 돌아가기
              </Button>
              <Button type="button" icon={<FileUp size={18} />} onClick={() => router.push("/upload")}>
                미션 후 다시 분석
              </Button>
            </div>
          </Card>
        </section>

        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <Card className="p-6">
            <h2 className="text-xl font-black text-slate-950">직접 검색 미션</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              추천 피드가 보여주는 흐름을 잠시 멈추고, 내가 직접 고른 검색어로 콘텐츠를 선택합니다.
            </p>
            <div className="mt-5 space-y-3">
              {data.reverse_queries.map((item: any, index: number) => (
                <div key={`${item.query_text}-${index}`} className="rounded-3xl border border-slate-200 bg-[#fbfaf7] p-4">
                  <p className="text-xs font-black uppercase tracking-[0.16em] text-slate-400">검색어 {index + 1}</p>
                  <h3 className="mt-2 text-base font-black text-slate-950">{item.query_text}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{item.why_this_helps}</p>
                  <div className="mt-4 flex gap-2">
                    <Button
                      type="button"
                      tone="secondary"
                      className="flex-1 text-[11px]"
                      icon={<Copy size={15} />}
                      onClick={() => copyToClipboard(item.query_text, index)}
                    >
                      {copiedIndex === index ? "복사 완료" : "검색어 복사"}
                    </Button>
                    <a
                      href={`https://www.youtube.com/results?search_query=${encodeURIComponent(item.query_text)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex min-h-11 flex-1 items-center justify-center gap-1.5 rounded-2xl bg-teal-600 text-[11px] font-black text-white shadow-sm transition hover:bg-teal-700"
                    >
                      YouTube 검색
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <div className="space-y-4">
            {data.missions.map((mission: any, index: number) => {
              const isChoice = mission.input_type === "choice";
              const isText = mission.input_type === "text";

              return (
                <MissionCard
                  key={mission.id}
                  title={mission.title}
                  description={mission.description}
                  label={`미션 ${index + 1}`}
                  completed={mission.completed}
                  onToggle={!isChoice && !isText ? () => toggleMission(index) : undefined}
                >
                  {!mission.completed && isChoice && mission.choices && (
                    <div className="flex flex-wrap gap-2">
                      {mission.choices.map((choice: string) => (
                        <button
                          key={choice}
                          type="button"
                          onClick={() => {
                            setInputs((prev) => ({ ...prev, [mission.id]: choice }));
                            toggleMission(index, choice);
                          }}
                          className="rounded-2xl border border-slate-200 bg-[#fbfaf7] px-3 py-2 text-xs font-bold text-slate-700 transition hover:border-slate-400"
                        >
                          {choice}
                        </button>
                      ))}
                    </div>
                  )}

                  {!mission.completed && isText && (
                    <div className="flex flex-col gap-2 sm:flex-row">
                      <input
                        type="text"
                        value={inputs[mission.id] || ""}
                        onChange={(e) => setInputs((prev) => ({ ...prev, [mission.id]: e.target.value }))}
                        placeholder="오늘 시도한 내용을 한 줄로 적어주세요"
                        className="min-h-11 flex-1 rounded-2xl border border-slate-200 bg-[#fbfaf7] px-4 text-sm font-semibold text-slate-700 outline-none focus:border-slate-500"
                      />
                      <Button type="button" tone="secondary" onClick={() => handleTextSubmit(index)}>
                        기록하기
                      </Button>
                    </div>
                  )}
                </MissionCard>
              );
            })}
          </div>
        </div>
      </div>
    </PageShell>
  );
}

export default function MissionPage() {
  return (
    <Suspense fallback={
      <PageShell active="mission" compact>
        <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
          <div className="mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-950" />
          <p className="font-bold text-slate-600">미션 데이터를 준비하는 중입니다.</p>
        </div>
      </PageShell>
    }>
      <MissionContent />
    </Suspense>
  );
}
