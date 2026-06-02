"use client";

import React, { useState, useRef } from "react";
import { ArrowLeft, ArrowRight, FileUp, Play, ShieldCheck, FolderUp, Archive, AlertCircle, CheckCircle2, BarChart3, Flame, Music, RotateCcw } from "lucide-react";
import { useRouter } from "next/navigation";
import PageShell from "../../components/PageShell";
import { Button } from "../../components/Button";
import Card from "../../components/Card";
import SectionTitle from "../../components/SectionTitle";
import { API_BASE_URL, DEFAULT_USER_ID } from "../../utils/apiConfig";
import { loadSelfSurveyResult } from "../../utils/surveyStorage";

type YoutubeFileKind = "watch" | "search" | "subscription" | "playlist" | "comment" | "liveChat" | "channel" | "music" | "unknown";

type DetectedYoutubeFile = {
  file: File;
  name: string;
  relativePath: string;
  kind: YoutubeFileKind;
};

const YOUTUBE_HINTS = [
  "youtube",
  "youtube and youtube music",
  "watch-history",
  "search-history",
  "history",
  "subscriptions",
  "subscription",
  "playlists",
  "playlist",
  "comments",
  "comment",
  "live_chat",
  "live chat",
  "channels",
  "channel",
  "시청 기록",
  "검색 기록",
  "구독정보",
  "구독 정보",
  "재생목록",
  "재생 목록",
  "댓글",
  "실시간 채팅",
  "실시간채팅",
  "채널",
  "music (library and uploads)",
];

const kindMeta: Record<YoutubeFileKind, { label: string; dot: string; badge: string }> = {
  watch: { label: "시청 기록", dot: "bg-rose-500", badge: "text-rose-700 bg-rose-50 border-rose-100" },
  search: { label: "검색 기록", dot: "bg-blue-500", badge: "text-blue-700 bg-blue-50 border-blue-100" },
  subscription: { label: "구독 정보", dot: "bg-teal-500", badge: "text-teal-700 bg-teal-50 border-teal-100" },
  playlist: { label: "재생목록", dot: "bg-violet-500", badge: "text-violet-700 bg-violet-50 border-violet-100" },
  comment: { label: "댓글", dot: "bg-amber-500", badge: "text-amber-700 bg-amber-50 border-amber-100" },
  liveChat: { label: "실시간 채팅", dot: "bg-emerald-500", badge: "text-emerald-700 bg-emerald-50 border-emerald-100" },
  channel: { label: "채널", dot: "bg-cyan-500", badge: "text-cyan-700 bg-cyan-50 border-cyan-100" },
  music: { label: "음악 제외", dot: "bg-slate-300", badge: "text-slate-500 bg-slate-50 border-slate-100" },
  unknown: { label: "후보 파일", dot: "bg-slate-400", badge: "text-slate-600 bg-slate-50 border-slate-100" },
};

function isUploadableKind(kind: YoutubeFileKind): boolean {
  return kind !== "music" && kind !== "unknown";
}

function getRelativePath(file: File): string {
  return (file as any).webkitRelativePath || file.name;
}

function detectYoutubeKind(path: string): YoutubeFileKind {
  const normalized = path.replace(/\\/g, "/").toLowerCase();
  const fileName = normalized.split("/").pop() ?? normalized;

  if (normalized.includes("search-history") || fileName.includes("검색 기록")) return "search";
  if (normalized.includes("watch-history") || fileName.includes("시청 기록") || normalized.includes("/시청 기록/")) return "watch";
  if (normalized.includes("subscriptions") || normalized.includes("subscription") || normalized.includes("구독정보") || normalized.includes("구독 정보")) return "subscription";
  if (normalized.includes("playlists") || normalized.includes("playlist") || normalized.includes("재생목록") || normalized.includes("재생 목록")) return "playlist";
  if (normalized.includes("comments") || normalized.includes("comment") || normalized.includes("댓글")) return "comment";
  if (normalized.includes("live_chat") || normalized.includes("live chat") || normalized.includes("실시간 채팅") || normalized.includes("실시간채팅")) return "liveChat";
  if (normalized.includes("channels") || normalized.includes("channel") || normalized.includes("채널")) return "channel";
  if (normalized.includes("music (library and uploads)") || normalized.includes("music-library") || normalized.includes("music_uploads") || normalized.includes("music uploads")) return "music";
  return "unknown";
}

