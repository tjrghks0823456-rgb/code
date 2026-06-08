-- ==========================================
--  언블리버블 (Unbelievable) Supabase Database Schema
--  Target: Supabase Postgres (with JSONB support)
--  
--  [보안 중요 규칙]
--  절대 실제 Supabase Secret Key, API Key, 또는 기타 개인정보를
--  본 SQL 파일 또는 임의의 공개 문서/소스코드에 하드코딩하여 포함하지 마십시오.
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
    survey_result JSONB DEFAULT NULL,         -- 자가진단 상세 응답 결과 백업
    raw_survey JSONB DEFAULT NULL,            -- 자가진단 전체 데이터 백업
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. 원천 업로드 파일 메타데이터 테이블
CREATE TABLE IF NOT EXISTS public.raw_file (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    storage_path VARCHAR(500) NOT NULL,
    upload_status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, PROCESSING, SUCCESS, FAIL
    excluded_ad_count INTEGER DEFAULT 0,
    skipped_sources_with_reason JSONB DEFAULT '{}'::jsonb,
    ad_skip_summary JSONB DEFAULT '[]'::jsonb,
    data_coverage JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. 정규화 이벤트 테이블
CREATE TABLE IF NOT EXISTS public.norm_event (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID NOT NULL REFERENCES public.raw_file(id) ON DELETE CASCADE,
    event_time TIMESTAMP NOT NULL,
    time_delta_sec INTEGER, -- 시청 시간 분석용 체류시간 (초 단위)
    video_duration_sec INTEGER, -- 영상 총 길이 (초 단위)
    text_base TEXT NOT NULL, -- 제목 또는 검색어 등
    platform VARCHAR(50) DEFAULT 'youtube',
    action_type VARCHAR(20) DEFAULT 'view', -- view, search
    source_surface VARCHAR(50) DEFAULT 'unknown',
    source_type VARCHAR(50), -- watch_history, search_history 등
    content_format VARCHAR(30) DEFAULT 'unknown', -- shorts, standard_video, live, unknown
    intent_level VARCHAR(30) DEFAULT 'unknown', -- active_search, unknown
    raw_time VARCHAR(255), -- 원본 시간 문자열
    video_id VARCHAR(50), -- YouTube Video ID
    channel_name VARCHAR(255), -- 채널명
    channel_url VARCHAR(500), -- 채널 URL
    title_url VARCHAR(500), -- 비디오 URL
    source_confidence VARCHAR(50) DEFAULT 'unknown', -- surface 판정 신뢰도
    is_duration_estimated BOOLEAN DEFAULT FALSE,
    estimated_duration_sec INTEGER,
    raw_item JSONB DEFAULT '{}'::jsonb -- 원본 아이템 저장
);

-- 4. 30분 단위 병합 세션 텍스트 테이블
CREATE TABLE IF NOT EXISTS public.session_text (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES public.raw_file(id) ON DELETE CASCADE,
    aggregated_text TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    event_count INTEGER DEFAULT 0, -- 세션 내 이벤트 개수
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
    nlp_provider VARCHAR(50) DEFAULT 'gcp', -- gcp, rule_based_fallback
    local_category VARCHAR(100),
    category_confidence FLOAT,
    category_candidates JSONB DEFAULT '[]'::jsonb,
    category_source VARCHAR(100),
    keywords_json JSONB DEFAULT '[]'::jsonb,
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
    exception_codes VARCHAR(40)[] DEFAULT '{}', -- P01, P04, P05 등 예외코드 리스트
    sampling_metadata JSONB DEFAULT '{}'::jsonb, -- 세션 샘플링 메타데이터
    data_quality_flags VARCHAR(100)[] DEFAULT '{}', -- 데이터 품질 플래그
    information_bias_risk FLOAT DEFAULT 0.0,
    shorts_stimulation_risk FLOAT DEFAULT 0.0,
    final_detox_risk FLOAT DEFAULT 0.0,
    shorts_analysis JSONB DEFAULT '{}'::jsonb,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. 6축 세부 점수 테이블
CREATE TABLE IF NOT EXISTS public.score_axis (
    axis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES public.score_run(run_id) ON DELETE CASCADE,
    axis_code VARCHAR(3) NOT NULL, -- TDS, SBS, EBS, VOS, SMS, UAS
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

-- 11. 사용자 관심사 분류 수정 피드백 테이블 (Phase 6)
-- 이 테이블은 DB가 스스로 실시간 학습하는 것이 아니라, 사용자가 직접 수정한 피드백 데이터를 누적하고,
-- 향후 딥러닝 임베딩 모델 및 다중 라벨링 모델의 재학습 데이터셋(Dataset) 구축에 활용하기 위한 목적입니다.
CREATE TABLE IF NOT EXISTS public.content_classification_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    event_id UUID REFERENCES public.norm_event(id) ON DELETE SET NULL,
    content_text TEXT NOT NULL,                      -- 원본 비디오 제목 또는 검색 텍스트
    predicted_category_l1 VARCHAR(100),          -- 예측 대분류
    predicted_category_l2 VARCHAR(100),          -- 예측 소분류
    corrected_category_l1 VARCHAR(100) NOT NULL, -- 사용자가 교정한 대분류
    corrected_category_l2 VARCHAR(100),          -- 사용자가 교정한 소분류
    confidence VARCHAR(20) DEFAULT 'low',        -- 당시 예측 신뢰도
    feedback_reason TEXT,                        -- 교정 이유 또는 추가 의견
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
CREATE INDEX IF NOT EXISTS idx_feedback_user ON public.content_classification_feedback(user_id);

-- ==========================================
--  Supabase RLS (Row Level Security) Policies
--  Only owners can access their own data
-- ==========================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.raw_file ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.score_run ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.detox_plan ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_classification_feedback ENABLE ROW LEVEL SECURITY;

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

-- Feedback Policies
CREATE POLICY "Users can manage their own feedback entries" ON public.content_classification_feedback
    FOR ALL USING (auth.uid() = user_id);

-- ==========================================
--  Seed Data (profiles 기본 사용자 seed만 포함)
-- ==========================================
INSERT INTO public.profiles (id, email, nickname, birth_year, survey_scores)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'seokhwan.son@gmail.com',
    '손석환',
    1999,
    '{"TDS": 70, "SBS": 60, "EBS": 50, "VOS": 65, "SMS": 80, "UAS": 55}'::jsonb
)
ON CONFLICT (id) DO UPDATE
SET email = EXCLUDED.email,
    nickname = EXCLUDED.nickname,
    birth_year = EXCLUDED.birth_year,
    survey_scores = EXCLUDED.survey_scores;
