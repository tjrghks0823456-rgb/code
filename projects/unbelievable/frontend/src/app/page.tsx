import React from "react";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col justify-between p-6 md:p-12 relative overflow-hidden">
      
      {/* Navbar Header */}
      <header className="w-full max-w-6xl mx-auto flex justify-between items-center z-20">
        <div className="flex items-center gap-2">
          <span className="text-xl font-black text-white tracking-widest uppercase">
            SH.SON_<span className="text-purple-400">UNBELIEVABLE</span>
          </span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider hidden sm:inline">
            v1.0.0 Prototype
          </span>
          <Link
            href="/survey"
            className="px-4 py-2 text-xs font-bold bg-slate-900 border border-slate-800 rounded-full text-slate-300 hover:text-white hover:border-slate-700 transition-all"
          >
            시작하기
          </Link>
        </div>
      </header>

      {/* Main Content Hero */}
      <main className="w-full max-w-4xl mx-auto text-center my-auto py-12 md:py-24 z-20 flex flex-col items-center">
        
        {/* Glow badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/25 text-purple-300 text-xs font-semibold mb-8 animate-pulse shadow-neon-purple">
          🧠 당신의 알고리즘 미디어 소비 진단
        </div>

        {/* Big Bold Headline */}
        <h1 className="text-4xl md:text-7xl font-black tracking-tight text-white mb-6 leading-tight">
          알고리즘이 숨긴<br />
          <span className="text-gradient-neon">당신의 진짜 미디어 성향</span>
        </h1>

        <p className="text-base md:text-lg text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed font-body">
          우리는 평소 자신이 매우 균형 있고 유익한 콘텐츠를 소비하고 있다고 생각합니다.<br className="hidden sm:inline" />
          귀하의 YouTube 실제 시청 데이터를 정량 분석하여 사전 자가진단 결과와<br className="hidden sm:inline" />
          실제 데이터 간의 <strong>'메타인지 격차(Meta-gap)'</strong>를 시각화합니다.
        </p>

        {/* CTA Button */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            href="/survey"
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold rounded-2xl transition-all shadow-lg hover:shadow-purple-500/35 transform hover:-translate-y-0.5"
          >
            🚀 3분 만에 내 편향성 측정하기
          </Link>
          <a
            href="#features"
            className="px-6 py-4 bg-slate-900/60 hover:bg-slate-900 border border-slate-800 text-slate-300 hover:text-white font-semibold rounded-2xl transition-all"
          >
            기능 자세히 보기
          </a>
        </div>

        {/* Dynamic Concept Highlights */}
        <section id="features" className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl mt-24 text-left">
          
          <div className="glass-panel p-6 rounded-3xl transition-all hover:border-purple-500/30 group">
            <div className="w-12 h-12 bg-purple-500/10 rounded-2xl flex items-center justify-center text-xl text-purple-400 mb-4 group-hover:scale-110 transition-all">
              ⚡
            </div>
            <h3 className="text-lg font-bold text-white mb-2">무의식 노출 필터링</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              5초 미만의 무의식적 쇼츠/썸네일 탭 행위를 제외합니다. 의미 있는 관람 시간 위주로 당신의 실제 정보 노출 상태를 필터링합니다.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-3xl transition-all hover:border-purple-500/30 group">
            <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center text-xl text-blue-400 mb-4 group-hover:scale-110 transition-all">
              📊
            </div>
            <h3 className="text-lg font-bold text-white mb-2">메타인지 갭 시각화</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              사전 자가진단(예측)과 실제 YouTube 소비 데이터(사후)의 6축 레이더 갭 오버레이 분석으로 당신의 알고리즘 인지 격차를 시각적으로 분석합니다.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-3xl transition-all hover:border-purple-500/30 group">
            <div className="w-12 h-12 bg-pink-500/10 rounded-2xl flex items-center justify-center text-xl text-pink-400 mb-4 group-hover:scale-110 transition-all">
              🎯
            </div>
            <h3 className="text-lg font-bold text-white mb-2">생성형 디톡스 미션</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              편향 분석에 그치지 않고, Gemini 2.5 Flash를 이용해 부족한 인식을 완화할 대체 검색어(Reverse Query)와 맞춤형 미션을 자동 추천합니다.
            </p>
          </div>

        </section>

      </main>

      {/* Footer */}
      <footer className="w-full max-w-6xl mx-auto border-t border-slate-900 pt-6 text-center text-xs text-slate-600 z-20">
        <p>© 2026 SH.SON_UNBELIEVABLE Team. All rights reserved. 본 웹 서비스는 정량 점수 엔진과 생성형 보완 결합 프로토타입입니다.</p>
      </footer>

    </div>
  );
}
