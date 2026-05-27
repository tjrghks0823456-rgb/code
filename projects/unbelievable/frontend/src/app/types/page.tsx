"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { loadSelfSurveyResult } from "../../utils/surveyStorage";

const ALL_TYPES = [
  {
    code: "DWSF",
    name: "도파민 탐험가",
    oneLiner: "자발적으로 다채로운 정보를 개척하지만, 유희적인 숏폼 자극도 유연하게 수용하는 유형입니다.",
    tags: ["#주도적탐색", "#다채로운장르", "#가벼운숏폼"],
    pattern: "직접 새로운 채널을 탐험하다가도 숏폼의 매끄러운 전개에 즐겁게 머무릅니다."
  },
  {
    code: "DWSL",
    name: "마라맛 큐레이터",
    oneLiner: "주도적으로 풍부한 정보원을 발굴하되, 호흡이 길고 강렬한 몰입감 높은 주제들을 탐색하는 경향이 뚜렷한 유형입니다.",
    tags: ["#강렬한몰입", "#주체적아카이빙", "#롱폼선호"],
    pattern: "시사 논쟁이나 다각도의 대립 주제를 담은 긴 강의 및 토론을 주도적으로 수집해 시청합니다."
  },
  {
    code: "DWMF",
    name: "지식 스낵 탐색가",
    oneLiner: "자율적으로 지식과 교양을 채굴하며, 바쁜 일상 속에서 주로 컴팩트하게 요약된 스낵 숏폼 비디오를 즐깁니다.",
    tags: ["#지식스낵", "#자율적학습", "#컴팩트소비"],
    pattern: "IT 테크, 과학 교양 등을 본인이 관심 있는 시간에 압축 요약 영상으로 똑똑하게 섭취합니다."
  },
  {
    code: "DWML",
    name: "지식 탐구형 선장",
    oneLiner: "추천 알고리즘 피드에 안주하지 않고 본인의 나침반을 들고 차분하고 밀도 높은 롱폼 교육 콘텐츠를 항해합니다.",
    tags: ["#지식탐구", "#주체적항해", "#깊은몰입"],
    pattern: "역사 다큐멘터리, 학술 강연 등 호흡이 길고 자극이 배제된 미디어를 나만의 서재처럼 쌓아 둡니다."
  },
  {
    code: "DNSF",
    name: "마라맛 쇼츠 광부",
    oneLiner: "확고하게 매료된 특정 장르나 채널에 들어가, 자극도가 강렬한 숏폼들만 집중적으로 시청하는 경향입니다.",
    tags: ["#특정장르", "#쇼츠채굴", "#고자극선호"],
    pattern: "좋아하는 유튜버의 숏폼 릴레이나 특정 게임 하이라이트를 속도감 있게 반복 시청합니다."
  },
  {
    code: "DNSL",
    name: "심연의 마라맛 광부",
    oneLiner: "본인이 매료된 특정 관심 주제에 긴 시간 깊이 몰입하며, 논쟁적이고 강렬한 자극의 롱폼 영상을 집요하게 시청합니다.",
    tags: ["#심연탐구", "#집요한몰입", "#논쟁주제"],
    pattern: "하나의 의혹 제기나 심층 비하인드 시사 이야기를 집요하고 진지하게 연속 파헤치며 봅니다."
  },
  {
    code: "DNMF",
    name: "조용한 기술 덕후",
    oneLiner: "본인의 명확한 전문 분야(Tech, 코딩, 기계 조작 등)의 유익한 정보 위주로 가볍고 핵심적인 스낵 콘텐츠를 봅니다.",
    tags: ["#기술탐구", "#덕후성향", "#조용한수용"],
    pattern: "불필요한 설명이 없는 깔끔한 제품 분해기나 기술 튜토리얼 쇼츠를 평온하게 모니터링합니다."
  },
  {
    code: "DNML",
    name: "한우물 연구자",
    oneLiner: "특정 학술/전문 분야에 대한 깊은 애착을 바탕으로 유해성 있는 자극을 배제하고 한우물만 진지하게 연구하듯 봅니다.",
    tags: ["#학구파", "#자극배제", "#진지한탐구"],
    pattern: "특정 학술 강의 채널이나 어학 코스, 정형화된 교육 채널의 롱폼 영상들을 학업하듯 순차 수강합니다."
  },
  {
    code: "PWSF",
    name: "알고리즘 롤러코스터",
    oneLiner: "추천 알고리즘 피드의 파도를 타고 유희적이고 흥미진진한 숏폼 콘텐츠를 스릴 넘치게 즐겨보는 유형입니다.",
    tags: ["#추천파도", "#롤러코스터", "#숏폼여행"],
    pattern: "홈 피드가 이어주는 다양한 자극적 숏폼과 재미 위주의 화제 클립들을 물 흐르듯 가볍게 올라탑니다."
  },
  {
    code: "PWSL",
    name: "자동재생 극장 관객",
    oneLiner: "자동재생이 추천하는 다채롭고 감정적인 롱폼 콘텐츠들을 수동적으로 켜두고 몰입하여 감상하는 관객입니다.",
    tags: ["#자동재생", "#수동적관객", "#롱폼시청"],
    pattern: "알고리즘이 물고 오는 풍부한 취미/이슈 롱폼 플레이리스트를 켜두고 차분하고 수동적으로 흘려보냅니다."
  },
  {
    code: "PWMF",
    name: "유튜브 유람선 탑승객",
    oneLiner: "추천 피드가 데려다주는 안전하고 건전하며 자극이 적은 정보/취미 카테고리의 스낵 영상들을 평화롭게 소비합니다.",
    tags: ["#유람선탑승", "#안전지대", "#취미탐방"],
    pattern: "위험이나 극단적 논쟁 없이 가볍게 정돈된 동식물 일상, 캠핑 요리 요약 비디오를 흐뭇하게 탑승 시청합니다."
  },
  {
    code: "PWML",
    name: "편안한 자동재생러",
    oneLiner: "다양하고 편안한 성격의 롱폼 영상들을 추천 흐름에 맞춰 평화롭게 틀어두고 부담 없이 배경음처럼 활용합니다.",
    tags: ["#라디오유저", "#편안한흐름", "#무자극롱폼"],
    pattern: "백색소음 같은 플레이리스트나 편안한 여행 다큐 연속 방송을 추천 대기열대로 평온하게 걸어둡니다."
  },
  {
    code: "PNSF",
    name: "알고리즘 도파민 루프",
    oneLiner: "추천 피드가 연결해 주는 특정 관심 영역의 짧고 입체적이며 호기심을 유발하는 콘텐츠 루프 속에 머무는 성향입니다.",
    tags: ["#도파민루프", "#알고리즘노출", "#속도감"],
    pattern: "알고리즘이 맞춤 제시한 특정 관심 키워드의 스낵 클립들을 꼬리를 물어가며 끊임없이 터치 감상합니다."
  },
  {
    code: "PNSL",
    name: "알고리즘 심연 정주행러",
    oneLiner: "알고리즘이 제시한 특정 자극이나 논쟁 중심의 강력한 테마 흐름을 따라 긴 롱폼 정주행에 깊이 몰입하는 유형입니다.",
    tags: ["#심연정주행", "#알고리즘추적", "#끝장몰입"],
    pattern: "특정 자극적인 대립 사건이나 연예 폭로 등 꼬리 무는 알고리즘 추천 롱폼 흐름에 끝까지 탑승합니다."
  },
  {
    code: "PNMF",
    name: "조용한 추천 루틴러",
    oneLiner: "추천 메커니즘을 전적으로 신뢰하되, 자극적인 이슈보다는 차분하고 짧게 정돈된 지식/취미 위주로 평화롭게 봅니다.",
    tags: ["#조용한루틴", "#차분한시청", "#안정적정보"],
    pattern: "본인 입맛에 맞춰 조율된 홈 화면에서, 건전하고 짧게 정돈된 어학 팁이나 운동 팁을 평화롭게 소화합니다."
  },
  {
    code: "PNML",
    name: "자동재생 한우물러",
    oneLiner: "알고리즘 피드가 가리키는 특정 건전 주제와 롱폼 채널에 안착하여, 자동재생 흐름에 맞춰 평화롭게 한우물을 시청하는 경향입니다.",
    tags: ["#자동한우물", "#평화적시청", "#건전수용"],
    pattern: "알고리즘이 잘 골라놓은 특정 교양 음악 채널이나 바둑 중계 롱폼을 틀어놓고 편안하게 안착 시청합니다."
  }
];

