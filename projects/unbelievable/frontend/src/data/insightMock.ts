export type SearchKeyword = {
  keyword: string;
  count: number;
  category: string;
};

export type CategoryShare = {
  name: string;
  value: number;
  tone: string;
};

export const searchKeywords: SearchKeyword[] = [
  { keyword: "쇼츠", count: 18, category: "콘텐츠" },
  { keyword: "야구", count: 12, category: "스포츠" },
  { keyword: "노트북 추천", count: 10, category: "IT" },
  { keyword: "디지털 디톡스", count: 8, category: "웰빙" },
  { keyword: "AI", count: 7, category: "기술" }
];

export const categoryShares: CategoryShare[] = [
  { name: "콘텐츠", value: 32, tone: "bg-rose-500" },
  { name: "스포츠", value: 22, tone: "bg-emerald-500" },
  { name: "IT", value: 18, tone: "bg-sky-500" },
  { name: "웰빙", value: 15, tone: "bg-amber-500" },
  { name: "기술", value: 13, tone: "bg-indigo-500" }
];

export const resultPreviewStats = [
  { label: "관심사 쏠림", value: "42점", caption: "주의 전 단계" },
  { label: "생각과 기록 차이", value: "18점", caption: "낮은 편" },
  { label: "사용자 주도성", value: "64%", caption: "직접 탐색 우세" },
  { label: "관심 다양성", value: "5개", caption: "주요 카테고리" }
];

export const reportInsights = [
  "검색어는 직접 찾은 관심사, 시청 기록은 알고리즘이 보여준 관심사예요.",
  "두 데이터를 비교하면 내가 원한 관심사와 피드가 밀어준 관심사의 차이를 볼 수 있어요.",
  "직접 탐색 비중은 높지만 특정 주제 반복 노출이 감지되었습니다."
];

