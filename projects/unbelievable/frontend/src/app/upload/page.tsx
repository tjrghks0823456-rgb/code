"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [agreed, setAgreed] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  
  // Meta-cognitive self-diagnosis survey state (0-100 scale)
  const [survey, setSurvey] = useState({
    TDS: 50, // 주제 다양성
    SBS: 50, // 출처 균형
    EBS: 50, // 감정 균형
    VOS: 50, // 관점 개방성
    SMS: 50, // 유해/자극 안전
    UAS: 50  // 사용자 주도성
  });
  
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSurveyChange = (axis: string, value: number) => {
    setSurvey(prev => ({ ...prev, [axis]: value }));
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    
    setUploading(true);
    setErrorMsg(null);
    
    try {
      // 1. Upload File via FormData
      const formData = new FormData();
      formData.append("file", file);
      
      const uploadRes = await fetch("http://localhost:8000/api/v1/upload?user_id=00000000-0000-0000-0000-000000000001", {
        method: "POST",
        body: formData,
      });
      
      if (!uploadRes.ok) {
        throw new Error(`파일 업로드 실패 (HTTP 상태코드 ${uploadRes.status})`);
      }
      
      const uploadData = await uploadRes.json();
      const fileId = uploadData.file_id;
      
      if (!fileId) {
        throw new Error("서버로부터 파일 ID를 전달받지 못했습니다.");
      }
      
      // 2. Trigger Analysis Calculation
      const analysisRes = await fetch(`http://localhost:8000/api/v1/analysis/run?file_id=${fileId}&user_id=00000000-0000-0000-0000-000000000001`, {
        method: "POST",
      });
      
      if (!analysisRes.ok) {
        throw new Error(`정량 편향 분석 실행 실패 (HTTP 상태코드 ${analysisRes.status})`);
      }
      
      const analysisData = await analysisRes.json();
      const runId = analysisData.run_id;
      
      if (!runId) {
        throw new Error("분석 실행 ID(run_id) 수신 실패");
      }
      
      setUploading(false);
      router.push(`/dashboard?run_id=${runId}`);
    } catch (err: any) {
      console.error("API connection failed:", err);
      setErrorMsg(err.message || "서버 연결에 실패했습니다.");
      setUploading(false);
    }
  };

  return (
    <div className="min-height-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-2xl bg-slate-900/40 border border-slate-800 rounded-3xl p-8 backdrop-blur-lg shadow-2xl relative">
        
        {/* Header */}
        <div className="mb-8 text-center">
          <span className="text-xs uppercase tracking-wider font-semibold text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full">
            Step {step} of 3
          </span>
          <h1 className="text-3xl font-extrabold text-white mt-3 font-heading">
            {step === 1 && "개인정보 수집 및 분석 동의"}
            {step === 2 && "YouTube 시청 기록 업로드"}
            {step === 3 && "미디어 분석 시작 준비"}
          </h1>
          <p className="text-sm text-slate-400 mt-2">
            {step === 1 && "디지털 디톡스 편향성 측정을 시작하기 위해 동의서에 서명해 주세요."}
            {step === 2 && "Google Takeout을 통해 발급받은 시청 및 검색기록 파일(.json / .csv)을 업로드해 주세요."}
            {step === 3 && "선택한 시청 기록 데이터를 바탕으로 분석을 시작할 준비가 되었습니다."}
          </p>
        </div>

        {/* Step 1: Consent */}
        {step === 1 && (
          <div className="space-y-6">
            <div className="bg-slate-950/50 border border-slate-800/80 rounded-2xl p-6 h-60 overflow-y-auto text-xs text-slate-400 leading-relaxed">
              <h3 className="text-sm font-bold text-white mb-2">[필수] 개인정보 수집 및 외부 API 분석 이용 동의서</h3>
              <p className="mb-4">언블리버블 서비스는 귀하가 업로드한 YouTube 시청 및 검색 데이터를 정규화하여 미디어 소비 성향의 편향성을 진단합니다. 분석 과정에서 아래 외부 API를 연동하여 동작합니다.</p>
              <ul className="list-disc list-inside space-y-2 mb-4">
                <li><strong>Google Cloud Natural Language API</strong>: 영상 제목 및 검색어의 텍스트 감정 톤 및 주제 분류 수집 (정량 전처리용)</li>
                <li><strong>Gemini 2.5 Flash API</strong>: 분석 완료 점수를 기반으로 디톡스 미션 및 맞춤형 검색 대안 권고사항 생성 (생성용)</li>
              </ul>
              <p>귀하의 모든 업로드 원본 파일은 분석 직후 또는 삭제 요청 시 비식별 조치 및 파기됩니다. Supabase RLS 정책에 따라 본인의 계정 외에는 외부 접근이 차단되도록 보호됩니다.</p>
            </div>
            
            <label className="flex items-center gap-3 cursor-pointer p-4 rounded-xl hover:bg-slate-800/20 border border-slate-800/50">
              <input 
                type="checkbox" 
                checked={agreed} 
                onChange={(e) => setAgreed(e.target.checked)} 
                className="w-5 h-5 rounded border-slate-800 text-purple-500 focus:ring-purple-500" 
              />
              <span className="text-sm text-slate-300">위 안내를 모두 정독하였으며, 분석 수집 및 API 활용에 전적으로 동의합니다.</span>
            </label>
            
            <button
              onClick={() => agreed && setStep(2)}
              disabled={!agreed}
              className={`w-full py-4 rounded-2xl font-bold transition-all ${agreed ? "bg-purple-600 text-white hover:bg-purple-500 shadow-lg shadow-purple-500/20" : "bg-slate-800 text-slate-500 cursor-not-allowed"}`}
            >
              다음 단계로 이동 <i className="ri-arrow-right-line ml-1"></i>
            </button>
          </div>
        )}

        {/* Step 2: Upload File */}
        {step === 2 && (
          <div className="space-y-6">
            <div className="border-2 border-dashed border-slate-800 hover:border-purple-500/50 rounded-2xl p-10 flex flex-col items-center justify-center cursor-pointer transition-all bg-slate-950/20 relative">
              <input 
                type="file" 
                accept=".json,.csv,.txt"
                onChange={(e) => e.target.files && setFile(e.target.files[0])}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <div className="w-16 h-16 bg-purple-500/10 rounded-full flex items-center justify-center text-2xl text-purple-400 mb-4">
                📁
              </div>
              <span className="text-sm font-semibold text-slate-300">
                {file ? file.name : "Google Takeout 시청 및 검색기록 파일 업로드"}
              </span>
              <span className="text-xs text-slate-500 mt-2">
                파일 최대 50MB (.json, .csv 형식 지원)
              </span>
            </div>
            
            <div className="flex gap-4">
              <button onClick={() => setStep(1)} className="w-1/3 py-4 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-2xl transition-all">
                이전
              </button>
              <button 
                onClick={() => file && setStep(3)} 
                disabled={!file} 
                className={`w-2/3 py-4 rounded-2xl font-bold transition-all ${file ? "bg-purple-600 text-white hover:bg-purple-500 shadow-lg shadow-purple-500/20" : "bg-slate-800 text-slate-500 cursor-not-allowed"}`}
              >
                자가진단 진행하기 <i className="ri-arrow-right-line ml-1"></i>
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Self-Diagnosis Survey */}
        {step === 3 && (
          <form onSubmit={handleUpload} className="space-y-6">
            <div className="space-y-4 bg-slate-950/40 border border-slate-800/80 rounded-2xl p-6 text-center">
              <div className="w-16 h-16 bg-purple-500/10 rounded-full flex items-center justify-center text-2xl text-purple-400 mx-auto mb-2 animate-bounce">
                ⚙️
              </div>
              <h3 className="text-base font-bold text-white">시청 데이터 분석 시작 준비</h3>
              <p className="text-xs text-slate-400 leading-relaxed max-w-sm mx-auto">
                파일 선택이 완료되었습니다. 이제 업로드와 분석을 시작할 수 있습니다. 분석 시작 후 서버에서 시청 기록 정규화, 5초 미만 보조 필터링, 6축 점수 계산이 순차적으로 진행됩니다.
              </p>
              
              <div className="mt-4 pt-3 border-t border-slate-800/60 text-left space-y-2 max-w-xs mx-auto">
                <div className="flex items-center gap-2 text-xs text-slate-400 font-semibold">
                  <span className="text-emerald-500">✓</span> 개인정보 보안 및 수집 이용 동의
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-300 font-semibold">
                  <span className="text-emerald-500">✓</span> YouTube 시청 데이터 선택 완료
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400 font-semibold">
                  <span className="text-emerald-500">✓</span> 6축 성향 대조 파이프라인 대기 중
                </div>
              </div>
            </div>
            
            {errorMsg && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 text-center">
                <p className="text-xs text-red-400 font-semibold leading-relaxed">
                  ⚠️ 분석 중 오류가 발생했습니다.<br />
                  백엔드 서버(FastAPI: Port 8000)가 정상 실행 중인지 확인해주세요.<br />
                  <span className="text-[10px] text-red-400/80">상세 오류: {errorMsg}</span>
                </p>
              </div>
            )}
            
            <div className="flex gap-4">
              <button type="button" onClick={() => setStep(2)} className="w-1/3 py-4 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-2xl transition-all">
                이전
              </button>
              <button 
                type="submit" 
                disabled={uploading}
                className="w-2/3 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold rounded-2xl transition-all shadow-lg shadow-purple-500/25 flex justify-center items-center gap-2"
              >
                {uploading ? (
                  <>
                    <span className="animate-spin text-lg">⏳</span> 실시간 도파민 필터링 및 분석 중...
                  </>
                ) : (
                  <>
                    🚀 최종 분석 시작하기
                  </>
                )}
              </button>
            </div>
          </form>
        )}

      </div>
    </div>
  );
}
