"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import RadarChart from "../../components/RadarChart";
import { loadSelfSurveyResult, SelfSurveyResult } from "../../utils/surveyStorage";

const CHARACTER_MAP: Record<string, {
  name: string;
  oneLiner: string;
  tags: string[];
  attention: string;
  recovery: string;
}> = {
  DWSF: {
    name: "도파민 탐험가",
    oneLiner: "자발적으로 다채로운 정보를 개척하지만, 유희적인 숏폼 자극도 유연하게 수용하는 유형입니다.",
    tags: ["#주도적탐색", "#다채로운장르", "#가벼운숏폼"],
    attention: "때로는 목적을 갖고 시작한 검색이 숏폼 추천 리스트로 새어 나가지 않는지 한 번씩 체크해 볼 필요가 있습니다.",
    recovery: "오늘 본 영상 중 가장 기억에 남는 가치 있는 제목 1개만 수첩에 적어 보는 습관을 권장합니다."
  },
  DWSL: {
    name: "마라맛 큐레이터",
    oneLiner: "주도적으로 풍부한 정보원을 발굴하되, 호흡이 길고 강렬한 몰입감 높은 주제들을 탐색하는 경향이 뚜렷한 유형입니다.",
    tags: ["#강렬한몰입", "#주체적아카이빙", "#롱폼선호"],
    attention: "자극적인 시사 논쟁이나 극단적인 대립 영상에 긴 시간 몰입하여 심리적 스트레스를 축적하지 않도록 조심하세요.",
    recovery: "자극이 없는 자연 상태의 고전 인문학이나 다큐멘터리 영상을 하루 1회 감상하는 것을 권장합니다."
  },
  DWMF: {
    name: "지식 스낵 탐색가",
    oneLiner: "자율적으로 지식과 교양을 채굴하며, 바쁜 일상 속에서 주로 컴팩트하게 요약된 스낵 숏폼 비디오를 즐깁니다.",
    tags: ["#지식스낵", "#자율적학습", "#컴팩트소비"],
    attention: "단편화된 지식 요약에 익숙해져 긴 글이나 복잡한 맥락의 지식을 끝까지 탐독하는 호흡이 다소 감소할 수 있습니다.",
    recovery: "20분 이상의 호흡이 긴 전문 지식 강좌나 역사 다큐멘터리 1편을 건너뛰지 않고 진득하게 관람해 보세요."
  },
  DWML: {
    name: "지식 탐구형 선장",
    oneLiner: "추천 알고리즘 피드에 안주하지 않고 본인의 나침반을 들고 차분하고 밀도 높은 롱폼 교육 콘텐츠를 항해합니다.",
    tags: ["#지식탐구", "#주체적항해", "#깊은몰입"],
    attention: "자신만의 지식 주제에 지나치게 수렴되어 다른 관점이나 대중적인 유희 카테고리의 트렌드를 완고하게 배척할 수 있습니다.",
    recovery: "가끔은 대중적인 최신 테크나 문화 트렌드 요약 숏폼을 가볍게 구경하며 시야를 환기해 보세요."
  },
  DNSF: {
    name: "마라맛 쇼츠 광부",
    oneLiner: "확고하게 매료된 특정 장르나 채널에 들어가, 자극도가 강렬한 숏폼들만 집중적으로 시청하는 경향입니다.",
    tags: ["#특정장르", "#쇼츠채굴", "#고자극선호"],
    attention: "알고리즘이 주는 좁고 강력한 자극의 루프에 매료되어 폭넓은 지식 노출과 사고의 다양성이 제한되기 쉽습니다.",
    recovery: "유튜브를 켜기 전에 평소 보던 주제 반대편에 있는 유익한 키워드를 직접 1회 검색해 보세요."
  },
  DNSL: {
    name: "심연의 마라맛 광부",
    oneLiner: "본인이 매료된 특정 관심 주제에 긴 시간 깊이 몰입하며, 논쟁적이고 강렬한 자극의 롱폼 영상을 집요하게 시청합니다.",
    tags: ["#심연탐구", "#집요한몰입", "#논쟁주제"],
    attention: "소수의 극단적이거나 논쟁적인 정보원에 고착되어 다른 사람들의 평범한 상식이나 다각도 시각과 괴리될 위험이 있습니다.",
    recovery: "국제 외신이나 공영 다큐멘터리를 통해 더 다각적이고 균형 잡힌 정보 출처를 복원해 보세요."
  },
  DNMF: {
    name: "조용한 기술 덕후",
    oneLiner: "본인의 명확한 전문 분야(Tech, 코딩, 기계 조작 등)의 유익한 정보 위주로 가볍고 핵심적인 스낵 콘텐츠를 봅니다.",
    tags: ["#기술탐구", "#덕후성향", "#조용한수용"],
    attention: "일상적 유희나 감정적 공감을 나누는 스토리 중심 콘텐츠를 소홀히 하여 소통의 유연성이 다소 저하될 수 있습니다.",
    recovery: "따뜻한 감동 중심의 인간 극장이나 일상 다큐멘터리 영상 1편을 평온하게 감상해 보는 것을 추천합니다."
  },
  DNML: {
    name: "한우물 연구자",
    oneLiner: "특정 학술/전문 분야에 대한 깊은 애착을 바탕으로 유해성 있는 자극을 배제하고 한우물만 진지하게 연구하듯 봅니다.",
    tags: ["#학구파", "#자극배제", "#진지한탐구"],
    attention: "미디어 소비 습관은 매우 건전하나 지나친 학술적 고립으로 인해 미디어 소비의 즐거움과 다양성이 아쉬울 수 있습니다.",
    recovery: "유튜브를 단순한 학습 도구가 아닌 가벼운 웃음을 주는 스포츠 하이라이트 등 오락성 콘텐츠로 하루 5분 휴식해 보세요."
  },
  PWSF: {
    name: "알고리즘 롤러코스터",
    oneLiner: "추천 알고리즘 피드의 파도를 타고 유희적이고 흥미진진한 숏폼 콘텐츠를 스릴 넘치게 즐겨보는 유형입니다.",
    tags: ["#추천파도", "#롤러코스터", "#숏폼여행"],
    attention: "직접 검색어를 입력하는 적극적 의지가 점차 수동적으로 변해 주체적인 미디어 소비 근력이 약해질 수 있습니다.",
    recovery: "피드의 영상을 누르기 전에 내가 '왜 누르는지'를 스스로에게 한마디 질문하는 잠깐 멈춤 루틴을 가져보세요."
  },
  PWSL: {
    name: "자동재생 극장 관객",
    oneLiner: "자동재생이 추천하는 다채롭고 감정적인 롱폼 콘텐츠들을 수동적으로 켜두고 몰입하여 감상하는 관객입니다.",
    tags: ["#자동재생", "#수동적관객", "#롱폼시청"],
    attention: "본인과 다른 성격의 가짜 자극 영상도 끊임없이 자동 재생되어 인지적 불균형을 스스로 인지하지 못할 수 있습니다.",
    recovery: "자동재생 옵션을 의도적으로 해제하고, 영상 하나가 끝날 때마다 다음에 볼 채널을 직접 검색해 고르세요."
  },
  PWMF: {
    name: "유튜브 유람선 탑승객",
    oneLiner: "추천 피드가 데려다주는 안전하고 건전하며 자극이 적은 정보/취미 카테고리의 스낵 영상들을 평화롭게 소비합니다.",
    tags: ["#유람선탑승", "#안전지대", "#취미탐방"],
    attention: "모험을 피해 늘 익숙하고 편안한 에코 챔버에만 갇혀 있어, 뇌에 신선하고 깊이 있는 지적 도전을 가로막을 수 있습니다.",
    recovery: "평소 접하지 않던 약간은 어렵고 학술적인 전문 과학 대중 강연을 10분만 시청해보는 지적 도전을 추천합니다."
  },
  PWML: {
    name: "편안한 자동재생러",
    oneLiner: "다양하고 편안한 성격의 롱폼 영상들을 추천 흐름에 맞춰 평화롭게 틀어두고 부담 없이 배경음처럼 활용합니다.",
    tags: ["#라디오유저", "#편안한흐름", "#무자극롱폼"],
    attention: "미디어 소비의 적극성이 매우 떨어져 필요한 정보가 생겼을 때 스스로 능동적으로 교차 검증하는 능력이 무뎌질 수 있습니다.",
    recovery: "라디오처럼 틀어놓는 습관 대신, 15분 동안 오직 영상의 자막과 내레이션에 고도로 주의를 다해 적극적으로 관람해보세요."
  },
  PNSF: {
    name: "알고리즘 도파민 루프",
    oneLiner: "추천 피드가 연결해 주는 특정 관심 영역의 짧고 입체적이며 호기심을 유발하는 콘텐츠 루프 속에 머무는 성향입니다.",
    tags: ["#도파민루프", "#알고리즘노출", "#속도감"],
    attention: "가장 짧고 강렬한 지점만 학습하므로 차분한 전개가 계속되는 문장이나 깊이 있는 미디어 소통에 지루함을 느끼기 쉽습니다.",
    recovery: "추천 영상 하나를 바로 누르기 전에 검색창에 직접 내가 원하는 키워드 하나를 검색하여 재생해 보세요."
  },
  PNSL: {
    name: "알고리즘 심연 정주행러",
    oneLiner: "알고리즘이 제시한 특정 자극이나 논쟁 중심의 강력한 테마 흐름을 따라 긴 롱폼 정주행에 깊이 몰입하는 유형입니다.",
    tags: ["#심연정주행", "#알고리즘추적", "#끝장몰입"],
    attention: "논쟁적인 자극 영상들이 꼬리를 물어 특정 채널의 주장을 무비판적으로 수용하거나 인지적 편중을 가중시킬 수 있습니다.",
    recovery: "반대 성향을 가진 차분한 중립 뉴스나 공영 방송사의 정량적인 시각을 1편 곁들여보세요."
  },
  PNMF: {
    name: "조용한 추천 루틴러",
    oneLiner: "추천 메커니즘을 전적으로 신뢰하되, 자극적인 이슈보다는 차분하고 짧게 정돈된 지식/취미 위주로 평화롭게 봅니다.",
    tags: ["#조용한루틴", "#차분한시청", "#안정적정보"],
    attention: "알고리즘이 잘 정제된 취미를 추천해 주므로 안전하지만, 직접 다른 정보원을 발굴하고 비판적으로 분석하는 노력이 줄어듭니다.",
    recovery: "오늘 본 미디어에서 가장 흥미로웠던 사실 한 줄을 기록하고 그 주장이 참인지 포털에 직접 구글링해보세요."
  },
  PNML: {
    name: "자동재생 한우물러",
    oneLiner: "알고리즘 피드가 가리키는 특정 건전 주제와 롱폼 채널에 안착하여, 자동재생 흐름에 맞춰 평화롭게 한우물을 시청하는 경향입니다.",
    tags: ["#자동한우물", "#평화적시청", "#건전수용"],
    attention: "특정 채널에 과도하게 의존하게 되어 다양한 인지 자극과 새로운 흥미 요소를 발견하는 기회가 차단될 수 있습니다.",
    recovery: "전혀 다른 분야인 '스포츠 분석'이나 '대중 교양 음악사' 채널의 대표 명작 영상을 1편 의도적으로 구동해 보세요."
  }
};

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
      <div className="min-height-screen bg-slate-950 flex flex-col items-center justify-center text-white p-6">
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
  const actualCode = processedData.actual_dsao?.code || "PNML";
  const character = CHARACTER_MAP[actualCode] || {
    name: processedData.actual_dsao?.name || "알고리즘 한우물러",
    oneLiner: "다양한 취미/관심사의 비디오를 알고리즘 피드가 지정하는 고유 흐름대로 시청하는 안정적 유형입니다.",
    tags: ["#자동한우물", "#안정시청", "#알고리즘적용"],
    attention: "다양한 외부 정보원을 골고루 경험하여 시야를 다양하게 복원하는 노력이 다소 아쉬울 수 있습니다.",
    recovery: "평소와 완전히 다른 새로운 시사 뉴스나 기술 강좌 영상을 한 편 의도적으로 찾아 관람해 보세요."
  };

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
                onClick={() => router.push("/mission?plan_id=mvp-active-plan")}
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
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6 border-b border-slate-900 pb-4">
            <div>
              <span className="text-xs font-semibold tracking-wider text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-full uppercase">
                실제 데이터 기반 알고리즘 유형 캐릭터
              </span>
              <h2 className="text-2xl font-black text-white mt-3 font-heading tracking-tight flex items-center gap-2">
                {character.name} <span className="text-sm font-semibold text-slate-400 bg-slate-800 px-2 py-0.5 rounded">{actualCode}</span>
              </h2>
            </div>
            <div className="flex flex-wrap gap-1.5">
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
      <div className="min-height-screen bg-slate-950 flex flex-col items-center justify-center text-white">
        <span className="animate-spin text-3xl mb-4">🌀</span>
        <p className="text-slate-400 font-semibold">시청 기록 데이터 분석 결과 구성 중...</p>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}
