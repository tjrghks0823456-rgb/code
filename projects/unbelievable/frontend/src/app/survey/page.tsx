"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { saveSelfSurveyResult, SelfSurveyResult } from "../../utils/surveyStorage";

interface Question {
  id: string;
  text: string;
  axis: "D" | "P" | "W" | "N" | "S" | "M" | "F" | "L";
}

const QUESTIONS: Question[] = [
  // 1. D/P 탐색 방식
  { id: "q1", text: "나는 보고 싶은 콘텐츠를 직접 검색해서 찾아보는 편이다.", axis: "D" },
  { id: "q2", text: "추천 피드에 뜬 영상을 누르다 보면 원래 보려던 것과 다른 콘텐츠를 보고 있을 때가 많다.", axis: "P" },
  { id: "q3", text: "관심 있는 채널이나 주제를 정해두고 직접 찾아보는 편이다.", axis: "D" },
  { id: "q4", text: "자동재생이나 추천 영상 흐름을 따라 오래 보는 편이다.", axis: "P" },
  // 2. W/N 관심 범위
  { id: "q5", text: "나는 평소 여러 분야의 콘텐츠를 골고루 보는 편이다.", axis: "W" },
  { id: "q6", text: "한 번 관심이 생긴 주제는 관련 콘텐츠를 계속 이어서 보는 편이다.", axis: "N" },
  { id: "q7", text: "정치, 예능, 취미, 학습, 뉴스 등 다양한 카테고리를 넘나드는 편이다.", axis: "W" },
  { id: "q8", text: "특정 주제나 장르의 콘텐츠가 내 시청 기록에서 큰 비중을 차지한다.", axis: "N" },
  // 3. S/M 자극 성향
  { id: "q9", text: "자극적인 제목이나 썸네일이 있으면 궁금해서 눌러보는 편이다.", axis: "S" },
  { id: "q10", text: "논쟁, 폭로, 갈등, 분노를 다룬 콘텐츠를 자주 보게 된다.", axis: "S" },
  { id: "q11", text: "나는 자극적인 콘텐츠보다 차분한 설명이나 정보성 콘텐츠를 선호한다.", axis: "M" },
  { id: "q12", text: "콘텐츠를 볼 때 재미나 충격보다 신뢰도와 설명의 균형을 더 중요하게 본다.", axis: "M" },
  // 4. F/L 시청 호흡
  { id: "q13", text: "나는 짧은 영상이나 쇼츠를 빠르게 넘겨보는 편이다.", axis: "F" },
  { id: "q14", text: "긴 영상보다는 짧고 핵심만 있는 콘텐츠가 더 편하다.", axis: "F" },
  { id: "q15", text: "관심 있는 주제라면 20분 이상의 긴 영상도 끝까지 보는 편이다.", axis: "L" },
  { id: "q16", text: "하나의 주제를 깊게 이해하기 위해 긴 해설 영상이나 강의를 보는 편이다.", axis: "L" }
];

const MODULE_NAMES = [
  "탐색 방식 (D/P)",
  "관심 범위 (W/N)",
  "자극 성향 (S/M)",
  "시청 호흡 (F/L)"
];

const MODULE_DESCS = [
  "콘텐츠를 선택할 때 스스로 주도하여 탐색하는지, 추천 시스템을 적극 활용하는지 진단합니다.",
  "다양한 카테고리를 폭넓게 탐험하는지, 관심이 생긴 하나의 테마에 깊게 파고드는지 진단합니다.",
  "도파민을 자극하는 Spicy한 감정 콘텐츠에 반응하는지, 차분하고 Mild한 유익 정보를 선호하는지 진단합니다.",
  "짧고 속도감 있는 콘텐츠를 가볍게 훑어보는지, 긴 호흡의 상세한 설명에 몰입하는지 진단합니다."
];

