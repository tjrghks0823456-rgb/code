"use client";

import React, { useState } from "react";
import { ArrowLeft, ArrowRight, FileUp, Play, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import PageShell from "../../components/PageShell";
import { Button } from "../../components/Button";
import Card from "../../components/Card";
import SectionTitle from "../../components/SectionTitle";

const prepItems = ["파일 준비", "개인정보 안내 확인", "시청 기록 선택", "분석 준비 완료"];

export default function UploadPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [agreed, setAgreed] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setErrorMsg(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await fetch("http://localhost:8000/api/v1/upload?user_id=00000000-0000-0000-0000-000000000001", {
        method: "POST",
        body: formData
      });

      if (!uploadRes.ok) {
        throw new Error(`파일 업로드 실패 (HTTP ${uploadRes.status})`);
      }

      const uploadData = await uploadRes.json();
      const fileId = uploadData.file_id;

      if (!fileId) {
        throw new Error("서버에서 파일 ID를 받지 못했습니다.");
      }

      const analysisRes = await fetch(`http://localhost:8000/api/v1/analysis/run?file_id=${fileId}&user_id=00000000-0000-0000-0000-000000000001`, {
        method: "POST"
      });

      if (!analysisRes.ok) {
        throw new Error(`분석 실행 실패 (HTTP ${analysisRes.status})`);
      }

      const analysisData = await analysisRes.json();
      const runId = analysisData.run_id;

      if (!runId) {
        throw new Error("분석 실행 ID를 받지 못했습니다.");
      }

      router.push(`/dashboard?run_id=${runId}`);
    } catch (err: any) {
      console.error("API connection failed:", err);
      setErrorMsg(err.message || "서버 연결에 실패했습니다.");
      setUploading(false);
    }
  };

  return (
    <PageShell active="upload" compact>
      <div className="mx-auto max-w-3xl">
        <SectionTitle
          eyebrow={`step ${step} of 3`}
          title="이제 실제 기록과 비교해볼 차례예요"
          description="자가진단 결과와 실제 시청 기록이 얼마나 다른지 확인해볼게요."
        />

        <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
          {prepItems.map((item, index) => (
            <div
              key={item}
              className={[
                "rounded-2xl border px-4 py-3 text-sm font-black",
                index + 1 <= step ? "border-slate-950 bg-slate-950 text-white" : "border-slate-200 bg-white text-slate-500"
              ].join(" ")}
            >
              {item}
            </div>
          ))}
        </div>

        <Card className="mt-6 p-6 md:p-8">
          {step === 1 && (
            <div className="space-y-6">
              <div className="rounded-3xl border border-teal-100 bg-teal-50 p-5">
                <div className="flex items-start gap-3">
                  <ShieldCheck className="mt-0.5 text-teal-700" size={24} />
                  <div>
                    <h2 className="text-lg font-black text-slate-950">개인정보 안내</h2>
                    <p className="mt-2 text-sm leading-6 text-slate-700">
                      브라우저 또는 업로드한 데이터 기준으로만 분석합니다. 원문 기록은 요약과 분류 중심으로 처리하며,
                      분석 데이터는 결과 생성 목적 외에는 사용하지 않아요.
                    </p>
                  </div>
                </div>
              </div>

              <label className="flex cursor-pointer items-start gap-3 rounded-3xl border border-slate-200 bg-[#fbfaf7] p-4">
                <input
                  type="checkbox"
                  checked={agreed}
                  onChange={(e) => setAgreed(e.target.checked)}
                  className="mt-1 h-5 w-5 rounded border-slate-300 text-slate-950 focus:ring-slate-900"
                />
                <span className="text-sm font-semibold leading-6 text-slate-700">
                  안내를 확인했고, 업로드한 기록을 미디어 성향 분석 목적으로 사용하는 것에 동의합니다.
                </span>
              </label>

              <Button type="button" className="w-full" disabled={!agreed} icon={<ArrowRight size={18} />} onClick={() => setStep(2)}>
                시청 기록 선택하기
              </Button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <label className="relative flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-[2rem] border-2 border-dashed border-slate-300 bg-[#fbfaf7] p-8 text-center transition hover:border-slate-500">
                <input
                  type="file"
                  accept=".json,.csv,.txt"
                  onChange={(e) => e.target.files && setFile(e.target.files[0])}
                  className="absolute inset-0 cursor-pointer opacity-0"
                />
                <FileUp size={38} className="text-slate-800" />
                <span className="mt-4 text-lg font-black text-slate-950">
                  {file ? file.name : "Google Takeout 시청 기록 파일을 올려주세요"}
                </span>
                <span className="mt-2 text-sm font-semibold text-slate-500">json, csv, txt 형식을 지원합니다.</span>
              </label>

              <div className="flex flex-col gap-3 sm:flex-row">
                <Button type="button" tone="secondary" icon={<ArrowLeft size={18} />} onClick={() => setStep(1)}>
                  이전
                </Button>
                <Button type="button" className="sm:flex-1" disabled={!file} icon={<ArrowRight size={18} />} onClick={() => setStep(3)}>
                  분석 준비 화면으로
                </Button>
              </div>
            </div>
          )}

          {step === 3 && (
            <form onSubmit={handleUpload} className="space-y-6">
              <div className="rounded-[2rem] border border-slate-200 bg-[#fbfaf7] p-6 text-center">
                <Play className="mx-auto text-slate-950" size={40} />
                <h2 className="mt-4 text-2xl font-black text-slate-950">내 알고리즘 리포트 만들기</h2>
                <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-slate-600">
                  파일 선택이 완료되었습니다. 이제 시청 기록을 정리하고 자가진단 결과와 비교해 대시보드 리포트를 생성합니다.
                </p>
              </div>

              {errorMsg && (
                <div className="rounded-3xl border border-rose-200 bg-rose-50 p-4 text-sm font-semibold leading-6 text-rose-700">
                  분석 중 오류가 발생했습니다. FastAPI 서버가 실행 중인지 확인해주세요.
                  <br />
                  <span className="text-xs">{errorMsg}</span>
                </div>
              )}

              <div className="flex flex-col gap-3 sm:flex-row">
                <Button type="button" tone="secondary" icon={<ArrowLeft size={18} />} onClick={() => setStep(2)}>
                  이전
                </Button>
                <Button type="submit" className="sm:flex-1" disabled={uploading} icon={<Play size={18} />}>
                  {uploading ? "분석 중..." : "기록 분석 시작하기"}
                </Button>
              </div>
            </form>
          )}
        </Card>
      </div>
    </PageShell>
  );
}