function isYoutubeCandidate(file: File): boolean {
  const path = getRelativePath(file).toLowerCase();
  const name = file.name.toLowerCase();

  const isSupported =
    name.endsWith(".json") ||
    name.endsWith(".html") ||
    name.endsWith(".csv") ||
    name.endsWith(".txt") ||
    name.endsWith(".zip");

  if (!isSupported) return false;

  return YOUTUBE_HINTS.some((hint) => path.includes(hint));
}

function detectYoutubeFiles(files: File[]): DetectedYoutubeFile[] {
  return files
    .filter(isYoutubeCandidate)
    .map((file) => {
      const relativePath = getRelativePath(file);
      return {
        file,
        name: file.name,
        relativePath,
        kind: detectYoutubeKind(relativePath),
      };
    });
}

const prepItems = ["파일 준비", "개인정보 안내 확인", "시청 기록 선택", "분석 준비 완료"];

export default function UploadPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [agreed, setAgreed] = useState(false);

  // Custom multi-option state
  const [detectedFiles, setDetectedFiles] = useState<DetectedYoutubeFile[]>([]);
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);

  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadSummary, setUploadSummary] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Ref callback for webkitdirectory setup to avoid React TS type errors
  const folderInputRef = useRef<HTMLInputElement | null>(null);
  const setFolderRef = (el: HTMLInputElement | null) => {
    folderInputRef.current = el;
    if (el) {
      el.setAttribute("webkitdirectory", "");
      el.setAttribute("directory", "");
    }
  };

  const handleFolderUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files ?? []);
    if (selected.length === 0) return;

    const detected = detectYoutubeFiles(selected);
    const uploadable = detected.filter((item) => isUploadableKind(item.kind));
    setSelectedFiles(selected);
    setDetectedFiles(detected);
    setZipFile(null); // Clear zip if folder uploaded

    if (detected.length === 0) {
      setErrorMsg(
        "YouTube 시청 기록 파일을 찾지 못했습니다. Google Takeout에 YouTube 기록이 포함되어 있는지 확인해주세요."
      );
      return;
    }

    if (uploadable.length === 0) {
      setErrorMsg(
        "분석 가능한 YouTube 기록 파일을 찾지 못했습니다. 음악 폴더만 선택된 경우 시청 기록, 검색 기록, 댓글, 구독정보, 재생목록 폴더가 함께 포함되어야 합니다."
      );
      return;
    }

    setErrorMsg(null);
  };

  const handleZipUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".zip")) {
      setErrorMsg("ZIP 파일만 업로드할 수 있습니다.");
      return;
    }

    // Front-end limit validation
    if (file.size > 150 * 1024 * 1024) {
      setErrorMsg("업로드 파일 용량이 너무 큽니다. 필요한 YouTube 기록 파일만 포함된 Takeout 파일을 사용해주세요.");
      return;
    }

    setZipFile(file);
    setDetectedFiles([]); // Clear folder files if zip uploaded
    setSelectedFiles([]);
    setErrorMsg(null);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const items = Array.from(e.dataTransfer.files);

      // If there is only one file and it is a ZIP
      if (items.length === 1 && items[0].name.toLowerCase().endsWith(".zip")) {
        const file = items[0];
        if (file.size > 150 * 1024 * 1024) {
          setErrorMsg("업로드 파일 용량이 너무 큽니다. 필요한 YouTube 기록 파일만 포함된 Takeout 파일을 사용해주세요.");
          return;
        }
        setZipFile(file);
        setDetectedFiles([]);
        setSelectedFiles([]);
        setErrorMsg(null);
      } else {
        // Treat as files drop
        const detected = detectYoutubeFiles(items);
        const uploadable = detected.filter((item) => isUploadableKind(item.kind));
        setSelectedFiles(items);
        setDetectedFiles(detected);
        setZipFile(null);

        if (detected.length === 0) {
          setErrorMsg("YouTube 시청 기록 파일을 찾지 못했습니다. Google Takeout에 YouTube 기록이 포함되어 있는지 확인해주세요.");
          return;
        }
        if (uploadable.length === 0) {
          setErrorMsg("분석 가능한 YouTube 기록 파일을 찾지 못했습니다. 음악 폴더만 선택된 경우 다른 기록 폴더도 함께 포함해주세요.");
          return;
        }
        setErrorMsg(null);
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!zipFile && uploadableFiles.length === 0) return;

    setUploading(true);
    setErrorMsg(null);

    try {
      // 1. Upload Folder or ZIP via FormData
      const formData = new FormData();

      if (zipFile) {
        formData.append("zip_file", zipFile);
      } else {
        uploadableFiles.forEach((item) => {
          formData.append("files", item.file);
          formData.append("paths", item.relativePath);
        });
      }

      // Load survey results from localStorage and append
      const surveyResult = loadSelfSurveyResult();
      if (surveyResult) {
        formData.append("survey_scores", JSON.stringify(surveyResult));
      }

      const uploadRes = await fetch(`${API_BASE_URL}/api/v1/upload/takeout?user_id=${DEFAULT_USER_ID}`, {
        method: "POST",
        body: formData,
      });

      if (!uploadRes.ok) {
        const errorData = await uploadRes.json().catch(() => null);
        throw new Error(errorData?.detail || `업로드 분석 요청에 실패했습니다. (HTTP ${uploadRes.status})`);
      }

      const uploadData = await uploadRes.json();
      if (!uploadData.file_id) {
        throw new Error("서버로부터 파일 ID를 전달받지 못했습니다.");
      }

      setUploadSummary(uploadData);
      setUploading(false);
    } catch (err: any) {
      console.error("API connection failed:", err);
      setErrorMsg(err.message || "서버 연결에 실패했습니다.");
      setUploading(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (!uploadSummary?.file_id) return;

    setAnalyzing(true);
    setErrorMsg(null);

    try {
      // 2. Trigger Analysis Calculation
      const analysisRes = await fetch(`${API_BASE_URL}/api/v1/analysis/run?file_id=${uploadSummary.file_id}&user_id=${DEFAULT_USER_ID}`, {
        method: "POST",
      });

      if (!analysisRes.ok) {
        const errorData = await analysisRes.json().catch(() => null);
        throw new Error(errorData?.detail || `정량 편향 분석 실행 실패 (HTTP ${analysisRes.status})`);
      }

      const analysisData = await analysisRes.json();
      const runId = analysisData.run_id;

      if (!runId) {
        throw new Error("분석 실행 ID(run_id) 수신 실패");
      }

      setAnalyzing(false);
      router.push(`/dashboard?run_id=${runId}`);
    } catch (err: any) {
      console.error("Analysis execution failed:", err);
      setErrorMsg(err.message || "분석 실행에 실패했습니다.");
      setAnalyzing(false);
    }
  };

  const uploadableFiles = detectedFiles.filter((file) => isUploadableKind(file.kind));
  const hasValidData = zipFile !== null || uploadableFiles.length > 0;

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

              {/* Hidden native file inputs */}
              <input
                ref={setFolderRef}
                type="file"
                multiple
                onChange={handleFolderUpload}
                className="hidden"
              />
              <input
                type="file"
                accept=".zip"
                onChange={handleZipUpload}
                className="hidden"
                id="zip-file-input"
              />

              {/* Drag & Drop Area */}
              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                className={`group relative flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-[2rem] border-2 border-dashed p-8 text-center transition ${
                  dragActive
                    ? "border-slate-950 bg-slate-100 scale-[1.01]"
                    : "border-slate-300 bg-[#fbfaf7] hover:border-slate-500"
                }`}
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-200 text-slate-800 mb-3 group-hover:scale-110 transition-transform">
                  <FileUp size={28} />
                </div>
                <span className="text-lg font-black text-slate-950">
                  Google Takeout 폴더나 ZIP 파일을 업로드하세요
                </span>
                <span className="mt-2 text-xs font-semibold text-slate-500 max-w-md">
                  파일을 하나씩 찾을 필요 없이 Takeout 폴더 또는 ZIP 파일을 올리면 필요한 시청 기록 파일을 알아서 탐색합니다.
                </span>

                {/* Action Buttons inside Dropzone */}
                <div className="mt-5 flex flex-wrap gap-2.5 justify-center z-10">
                  <button
                    type="button"
                    onClick={() => folderInputRef.current?.click()}
                    className="inline-flex items-center gap-1.5 rounded-2xl bg-slate-950 px-4 py-2.5 text-xs font-black text-white hover:bg-slate-850 transition-colors shadow-sm"
                  >
                    <FolderUp size={14} /> Takeout 폴더 선택
                  </button>
                  <button
                    type="button"
                    onClick={() => document.getElementById("zip-file-input")?.click()}
                    className="inline-flex items-center gap-1.5 rounded-2xl border border-slate-300 bg-white px-4 py-2.5 text-xs font-black text-slate-800 hover:bg-slate-50 transition-colors shadow-sm"
                  >
                    <Archive size={14} /> ZIP 파일 선택
                  </button>
                </div>

                <span className="mt-4 text-[10px] text-slate-400 font-semibold">
                  또는 여기에 폴더나 ZIP 파일을 끌어다 놓으세요
                </span>
              </div>

              {/* Error Message Card */}
              {errorMsg && (
                <div className="rounded-3xl border border-rose-200 bg-rose-50 p-4 flex gap-2.5 items-start animate-shake">
                  <AlertCircle className="mt-0.5 text-rose-700 shrink-0" size={18} />
                  <div>
                    <p className="text-xs font-bold text-rose-800 mb-0.5">업로드 파일 감지 오류</p>
                    <p className="text-xs text-rose-700 font-medium leading-relaxed">{errorMsg}</p>
                    <p className="text-[10px] text-slate-500 mt-1.5">
                      해결 안내: 내보낸 Google Takeout 폴더 내에 `YouTube` 및 `watch-history.json` / `watch-history.html` 파일이 포함되어 있는지 확인해주세요.
                    </p>
                  </div>
                </div>
              )}

              {/* Detected Results Card */}
              {hasValidData && (
                <div className="rounded-3xl border border-slate-200 bg-white p-5 space-y-3 shadow-sm">
                  <div className="flex justify-between items-center border-b border-slate-100 pb-2.5">
                    <h3 className="text-xs font-black tracking-wider text-slate-900 flex items-center gap-1.5">
                      <FileUp size={14} className="text-slate-700" />
                      감지된 파일 결과
                    </h3>
                    <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                      분석 대상 파일: {zipFile ? 1 : uploadableFiles.length}개
                    </span>
                  </div>

                  {zipFile ? (
                    <div className="flex items-center justify-between bg-[#fbfaf7] p-3 rounded-2xl border border-slate-100">
                      <div className="flex items-center gap-2.5 min-w-0">
                        <Archive size={18} className="text-slate-700" />
                        <div className="min-w-0">
                          <p className="text-xs font-black text-slate-950 truncate">{zipFile.name}</p>
                          <p className="text-[10px] text-slate-500 mt-0.5">
                            {(zipFile.size / 1024 / 1024).toFixed(2)} MB • ZIP 파일 업로드 대기 완료
                          </p>
                        </div>
                      </div>
                      <span className="text-[9px] font-black text-teal-700 bg-teal-50 border border-teal-100 px-2 py-0.5 rounded-full shrink-0">
                        서버 내부 스캔 대기
                      </span>
                    </div>
                  ) : (
                    <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                      {detectedFiles.map((item, idx) => {
                        const meta = kindMeta[item.kind];
                        return (
                        <div key={`${item.kind}-${idx}`} className="flex items-center justify-between bg-[#fbfaf7] p-2.5 rounded-2xl border border-slate-100">
                          <div className="flex items-center gap-2.5 min-w-0">
                            <span className={`h-2 w-2 rounded-full ${meta.dot} shrink-0`} />
                            <div className="min-w-0">
                              <p className="text-xs font-black text-slate-950 truncate">{item.name}</p>
                              <p className="text-[10px] text-slate-500 truncate">{item.relativePath}</p>
                            </div>
                          </div>
                          <span className={`text-[9px] font-black border px-2 py-0.5 rounded-full shrink-0 ${meta.badge}`}>
                            {meta.label}
                          </span>
                        </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              <div className="flex flex-col gap-3 sm:flex-row">
                <Button type="button" tone="secondary" icon={<ArrowLeft size={18} />} onClick={() => setStep(1)}>
                  이전
                </Button>
                <Button
                  type="button"
                  className="sm:flex-1"
                  disabled={!hasValidData}
                  icon={<ArrowRight size={18} />}
                  onClick={() => setStep(3)}
                >
                  분석 준비 화면으로
                </Button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              {!uploadSummary ? (
                <form onSubmit={handleUpload} className="space-y-6">
                  <div className="rounded-[2rem] border border-slate-200 bg-[#fbfaf7] p-6 text-center">
                    <Play className="mx-auto text-slate-950" size={40} />
                    <h2 className="mt-4 text-2xl font-black text-slate-950">내 알고리즘 리포트 만들기</h2>
                    <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-slate-600">
                      파일 선택이 완료되었습니다. 이제 시청 기록을 정리하고 자가진단 결과와 비교해 대시보드 리포트를 생성합니다.
                    </p>

                    <div className="mt-5 pt-4 border-t border-slate-200/65 text-left max-w-sm mx-auto space-y-2.5">
                      <div className="flex items-center gap-2 text-xs text-slate-500 font-semibold">
                        <CheckCircle2 size={14} className="text-emerald-600" /> 개인정보 보안 및 수집 동의 완료
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-800 font-black">
                        <CheckCircle2 size={14} className="text-emerald-600" /> {zipFile ? `ZIP 파일 대기 완료 (${zipFile.name})` : `YouTube 분석 파일 감지 완료 (${uploadableFiles.length}개)`}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-500 font-semibold">
                        <CheckCircle2 size={14} className="text-emerald-600" /> 짧은 노출 추정 필터 적용 대기 중
                      </div>
                    </div>
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
                      {uploading ? "업로드 및 데이터 정제 중..." : "기록 분석 시작하기"}
                    </Button>
                  </div>
                </form>
              ) : (
                <div className="space-y-6 animate-fadeIn">
                  {/* Summary Card */}
                  <div className="rounded-[2rem] border border-slate-900 bg-slate-950 p-6 md:p-8 text-white relative overflow-hidden shadow-2xl">
                    {/* Glowing background decor */}
                    <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-teal-500/10 blur-3xl" />
                    <div className="absolute -left-16 -bottom-16 h-48 w-48 rounded-full bg-indigo-500/10 blur-3xl" />

                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-teal-500/20 text-teal-400">
                        <CheckCircle2 size={24} />
                      </div>
                      <div>
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-teal-400">Step 3 Complete</span>
                        <h2 className="text-2xl font-black tracking-tight mt-0.5">시청 데이터 정제 완료!</h2>
                      </div>
                    </div>

                    <p className="mt-4 text-xs font-medium leading-relaxed text-slate-300 max-w-xl">
                      업로드된 Google Takeout 분석이 성공적으로 마무리되었습니다.
                      관심사 분석에 왜곡을 일으킬 수 있는 음악 데이터를 제외하고 시청 유형별로 분류를 마쳤습니다.
                    </p>

                    {/* Stats Grid */}
                    <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
                      <div className="rounded-2xl bg-white/5 border border-white/10 p-3.5 hover:bg-white/10 transition-colors">
                        <span className="text-[10px] font-bold text-slate-400 block">시청 기록</span>
                        <span className="text-lg font-black mt-1 block text-rose-400">
                          {uploadSummary.parsed_source_counts?.watch_history || 0}건
                        </span>
                      </div>
                      <div className="rounded-2xl bg-white/5 border border-white/10 p-3.5 hover:bg-white/10 transition-colors">
                        <span className="text-[10px] font-bold text-slate-400 block">검색 기록</span>
                        <span className="text-lg font-black mt-1 block text-blue-400">
                          {uploadSummary.parsed_source_counts?.search_history || 0}건
                        </span>
                      </div>
                      <div className="rounded-2xl bg-white/5 border border-white/10 p-3.5 hover:bg-white/10 transition-colors">
                        <span className="text-[10px] font-bold text-slate-400 block">구독 정보</span>
                        <span className="text-lg font-black mt-1 block text-teal-400">
                          {uploadSummary.parsed_source_counts?.subscription || 0}개
                        </span>
                      </div>
                      <div className="rounded-2xl bg-white/5 border border-white/10 p-3.5 hover:bg-white/10 transition-colors">
                        <span className="text-[10px] font-bold text-slate-400 block">재생목록</span>
                        <span className="text-lg font-black mt-1 block text-violet-400">
                          {uploadSummary.parsed_source_counts?.playlist || 0}개
                        </span>
                      </div>
                      <div className="rounded-2xl bg-white/5 border border-white/10 p-3.5 hover:bg-white/10 transition-colors">
                        <span className="text-[10px] font-bold text-slate-400 block">댓글</span>
                        <span className="text-lg font-black mt-1 block text-amber-400">
                          {uploadSummary.parsed_source_counts?.comment || 0}건
                        </span>
                      </div>
                      <div className="rounded-2xl bg-white/5 border border-white/10 p-3.5 hover:bg-white/10 transition-colors">
                        <span className="text-[10px] font-bold text-slate-400 block">실시간 채팅</span>
                        <span className="text-lg font-black mt-1 block text-emerald-400">
                          {uploadSummary.parsed_source_counts?.live_chat || 0}건
                        </span>
                      </div>
                      <div className="rounded-2xl bg-white/5 border border-white/10 p-3.5 hover:bg-white/10 transition-colors">
                        <span className="text-[10px] font-bold text-slate-400 block">채널</span>
                        <span className="text-lg font-black mt-1 block text-cyan-400">
                          {uploadSummary.parsed_source_counts?.channel || 0}개
                        </span>
                      </div>
                    </div>

                    <div className="mt-3 flex items-center justify-between rounded-2xl bg-orange-500/10 border border-orange-400/20 px-4 py-3">
                      <span className="text-xs font-bold text-orange-100">광고 출처 제외</span>
                      <span className="text-xs font-black text-orange-300">
                        {uploadSummary.excluded_ad_count || 0}건 분석 제외
                      </span>
                    </div>

                    {/* Session Splitting Stats */}
                    <div className="mt-4 flex items-center justify-between rounded-2xl bg-white/5 border border-white/10 px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Flame className="text-amber-400" size={16} />
                        <span className="text-xs font-bold text-slate-300">멀티 세션 타임슬라이스</span>
                      </div>
                      <span className="text-xs font-black text-amber-300">
                        {uploadSummary.session_count || 0}개 분석 세션 분류
                      </span>
                    </div>

                    {/* LocalStorage Survey Connection badge */}
                    {loadSelfSurveyResult() && (
                      <div className="mt-3 flex items-center justify-between rounded-2xl bg-teal-500/10 border border-teal-500/20 px-4 py-2.5">
                        <span className="inline-flex items-center gap-1.5 text-[10px] font-black text-teal-400">
                          <CheckCircle2 size={13} />
                          자가진단 연동 상태
                        </span>
                        <span className="text-xs font-black text-teal-300">
                          {loadSelfSurveyResult()?.resultName || "미디어 유형 분석"} 점수 동기화 완료
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Ignored / skipped source alert card */}
                  {((uploadSummary.ignored_sources && uploadSummary.ignored_sources.length > 0) || (uploadSummary.skipped_sources_with_reason && Object.keys(uploadSummary.skipped_sources_with_reason).length > 0)) && (
                    <div className="rounded-3xl border border-[#ece9df] bg-[#fbfaf7] p-5 space-y-3.5">
                      <div className="flex items-center gap-2 text-slate-900">
                        <Music className="text-teal-700" size={18} />
                        <h3 className="text-xs font-black tracking-wider">MVP 분석 필터 및 정제 제외 내역</h3>
                      </div>

                      <p className="text-xs leading-relaxed text-slate-600 font-medium">
                        핵심 시청 성향과 미디어 편향도 검출 정밀성을 높이기 위해, 음악 감상 이력(Music 라이브러리/업로드) 및 분석 무관 폴더는 노이즈 유입 방지 차원에서 MVP 분석 대상에서 배제 처리되었습니다.
                      </p>

                      <div className="space-y-1.5 max-h-32 overflow-y-auto pr-1">
                        {uploadSummary.ignored_sources?.slice(0, 5).map((path: string, i: number) => (
                          <div key={`ignored-${i}`} className="flex justify-between bg-white px-3 py-2 rounded-xl border border-slate-200/80 text-[10px]">
                            <span className="font-semibold text-slate-500 truncate max-w-[70%]">{path.split('/').pop()}</span>
                            <span className="font-black text-teal-700 shrink-0">Music 제외 완료</span>
                          </div>
                        ))}
                        {uploadSummary.skipped_sources_with_reason && Object.entries(uploadSummary.skipped_sources_with_reason).slice(0, 5).map(([path, reason]: [string, any], i: number) => (
                          <div key={`skipped-${i}`} className="flex justify-between bg-white px-3 py-2 rounded-xl border border-slate-200/80 text-[10px]">
                            <span className="font-semibold text-slate-500 truncate max-w-[65%]">{path.split('/').pop()}</span>
                            <span className="font-bold text-slate-400 shrink-0 truncate max-w-[30%]">제외: {reason}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {errorMsg && (
                    <div className="rounded-3xl border border-rose-200 bg-rose-50 p-4 text-sm font-semibold leading-6 text-rose-700 animate-shake">
                      분석 중 오류가 발생했습니다. FastAPI 서버가 실행 중인지 확인해주세요.
                      <br />
                      <span className="text-xs font-mono">{errorMsg}</span>
                    </div>
                  )}

                  {/* Submit / Trigger Analysis Button */}
                  <div className="flex flex-col gap-3 sm:flex-row pt-2">
                    <Button
                      type="button"
                      tone="secondary"
                      icon={<RotateCcw size={18} />}
                      disabled={analyzing}
                      onClick={() => {
                        setUploadSummary(null);
                        setStep(2);
                      }}
                    >
                      기록 다시 올리기
                    </Button>
                    <Button
                      type="button"
                      className="sm:flex-1 relative overflow-hidden bg-gradient-to-r from-teal-600 to-indigo-600 hover:from-teal-500 hover:to-indigo-500 text-white font-black shadow-lg shadow-teal-500/10 hover:shadow-teal-500/20 group transition-all"
                      disabled={analyzing}
                      icon={analyzing ? null : <BarChart3 size={18} className="group-hover:scale-110 transition-transform" />}
                      onClick={handleRunAnalysis}
                    >
                      {analyzing ? (
                        <div className="flex items-center justify-center gap-2">
                          <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                          <span>AI 미디어 디톡스 리포트 생성 중... (약 5초 소요)</span>
                        </div>
                      ) : (
                        "AI 미디어 리포트 발행하기"
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </Card>
      </div>
    </PageShell>
  );
}
