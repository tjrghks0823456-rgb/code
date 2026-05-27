-- ==========================================
--  언블리버블 (Unbelievable) Database Schema
--  Target: Supabase Postgres (with JSONB support)
-- ==========================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. 사용자 프로필 테이블
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    nickname VARCHAR(100) NOT NULL,
    birth_year SMALLINT,
    survey_scores JSONB DEFAULT '{}'::jsonb, -- 사전 주관적 인식 자가진단 설문 점수 저장
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. 원천 업로드 파일 메타데이터 테이블
CREATE TABLE IF NOT EXISTS public.raw_file (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    storage_path VARCHAR(500) NOT NULL,
    upload_status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, PROCESSING, SUCCESS, FAIL
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. 정규화 이벤트 테이블
CREATE TABLE IF NOT EXISTS public.norm_event (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID NOT NULL REFERENCES public.raw_file(id) ON DELETE CASCADE,
    event_time TIMESTAMP NOT NULL,
    time_delta_sec INTEGER, -- 시청 시간 분석용 체류시간 (초 단위)
    text_base TEXT NOT NULL, -- 제목 또는 검색어 등
    platform VARCHAR(50) DEFAULT 'youtube',
    action_type VARCHAR(20) DEFAULT 'view', -- view, search
    source_surface VARCHAR(50) -- home, search, autoplay, etc.
);

-- 4. 30분 단위 병합 세션 텍스트 테이블
CREATE TABLE IF NOT EXISTS public.session_text (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES public.raw_file(id) ON DELETE CASCADE,
    aggregated_text TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL
);

-- 5. Cloud NL API 정량 분석 결과 테이블 (역정규화 JSONB 적재)
CREATE TABLE IF NOT EXISTS public.nlp_result (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES public.session_text(id) ON DELETE CASCADE,
    categories_json JSONB NOT NULL, -- content classification category paths
    sentiment_score FLOAT NOT NULL, -- -1.0 ~ 1.0
    sentiment_magnitude FLOAT DEFAULT 0.0,
    language_code VARCHAR(10) DEFAULT 'ko',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. 1회차 종합 점수 분석 결과 테이블
CREATE TABLE IF NOT EXISTS public.score_run (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    file_id UUID REFERENCES public.raw_file(id) ON DELETE CASCADE,
    bias_risk_score FLOAT NOT NULL, -- 최종 편향 위험도 종합 점수 (0 ~ 100)
    weighted_health FLOAT NOT NULL, -- 6축 가중합 종합 건강 점수 (0 ~ 100)
    mbti_type VARCHAR(10) NOT NULL, -- 16가지 미디어 소비 성향 유형 (예: INTP)
    exception_codes VARCHAR(20)[] DEFAULT '{}', -- P01, P04, P05 등 예외코드 리스트
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. 6축 세부 점수 테이블
CREATE TABLE IF NOT EXISTS public.score_axis (
    axis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES public.score_run(run_id) ON DELETE CASCADE,
    axis_code VARCHAR(3) NOT NULL, -- TDS (주제다양성), SBS (출처균형), EBS (감정균형), VOS (관점개방성), SMS (유해안전), UAS (사용자주도성)
    axis_value FLOAT NOT NULL DEFAULT 0.0, -- 0.0 ~ 100.0
    axis_grade VARCHAR(10), -- High, Medium, Low
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(run_id, axis_code)
);

-- 8. LLM 생성 맞춤형 디톡스 플랜 테이블
CREATE TABLE IF NOT EXISTS public.detox_plan (
    plan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES public.score_run(run_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    reverse_queries JSONB NOT NULL DEFAULT '[]'::jsonb, -- Gemini 추천 대체 검색어
    mission_json JSONB NOT NULL, -- 3일/7일 액션 미션 구조화 데이터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. 미션 수행 로그 테이블
CREATE TABLE IF NOT EXISTS public.mission_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id UUID NOT NULL REFERENCES public.detox_plan(plan_id) ON DELETE CASCADE,
    mission_item_id VARCHAR(100) NOT NULL, -- mission_json 내의 미션 항목 고유 ID
    completed_yn BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP
);

-- 10. 외부 API 호출 및 민감 이벤트 감사 로그
CREATE TABLE IF NOT EXISTS public.audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL, -- API_CALL, DELETE_DATA, AUTH_EVENT
    target_id UUID,
    status_code INTEGER,
    latency_ms INTEGER,
    provider VARCHAR(50), -- Cloud NL, Gemini, YouTube
    error_code VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
--  Indexes for performance optimization
-- ==========================================
CREATE INDEX IF NOT EXISTS idx_norm_event_file ON public.norm_event(file_id);
CREATE INDEX IF NOT EXISTS idx_nlp_result_session ON public.nlp_result(session_id);
CREATE INDEX IF NOT EXISTS idx_score_run_user ON public.score_run(user_id);
CREATE INDEX IF NOT EXISTS idx_score_axis_run ON public.score_axis(run_id);
CREATE INDEX IF NOT EXISTS idx_detox_plan_run ON public.detox_plan(run_id);
CREATE INDEX IF NOT EXISTS idx_mission_log_plan ON public.mission_log(plan_id);

-- ==========================================
--  Supabase RLS (Row Level Security) Policies
--  Only owners can access their own data
-- ==========================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.raw_file ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.score_run ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.detox_plan ENABLE ROW LEVEL SECURITY;

-- Profiles Policies
CREATE POLICY "Users can view and update their own profile" ON public.profiles
    FOR ALL USING (auth.uid() = id);

-- Raw File Policies
CREATE POLICY "Users can manage their own files" ON public.raw_file
    FOR ALL USING (auth.uid() = user_id);

-- Score Run Policies
CREATE POLICY "Users can view their own score runs" ON public.score_run
    FOR ALL USING (auth.uid() = user_id);

-- Detox Plan Policies
CREATE POLICY "Users can manage their own detox plans" ON public.detox_plan
    FOR ALL USING (auth.uid() = user_id);
