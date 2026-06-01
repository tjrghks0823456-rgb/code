"use client";

import React, { Suspense, useEffect, useState } from "react";
import { ArrowLeft, Copy, RefreshCcw } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "../../components/Button";
import Card from "../../components/Card";
import MissionCard from "../../components/MissionCard";
import PageShell from "../../components/PageShell";
import SectionTitle from "../../components/SectionTitle";

const DEMO_PLAN = {
  active: true,
  plan_id: "demo",
  reverse_queries: [
    { query_text: "쇼츠 줄이기", expected_topic: "휴식", why_this_helps: "짧은 추천 흐름을 잠깐 끊고 시청 속도를 늦추는 데 도움이 됩니다." },
    { query_text: "긴 영상 추천", expected_topic: "롱폼", why_this_helps: "짧은 추천 흐름을 끊고 맥락을 천천히 따라갈 수 있습니다." },
    { query_text: "디지털 휴식 루틴", expected_topic: "웰빙", why_this_helps: "내 알고리즘에 새 창을 열어 관심사 폭을 조금 넓혀줍니다." }
  ],
  missions: [
    {
      id: "m-1",
      title: "같은 이슈, 다른 제목 비교하기",
      description: "최근 많이 본 주제 하나를 골라 제목이 다른 영상 두 개를 비교해보세요.",
      success_condition: "비교 후 완료",
      effort_level: "low",
      input_type: "choice",
      choices: ["뉴스", "스포츠", "IT", "엔터"],
      completed: false,
      log_id: "log-1"
    },
    {
      id: "m-2",
      title: "오늘 본 영상 한 줄로 남기기",
      description: "기억에 남은 영상 하나를 고르고 왜 눌렀는지 한 줄만 적어보세요.",
      success_condition: "한 줄 작성",
      effort_level: "low",
      input_type: "text",
      completed: false,
      log_id: "log-2"
    },
    {
      id: "m-3",
      title: "추천 영상 말고 직접 검색해서 하나 고르기",
      description: "피드가 보여준 영상 대신 검색창에 새 키워드 하나를 입력해 직접 선택해보세요.",
      success_condition: "검색 후 선택",
      effort_level: "low",
      input_type: "choice",
      choices: ["교양", "음악", "운동", "학습"],
      completed: false,
      log_id: "log-3"
    }
  ]
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
          ? `http://localhost:8000/api/v1/detox/plan?plan_id=${planId}&user_id=00000000-0000-0000-0000-000000000001`
          : `http://localhost:8000/api/v1/detox/plan?user_id=00000000-0000-0000-0000-000000000001`;

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
          setFetchError("현재 활성화된 미션 플랜이 없습니다. 대시보드에서 미션을 먼저 생성해주세요.");
        }
      } catch (err: any) {
        console.error("Mission plan fetch failed:", err);
        setFetchError(err.message?.includes("fetch") ? "FastAPI 서버에 연결할 수 없습니다." : `플랜 조회 실패: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchPlan();
  }, [planId, isDemo]);

  const toggleMission = async (index: number, selectedInput?: string) => {
    if (!data) return;
    const targetMission = data.missions[index];
    const newStatus = selectedInput ? true : !targetMission.completed;

    const updatedMissions = [...data.missions];
    updatedMissions[index] = { ...targetMission, completed: newStatus };
    setData({ ...data, missions: updatedMissions });

    if (!isDemo) {
      try {
        await fetch(`http://localhost:8000/api/v1/detox/mission/${targetMission.log_id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ completed: newStatus })
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

  if (loading) {
    return (
      <PageShell active="mission" compact>
        <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
          <div className="mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-950" />
          <p className="font-bold text-slate-600">오늘의 환기 미션을 준비하는 중입니다.</p>
        </div>
      </PageShell>
    );
  }

  if (fetchError) {
    return (
      <PageShell active="mission" compact>
        <Card className="mx-auto max-w-lg p-8 text-center">
          <h1 className="text-2xl font-black text-slate-950">미션 플랜을 불러오지 못했습니다</h1>
          <p className="mt-4 rounded-2xl bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{fetchError}</p>
          <div className="mt-5 flex flex-col gap-3">
            <Button type="button" onClick={() => router.push("/dashboard")}>대시보드로 돌아가기</Button>
            <Button type="button" tone="secondary" onClick={() => router.push("/mission?demo=true")}>예시 미션 보기</Button>
          </div>
        </Card>
      </PageShell>
    );
  }

  const completedCount = data.missions.filter((mission: any) => mission.completed).length;
  const progressPercent = Math.round((completedCount / data.missions.length) * 100);

  return (
    <PageShell active="mission">
      <div className="space-y-8">
        {isDemo && (
          <div className="rounded-3xl border border-amber-200 bg-amber-50 px-5 py-4 text-sm font-semibold text-amber-800">
            예시 데이터로 보여주는 화면입니다. 실제 분석 후에는 맞춤 미션이 생성됩니다.
          </div>
        )}

        <section className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <SectionTitle
            eyebrow="reset mission"
            title="알고리즘 환기 미션"
            description="완료율을 채우는 숙제가 아니라, 추천 흐름에 새 창을 여는 가벼운 루틴입니다."
          />
          <Button type="button" tone="secondary" icon={<ArrowLeft size={18} />} onClick={() => router.push("/dashboard")}>
            대시보드로
          </Button>
        </section>

        <Card className="p-6">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-700">this week</p>
              <h2 className="mt-2 text-3xl font-black text-slate-950">이번 주 균형 회복 {progressPercent}%</h2>
            </div>
            <RefreshCcw className="text-teal-700" size={34} />
          </div>
          <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-100">
            <div className="h-full rounded-full bg-teal-600 transition-all" style={{ width: `${progressPercent}%` }} />
          </div>
        </Card>

        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <Card className="p-6">
            <h2 className="text-xl font-black text-slate-950">새 관점 검색어</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              피드가 보여준 영상 대신 직접 검색해볼 만한 가벼운 키워드입니다.
            </p>
            <div className="mt-5 space-y-3">
              {data.reverse_queries.map((item: any, index: number) => (
                <div key={`${item.query_text}-${index}`} className="rounded-3xl border border-slate-200 bg-[#fbfaf7] p-4">
                  <p className="text-xs font-black uppercase tracking-[0.16em] text-slate-400">검색어 {index + 1}</p>
                  <h3 className="mt-2 text-base font-black text-slate-950">{item.query_text}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{item.why_this_helps}</p>
                  <Button
                    type="button"
                    tone="secondary"
                    className="mt-4 w-full"
                    icon={<Copy size={16} />}
                    onClick={() => copyToClipboard(item.query_text, index)}
                  >
                    {copiedIndex === index ? "복사 완료" : "검색어 복사"}
                  </Button>
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
                  label={`오늘의 환기 ${index + 1}`}
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
                        placeholder="한 줄만 적어도 충분해요"
                        className="min-h-11 flex-1 rounded-2xl border border-slate-200 bg-[#fbfaf7] px-4 text-sm font-semibold text-slate-700 outline-none focus:border-slate-500"
                      />
                      <Button type="button" tone="secondary" onClick={() => handleTextSubmit(index)}>
                        남기기
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
          <p className="font-bold text-slate-600">미션 센터를 준비하는 중입니다.</p>
        </div>
      </PageShell>
    }>
      <MissionContent />
    </Suspense>
  );
}