const TYPE_NAMES: Record<string, string> = {
  DWSF: "도파민 탐험가",
  DWSL: "마라맛 큐레이터",
  DWMF: "지식 스낵 탐색가",
  DWML: "지식 탐구형 선장",
  DNSF: "마라맛 쇼츠 광부",
  DNSL: "심연의 마라맛 광부",
  DNMF: "조용한 기술 덕후",
  DNML: "한우물 연구자",
  PWSF: "알고리즘 롤러코스터",
  PWSL: "자동재생 극장 관객",
  PWMF: "유튜브 유람선 탑승객",
  PWML: "편안한 자동재생러",
  PNSF: "알고리즘 도파민 루프",
  PNSL: "알고리즘 심연 정주행러",
  PNMF: "조용한 추천 루틴러",
  PNML: "자동재생 한우물러"
};

const TYPE_DESCS: Record<string, string> = {
  DWSF: "자신이 원하는 분야의 다양한 정보를 자발적으로 찾아보는 과정에서, 간혹 가벼운 자극이나 흥미 중심의 콘텐츠를 빠르게 수용하는 성향입니다.",
  DWSL: "주도적으로 풍부한 정보원을 발굴하되, 긴 호흡의 강렬하거나 몰입감 높은 주제들을 탐색하고 아카이빙하는 경향이 뚜렷한 유형입니다.",
  DWMF: "자율적으로 유용한 상식과 과학적, 정보성 지식을 수집하며, 바쁜 시간 속에서 주로 컴팩트하게 정리된 숏폼 형태를 영리하게 소비합니다.",
  DWML: "추천 엔진에 안주하지 않고 본인의 나침반을 들고 차분하고 밀도 높은 긴 호흡의 지식 다큐멘터리나 교육 자료를 주도적으로 항해합니다.",
  DNSF: "확고하게 매료된 특정 장르나 소수 채널에 들어가, 주로 자극적이고 폭발적인 즐거움을 유발하는 숏폼들을 연속적으로 채굴하는 취향입니다.",
  DNSL: "본인의 특정한 관심 테마에 온전하게 가두어 둔 채, 논쟁적이거나 심오하며 마라맛처럼 자극도가 강렬한 롱폼들을 정교하게 분석하듯 봅니다.",
  DNMF: "본인의 명확한 전문 분야(Tech, 코딩, 기계 조작 등)의 정보를 적극 추적하며, 핵심적인 설명 위주의 스낵 비디오를 즐겨 소비하는 성향입니다.",
  DNML: "특정 장르나 타겟 정보에 대한 학술적 탐구도가 아주 깊으며, 유해 자극을 배제하고 한우물만 진지하고 깊이 있게 정독하듯 공부합니다.",
  PWSF: "추천 알고리즘이 연결해 주는 파도를 타고 유희적이고 흥미진진한 숏폼 콘텐츠들을 가볍게 건너뛰며 즐거운 엔터테인먼트를 영위합니다.",
  PWSL: "자동재생이 추천하는 다채로운 감정 유발 콘텐츠들을 수동적으로 켜놓은 채, 긴 호흡의 영상들을 차분하게 몰입해 바라보는 관객입니다.",
  PWMF: "추천 피드가 데려다주는 안전하고 건전하며 자극이 덜한 정보/취미 카테고리들의 스낵 콘텐츠들을 평화롭게 여행하는 탑승객입니다.",
  PWML: "다양하고 편안한 성격의 롱폼 영상들을 추천 흐름이 흘러가는 대로 고요히 재생해 두고 부담 없이 편안하게 즐겨봅니다.",
  PNSF: "추천 피드가 연결해 주는 특정 관심 영역의 짧고 입체적이며 흥미를 자극하는 콘텐츠 루프 속에서 자연스러운 즐거움을 경험하는 성향입니다.",
  PNSL: "알고리즘이 제시한 특정 자극이나 논쟁 중심의 강력한 주제 흐름을 거스르지 않고, 긴 롱폼 정주행에 오랜 시간을 흔쾌히 몰입합니다.",
  PNMF: "추천 메커니즘을 적극 신뢰하되, 자극적인 이슈보다는 본인 관심 분야의 차분하고 짧게 정돈된 영상 중심의 루틴을 조용하게 소비합니다.",
  PNML: "알고리즘 피드가 가리키는 특정 건전 주제와 롱폼 채널에 안착하여, 자동재생 흐름에 맞춰 평화롭게 한우물을 시청하는 경향입니다."
};