export default function TypesPage() {
  const router = useRouter();
  const [myType, setMyType] = useState<string | null>(null);

  useEffect(() => {
    const survey = loadSelfSurveyResult();
    if (survey && survey.resultCode) {
      setMyType(survey.resultCode);
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 md:p-12 font-body relative">
      
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[10%] right-[20%] w-[35%] h-[35%] rounded-full bg-slate-900/30 blur-[120px]" />
      </div>

      <div className="max-w-6xl mx-auto space-y-8 relative z-10">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-900 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold text-white font-heading tracking-tight">
              🌐 DSAO 16유형 성향 도감
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              DSAO 16개 소비 유형 카드를 탐험하며 다양한 미디어 소비 양상을 가볍게 비교해 보세요.
            </p>
          </div>
          <button 
            onClick={() => router.back()}
            className="px-5 py-2.5 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-350 hover:text-white font-bold rounded-xl transition-all text-xs"
          >
            ← 이전 화면으로 복귀
          </button>
        </div>

        {/* 16-Type Card Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {ALL_TYPES.map((item) => {
            const isMyType = item.code === myType;
            return (
              <div 
                key={item.code}
                className={`rounded-2xl p-5 border transition-all duration-300 relative flex flex-col justify-between ${
                  isMyType 
                    ? "bg-purple-900/10 border-purple-500/60 shadow-[0_0_20px_rgba(168,85,247,0.15)] ring-1 ring-purple-500/25 scale-[1.02]" 
                    : "bg-slate-900/30 border-slate-800/80 hover:border-slate-700/80 hover:bg-slate-900/40"
                }`}
              >
                {isMyType && (
                  <span className="absolute top-4 right-4 text-[8px] font-black uppercase bg-purple-500/20 text-purple-300 border border-purple-500/40 px-2 py-0.5 rounded-full tracking-wider animate-pulse">
                    My Type
                  </span>
                )}
                
                <div>
                  <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-widest">{item.code}</span>
                  <h3 className="text-base font-bold text-white mt-1 font-heading">{item.name}</h3>
                  
                  <div className="flex flex-wrap gap-1 mt-2.5">
                    {item.tags.map(t => (
                      <span key={t} className="text-[8px] bg-slate-950 border border-slate-850 text-slate-400 px-2 py-0.5 rounded-full font-medium">
                        {t}
                      </span>
                    ))}
                  </div>
                  
                  <p className="text-[11px] text-slate-400 mt-4 leading-relaxed border-t border-slate-850/60 pt-3">
                    {item.oneLiner}
                  </p>
                </div>
                
                <div className="mt-4 pt-3 border-t border-dashed border-slate-850/50 bg-slate-950/20 p-2.5 rounded-xl">
                  <span className="text-[9px] font-bold text-indigo-400 uppercase tracking-wider block">소비 양상 예시</span>
                  <p className="text-[10px] text-slate-500 mt-1 leading-relaxed">
                    {item.pattern}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
}