export default function SurveyPage() {
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState(0); // 0, 1, 2, 3 = Modules, 4 = Result View
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<SelfSurveyResult | null>(null);

  const handleAnswerSelect = (qId: string, score: number) => {
    setAnswers(prev => ({
      ...prev,
      [qId]: score
    }));
  };

  const getPageQuestions = (pageIndex: number) => {
    return QUESTIONS.slice(pageIndex * 4, (pageIndex + 1) * 4);
  };

  const isPageComplete = (pageIndex: number) => {
    const questions = getPageQuestions(pageIndex);
    return questions.every(q => answers[q.id] !== undefined);
  };

  const allQuestionsAnswered = () => {
    return QUESTIONS.every(q => answers[q.id] !== undefined);
  };

  const calculateResult = () => {
    // 1. Scoring
    const D = (answers.q1 || 3) + (answers.q3 || 3);
    const P = (answers.q2 || 3) + (answers.q4 || 3);
    
    const W = (answers.q5 || 3) + (answers.q7 || 3);
    const N = (answers.q6 || 3) + (answers.q8 || 3);
    
    const S = (answers.q9 || 3) + (answers.q10 || 3);
    const M = (answers.q11 || 3) + (answers.q12 || 3);
    
    const F = (answers.q13 || 3) + (answers.q14 || 3);
    const L = (answers.q15 || 3) + (answers.q16 || 3);

    // 2. Decision Logic with Tie-breakers
    const code_DP = D >= P ? "D" : "P";
    const code_WN = W >= N ? "W" : "N";
    const code_SM = M >= S ? "M" : "S"; // Tie-breaker: M
    const code_FL = L >= F ? "L" : "F"; // Tie-breaker: L

    const resultCode = `${code_DP}${code_WN}${code_SM}${code_FL}`;
    const resultName = TYPE_NAMES[resultCode] || "미지의 미디어 관찰자";

    const surveyResult: SelfSurveyResult = {
      answers,
      axisScores: { D, P, W, N, S, M, F, L },
      axisMargins: {
        DP: D - P,
        WN: W - N,
        SM: M - S,
        FL: L - F
      },
      resultCode,
      resultName,
      createdAt: new Date().toISOString(),
      schemaVersion: "1.0.0"
    };

    saveSelfSurveyResult(surveyResult);
    setResult(surveyResult);
    setCurrentPage(4); // Move to result screen
  };

  const handleRetake = () => {
    setAnswers({});
    setResult(null);
    setCurrentPage(0);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 md:p-12 font-body relative">
      
      {/* Background radial soft light (No aggressive neon) */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[20%] left-[25%] w-[40%] h-[40%] rounded-full bg-slate-900/40 blur-[100px]" />
      </div>

      <div className="w-full max-w-2xl bg-slate-900/30 border border-slate-800/80 rounded-3xl p-6 md:p-8 backdrop-blur-md shadow-2xl relative z-10">
        
        {/* PROGRESS BLOCK (Surveys 1 to 4) */}
        {currentPage < 4 && (
          <div>
            {/* Header */}
            <div className="text-center mb-6">
              <span className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
                DSAO 자가진단 설문
              </span>
              <h1 className="text-2xl font-bold text-white mt-1 font-heading">
                {MODULE_NAMES[currentPage]}
              </h1>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto leading-relaxed">
                {MODULE_DESCS[currentPage]}
              </p>
            </div>

            {/* Stepper progress bar */}
            <div className="w-full bg-slate-950 rounded-full h-1.5 mb-8 border border-slate-850 overflow-hidden">
              <div 
                className="bg-purple-600 h-full rounded-full transition-all duration-300"
                style={{ width: `${((currentPage + 1) / 4) * 100}%` }}
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-2 font-semibold px-1">
                <span>1. 탐색방식</span>
                <span>2. 관심범위</span>
                <span>3. 자극성향</span>
                <span>4. 시청호흡</span>
              </div>
            </div>

            {/* Questions list (4 per module page) */}
            <div className="space-y-6">
              {getPageQuestions(currentPage).map((q, idx) => (
                <div key={q.id} className="bg-slate-950/40 border border-slate-850/60 rounded-2xl p-5 space-y-4">
                  <div className="flex gap-2">
                    <span className="text-xs font-bold text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded h-fit">
                      Q{currentPage * 4 + idx + 1}
                    </span>
                    <h3 className="text-sm text-slate-200 leading-relaxed font-semibold">
                      {q.text}
                    </h3>
                  </div>

                  {/* Likert Scale (1 to 5 buttons, mobile-friendly touch chips) */}
                  <div className="grid grid-cols-5 gap-2 pt-1">
                    {[1, 2, 3, 4, 5].map(score => {
                      const labels = ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"];
                      const isSelected = answers[q.id] === score;
                      return (
                        <button
                          key={score}
                          type="button"
                          onClick={() => handleAnswerSelect(q.id, score)}
                          className={`py-2 px-1 rounded-xl text-center transition-all flex flex-col items-center justify-center border ${
                            isSelected 
                              ? "bg-purple-950/20 border-purple-500/80 text-purple-300 font-bold" 
                              : "bg-slate-900/40 border-slate-850 text-slate-400 hover:border-slate-700 hover:text-slate-300"
                          }`}
                        >
                          <span className="text-xs md:text-sm">{score}</span>
                          <span className="text-[8px] md:text-[9px] mt-1 text-slate-500 tracking-tighter hidden sm:inline">
                            {labels[score - 1]}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            {/* Bottom Navigation */}
            <div className="flex justify-between items-center gap-4 mt-8 pt-4 border-t border-slate-900">
              <button
                type="button"
                onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
                disabled={currentPage === 0}
                className={`px-5 py-3 font-semibold text-xs rounded-xl transition-all ${
                  currentPage === 0 
                    ? "bg-slate-900/10 text-slate-600 cursor-not-allowed border border-transparent" 
                    : "bg-slate-900 border border-slate-850 text-slate-300 hover:text-white hover:border-slate-700"
                }`}
              >
                이전 단계
              </button>

              <span className="text-xs text-slate-500 font-medium">
                {currentPage + 1} / 4 페이지
              </span>

              {currentPage < 3 ? (
                <button
                  type="button"
                  onClick={() => setCurrentPage(prev => prev + 1)}
                  disabled={!isPageComplete(currentPage)}
                  className={`px-6 py-3 font-bold text-xs rounded-xl transition-all ${
                    isPageComplete(currentPage)
                      ? "bg-purple-600 text-white hover:bg-purple-500"
                      : "bg-slate-900 text-slate-650 cursor-not-allowed border border-transparent"
                  }`}
                >
                  다음 단계 →
                </button>
              ) : (
                <button
                  type="button"
                  onClick={calculateResult}
                  disabled={!allQuestionsAnswered()}
                  className={`px-6 py-3 font-bold text-xs rounded-xl transition-all ${
                    allQuestionsAnswered()
                      ? "bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-500 hover:to-indigo-500"
                      : "bg-slate-900 text-slate-650 cursor-not-allowed border border-transparent"
                  }`}
                >
                  결과 확인하기 ✓
                </button>
              )}
            </div>
          </div>
        )}

        {/* RESULT BLOCK (Page Index 4) */}
        {currentPage === 4 && result && (
          <div className="space-y-6">
            
            {/* Header Result */}
            <div className="text-center pb-4 border-b border-slate-900">
              <span className="text-xs font-semibold tracking-wider text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full">
                자가진단 결과 수집 완료
              </span>
              <h2 className="text-3xl font-black text-white mt-3 font-heading tracking-tight">
                {result.resultCode}
              </h2>
              <h3 className="text-lg font-bold text-slate-300 mt-1">
                {result.resultName}
              </h3>
            </div>

            {/* 4-Axis Diagnosis summary cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              
              <div className="bg-slate-950/30 border border-slate-850 p-4 rounded-2xl">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">1. 탐색 방식</span>
                <h4 className="text-sm font-bold text-white mt-1">
                  {result.resultCode.includes("D") ? "직접 운전형 (Driver)" : "추천 탑승형 (Passenger)"}
                </h4>
                <p className="text-[10px] text-slate-400 mt-1">
                  {result.resultCode.includes("D") 
                    ? "직접 탐색하고 검색하여 주도적으로 영상을 취사선택합니다." 
                    : "알고리즘의 정교한 흐름에 맞추어 제시되는 영상을 수용합니다."}
                </p>
              </div>

              <div className="bg-slate-950/30 border border-slate-850 p-4 rounded-2xl">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">2. 관심 범위</span>
                <h4 className="text-sm font-bold text-white mt-1">
                  {result.resultCode.includes("W") ? "폭넓은 탐색형 (Wide)" : "집중 몰입형 (Narrow)"}
                </h4>
                <p className="text-[10px] text-slate-400 mt-1">
                  {result.resultCode.includes("W") 
                    ? "정치, 예능, 시사, 정보 등 다채로운 영역을 다양하게 넘나듭니다." 
                    : "마음에 안착한 한두 주제의 세부 채널군을 진득하고 밀접하게 봅니다."}
                </p>
              </div>

              <div className="bg-slate-950/30 border border-slate-850 p-4 rounded-2xl">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">3. 자극 성향</span>
                <h4 className="text-sm font-bold text-white mt-1">
                  {result.resultCode.includes("M") ? "안정 정보형 (Mild)" : "고자극 반응형 (Spicy)"}
                </h4>
                <p className="text-[10px] text-slate-400 mt-1">
                  {result.resultCode.includes("M") 
                    ? "자극 유도 어휘보다 신뢰성 있고 감정이 치우치지 않는 정보에 반응합니다." 
                    : "썸네일 유도 문구나 시선을 끄는 논쟁, 갈등 중심의 이야기에 끌립니다."}
                </p>
              </div>

              <div className="bg-slate-950/30 border border-slate-850 p-4 rounded-2xl">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">4. 시청 호흡</span>
                <h4 className="text-sm font-bold text-white mt-1">
                  {result.resultCode.includes("L") ? "롱폼 몰입형 (Long)" : "숏폼 속도형 (Flash)"}
                </h4>
                <p className="text-[10px] text-slate-400 mt-1">
                  {result.resultCode.includes("L") 
                    ? "20분 이상 강의나 풀 다큐멘터리 등 맥락이 긴 영상을 잘 감상합니다." 
                    : "핵심만 있는 짧은 콘텐츠나 숏폼을 밀도 있고 빠르게 훑어봅니다."}
                </p>
              </div>

            </div>

            {/* Description Text */}
            <div className="bg-slate-950/50 border border-slate-900 rounded-2xl p-5 text-center">
              <p className="text-xs text-slate-400 leading-relaxed max-w-lg mx-auto">
                {TYPE_DESCS[result.resultCode]}
              </p>
            </div>

            {/* Informative Neutral Disclaimer Box */}
            <div className="bg-slate-900/10 border border-slate-850 rounded-2xl p-4 text-center">
              <p className="text-[11px] text-slate-500 leading-relaxed font-semibold">
                ℹ️ 이 결과는 사용자가 스스로 응답한 자가진단 결과이며, 이후 실제 시청 데이터 분석 결과와 비교됩니다.
              </p>
            </div>

            {/* Actions CTA buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-2">
              <button
                type="button"
                onClick={handleRetake}
                className="w-full sm:w-1/3 py-3 bg-slate-900 hover:bg-slate-850 border border-slate-800 text-slate-300 font-bold rounded-xl transition-all text-xs"
              >
                🔄 다시 진단하기
              </button>
              <button
                type="button"
                onClick={() => router.push("/upload")}
                className="w-full sm:w-2/3 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold rounded-xl transition-all shadow-lg text-xs flex justify-center items-center gap-1.5"
              >
                🚀 실제 소비 데이터 분석하기
              </button>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
