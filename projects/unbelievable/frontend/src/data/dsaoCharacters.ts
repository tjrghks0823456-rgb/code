export type DsaoCharacterColor =
  | "amber"
  | "blue"
  | "cyan"
  | "emerald"
  | "fuchsia"
  | "indigo"
  | "lime"
  | "orange"
  | "pink"
  | "purple"
  | "rose"
  | "sky"
  | "teal"
  | "violet";

export type DsaoCharacter = {
  code: string;
  name: string;
  title: string;
  animal: string;
  characterName: string;
  emoji: string;
  color: DsaoCharacterColor;
  imagePath?: string;
  oneLiner: string;
  shortDescription: string;
  strengths: string[];
  cautions: string[];
  recommendedAction: string[];
  accentColor: string;
  tags: string[];
  attention: string;
  recovery: string;
  visualConcept: string;
  consumptionPattern: string;
};

type BaseDsaoCharacter = Omit<
  DsaoCharacter,
  "title" | "animal" | "shortDescription" | "strengths" | "cautions" | "recommendedAction" | "accentColor"
>;

const baseDsaoCharacters: Record<string, BaseDsaoCharacter> = {
  DWSF: {
    code: "DWSF",
    name: "다채로운 숏폼 탐색형",
    characterName: "스파크",
    emoji: "✨",
    color: "amber",
    imagePath: "/characters/dwsf.png",
    oneLiner: "새로운 주제와 짧은 영상을 가볍게 넘나들며 호기심을 빠르게 넓히는 패턴입니다.",
    tags: ["#넓은탐색", "#숏폼", "#호기심"],
    attention: "탐색 폭이 넓은 만큼 기억에 남는 주제가 금방 흩어질 수 있어, 본 뒤 남는 포인트를 하나만 붙잡아두면 좋습니다.",
    recovery: "오늘 본 짧은 영상 중 다시 찾아볼 가치가 있는 주제 1개를 저장하거나 검색어로 남겨보세요.",
    visualConcept: "작은 불꽃이 여러 색의 길을 밝히며 빠르게 이동하는 이미지",
    consumptionPattern: "새로운 채널, 밈, 교양 클립을 빠르게 넘기며 흥미로운 주제를 발견합니다."
  },
  DWSL: {
    code: "DWSL",
    name: "다채로운 롱폼 탐색형",
    characterName: "아카이브",
    emoji: "🗂️",
    color: "violet",
    imagePath: "/characters/dwsl.png",
    oneLiner: "여러 분야의 긴 콘텐츠를 차곡차곡 모으며 지식의 맥락을 넓혀가는 패턴입니다.",
    tags: ["#롱폼", "#기록가", "#넓은지식"],
    attention: "관심사가 넓어질수록 시청 목록이 쌓이기 쉬우니, 볼 것과 보관할 것을 구분하는 루틴이 도움이 됩니다.",
    recovery: "긴 영상 하나를 본 뒤 핵심 문장 2개만 메모해 나만의 아카이브를 가볍게 정리해보세요.",
    visualConcept: "색색의 파일과 책갈피를 정돈하는 기록가 캐릭터",
    consumptionPattern: "다큐, 강연, 리뷰, 해설 영상을 주제별로 모아두고 천천히 살펴봅니다."
  },
  DWMF: {
    code: "DWMF",
    name: "지식 스낵 탐색형",
    characterName: "바이트",
    emoji: "🍪",
    color: "cyan",
    imagePath: "/characters/dwmf.png",
    oneLiner: "짧은 지식 콘텐츠를 효율적으로 골라 보며 일상 속 학습 밀도를 높이는 패턴입니다.",
    tags: ["#지식스낵", "#요약", "#효율탐색"],
    attention: "짧은 요약에 익숙해지면 긴 맥락을 확인할 기회가 줄 수 있어, 가끔은 원본 출처를 함께 확인하면 좋습니다.",
    recovery: "마음에 든 지식 스낵 하나를 골라 10분짜리 관련 영상이나 글로 한 단계만 더 확장해보세요.",
    visualConcept: "작은 큐브형 지식 조각을 빠르게 모으는 캐릭터",
    consumptionPattern: "과학, IT, 역사, 생활 팁을 짧은 요약 영상으로 빠르게 섭취합니다."
  },
  DWML: {
    code: "DWML",
    name: "깊이 있는 지식 항해형",
    characterName: "네비",
    emoji: "🧭",
    color: "blue",
    imagePath: "/characters/dwml.png",
    oneLiner: "스스로 방향을 잡고 긴 지식 콘텐츠를 탐색하며 깊은 이해를 쌓아가는 패턴입니다.",
    tags: ["#주도탐색", "#롱폼", "#깊은이해"],
    attention: "정해둔 관심 경로가 탄탄한 만큼, 다른 관점의 콘텐츠를 만나는 빈도는 낮아질 수 있습니다.",
    recovery: "익숙한 분야와 다른 주제의 입문 영상을 하나 골라 탐색 지도에 새 지점을 추가해보세요.",
    visualConcept: "나침반과 별자리를 들고 긴 항로를 그리는 탐험가",
    consumptionPattern: "강의, 다큐, 전문 해설을 직접 검색해 순서대로 따라가며 봅니다."
  },
  DNSF: {
    code: "DNSF",
    name: "특정 관심 숏폼 집중형",
    characterName: "핀",
    emoji: "📌",
    color: "rose",
    imagePath: "/characters/dnsf.png",
    oneLiner: "특정 관심사에 빠르게 반응하며 짧은 콘텐츠를 집중적으로 확인하는 패턴입니다.",
    tags: ["#관심고정", "#빠른반응", "#숏폼집중"],
    attention: "익숙한 관심사 주변에서 비슷한 영상이 이어지면 새로운 주제가 들어올 틈이 좁아질 수 있습니다.",
    recovery: "관심 키워드 옆에 낯선 보조 키워드 하나를 붙여 검색해보며 탐색 범위를 조금 넓혀보세요.",
    visualConcept: "지도 위 한 지점을 정확히 찍고 주변을 빠르게 스캔하는 캐릭터",
    consumptionPattern: "좋아하는 장르, 크리에이터, 이슈의 짧은 클립을 연속해서 확인합니다."
  },
  DNSL: {
    code: "DNSL",
    name: "특정 주제 장기 몰입형",
    characterName: "딥",
    emoji: "🔎",
    color: "indigo",
    imagePath: "/characters/dnsl.png",
    oneLiner: "하나의 주제를 오래 파고들며 세부 맥락을 깊게 이해하려는 탐구형 패턴입니다.",
    tags: ["#주제몰입", "#장기시청", "#탐구형"],
    attention: "한 주제에 오래 머물수록 다른 해석이나 배경 정보가 뒤늦게 보일 수 있어 출처를 넓히는 습관이 유용합니다.",
    recovery: "같은 주제를 다루는 다른 채널의 차분한 설명 영상을 하나 더해 균형 있게 비교해보세요.",
    visualConcept: "돋보기와 노트를 들고 한 주제를 깊게 관찰하는 캐릭터",
    consumptionPattern: "한 사건, 취미, 분야의 긴 영상과 관련 영상을 이어 보며 맥락을 쌓습니다."
  },
  DNMF: {
    code: "DNMF",
    name: "전문 정보 압축형",
    characterName: "칩",
    emoji: "💠",
    color: "emerald",
    imagePath: "/characters/dnmf.png",
    oneLiner: "필요한 전문 정보를 짧고 정확하게 수집해 실용적인 답을 빠르게 얻는 패턴입니다.",
    tags: ["#전문정보", "#압축학습", "#실용탐색"],
    attention: "필요한 정보만 빠르게 모으다 보면 배경 맥락이나 다른 사례를 살펴볼 시간이 부족할 수 있습니다.",
    recovery: "짧은 튜토리얼을 본 뒤 관련 공식 문서나 긴 설명 영상의 목차를 한 번 훑어보세요.",
    visualConcept: "반짝이는 칩 안에 핵심 정보가 정리되는 캐릭터",
    consumptionPattern: "코딩, 장비, 도구 사용법 같은 실용 정보를 짧은 영상으로 압축해서 봅니다."
  },
  DNML: {
    code: "DNML",
    name: "한우물 연구형",
    characterName: "루트",
    emoji: "🌱",
    color: "teal",
    imagePath: "/characters/dnml.png",
    oneLiner: "특정 분야를 꾸준히 깊게 탐색하며 뿌리부터 이해를 넓혀가는 패턴입니다.",
    tags: ["#한우물", "#연구형", "#꾸준탐색"],
    attention: "익숙한 분야의 깊이는 강점이지만, 가벼운 휴식형 콘텐츠가 부족하면 시청 경험이 단조로워질 수 있습니다.",
    recovery: "같은 분야의 입문자용 영상이나 전혀 다른 취미 영상을 짧게 보며 리듬을 환기해보세요.",
    visualConcept: "뿌리를 깊게 내리며 지식 나무를 키우는 캐릭터",
    consumptionPattern: "학습 채널, 강의 시리즈, 전문 분야 영상을 꾸준히 이어서 봅니다."
  },
  PWSF: {
    code: "PWSF",
    name: "추천 피드 유람형",
    characterName: "웨이브",
    emoji: "🌊",
    color: "sky",
    imagePath: "/characters/pwsf.png",
    oneLiner: "추천 흐름을 따라 다양한 숏폼을 가볍게 둘러보며 흥미를 발견하는 패턴입니다.",
    tags: ["#추천피드", "#숏폼유람", "#가벼운탐색"],
    attention: "추천 흐름이 편한 만큼, 내가 직접 고른 주제와 피드가 보여준 주제를 구분해보면 더 선명해집니다.",
    recovery: "피드에서 멈춘 영상 하나를 보고 왜 눌렀는지 한 문장으로 정리해보세요.",
    visualConcept: "작은 보드를 타고 추천 피드의 물결을 부드럽게 넘는 캐릭터",
    consumptionPattern: "홈 피드와 추천 탭을 따라 짧은 영상들을 부담 없이 둘러봅니다."
  },
  PWSL: {
    code: "PWSL",
    name: "자동재생 감상형",
    characterName: "시네",
    emoji: "🎬",
    color: "fuchsia",
    imagePath: "/characters/pwsl.png",
    oneLiner: "추천되는 긴 콘텐츠를 편안하게 감상하며 흐름 속에서 이야기를 따라가는 패턴입니다.",
    tags: ["#자동재생", "#롱폼감상", "#편안한시청"],
    attention: "자동재생이 이어질 때 시청 시간이 길어질 수 있어, 한 편이 끝나는 지점에서 잠깐 멈추는 기준이 필요합니다.",
    recovery: "긴 영상 하나가 끝나면 다음 영상을 보기 전 물 한 잔이나 짧은 스트레칭으로 흐름을 끊어보세요.",
    visualConcept: "작은 극장 의자에 앉아 다음 장면을 차분히 기다리는 캐릭터",
    consumptionPattern: "리뷰, 예능, 다큐, 해설 영상이 자동으로 이어지는 흐름을 감상합니다."
  },
  PWMF: {
    code: "PWMF",
    name: "편안한 정보 스낵형",
    characterName: "쿠션",
    emoji: "☁️",
    color: "lime",
    imagePath: "/characters/pwmf.png",
    oneLiner: "부담 없는 추천 정보 콘텐츠를 가볍게 소비하며 편안한 리듬을 유지하는 패턴입니다.",
    tags: ["#정보스낵", "#편안함", "#추천소비"],
    attention: "편한 정보 위주로 머물다 보면 새롭거나 조금 어려운 주제를 만나는 빈도가 낮아질 수 있습니다.",
    recovery: "평소보다 살짝 낯선 교양 영상 하나를 5분만 보고 새로 알게 된 점을 적어보세요.",
    visualConcept: "말랑한 쿠션 위에 앉아 작은 정보 조각을 받아보는 캐릭터",
    consumptionPattern: "생활 지식, 취미 팁, 짧은 교양 영상을 추천 피드에서 편하게 봅니다."
  },
  PWML: {
    code: "PWML",
    name: "편안한 롱폼 흐름형",
    characterName: "라디오",
    emoji: "📻",
    color: "orange",
    imagePath: "/characters/pwml.png",
    oneLiner: "긴 영상을 배경처럼 편안하게 소비하며 안정적인 시청 흐름을 만드는 패턴입니다.",
    tags: ["#롱폼흐름", "#배경시청", "#편안한루틴"],
    attention: "배경처럼 틀어두는 시간이 길어지면 실제로 남는 내용이 흐려질 수 있습니다.",
    recovery: "하루 한 번은 10분만 화면과 자막에 집중해 능동적으로 보는 구간을 만들어보세요.",
    visualConcept: "따뜻한 라디오 주파수처럼 긴 콘텐츠를 부드럽게 흘려보내는 캐릭터",
    consumptionPattern: "여행, 음악, 토크, 다큐형 롱폼을 작업이나 휴식 배경으로 틀어둡니다."
  },
  PNSF: {
    code: "PNSF",
    name: "추천 피드 반복형",
    characterName: "루프",
    emoji: "🌀",
    color: "purple",
    imagePath: "/characters/pnsf.png",
    oneLiner: "추천 피드 안에서 익숙한 관심사의 짧은 영상이 반복적으로 이어지는 패턴입니다.",
    tags: ["#추천피드", "#짧은영상", "#반복노출"],
    attention: "비슷한 짧은 영상이 계속 이어질 때는 시간이 빠르게 지나갈 수 있어, 중간에 멈춤 신호를 두면 좋습니다.",
    recovery: "피드에서 같은 주제가 세 번 보이면 검색창에 직접 다른 키워드 하나를 넣어 흐름을 바꿔보세요.",
    visualConcept: "둥근 소용돌이 안에서 같은 관심 키워드를 부드럽게 순환하는 캐릭터",
    consumptionPattern: "추천 피드가 이어주는 특정 관심사의 짧은 영상을 꼬리물기처럼 봅니다."
  },
  PNSL: {
    code: "PNSL",
    name: "추천 주제 정주행형",
    characterName: "트랙",
    emoji: "🎞️",
    color: "pink",
    imagePath: "/characters/pnsl.png",
    oneLiner: "추천 알고리즘이 이어주는 특정 주제의 긴 영상을 연속 감상하는 패턴입니다.",
    tags: ["#추천주제", "#정주행", "#롱폼"],
    attention: "하나의 추천 경로를 오래 따라가면 다른 관점의 영상이 뒤로 밀릴 수 있습니다.",
    recovery: "연속 감상 중간에 같은 주제를 다루는 짧은 요약이나 다른 채널 영상을 끼워 넣어보세요.",
    visualConcept: "필름 트랙을 따라 한 주제의 장면들이 차례로 이어지는 캐릭터",
    consumptionPattern: "추천 목록에 연결된 긴 해설, 리뷰, 시리즈 영상을 계속 이어 봅니다."
  },
  PNMF: {
    code: "PNMF",
    name: "조용한 추천 루틴형",
    characterName: "모드",
    emoji: "🧩",
    color: "emerald",
    imagePath: "/characters/pnmf.png",
    oneLiner: "자극이 적은 추천 콘텐츠를 루틴처럼 소비하며 차분한 정보 흐름을 유지하는 패턴입니다.",
    tags: ["#추천루틴", "#차분한정보", "#짧은콘텐츠"],
    attention: "편안한 루틴은 장점이지만, 직접 찾아보는 탐색성이 조금 약해질 수 있습니다.",
    recovery: "추천 영상 하나를 본 뒤 관련 내용을 직접 검색해서 다른 출처의 설명을 하나 더 확인해보세요.",
    visualConcept: "조용한 모드 전환 버튼처럼 차분한 정보 조각을 맞추는 캐릭터",
    consumptionPattern: "운동 팁, 언어 팁, 생활 정보처럼 짧고 안정적인 추천 영상을 루틴처럼 봅니다."
  },
  PNML: {
    code: "PNML",
    name: "자동재생 한우물형",
    characterName: "앵커",
    emoji: "⚓",
    color: "teal",
    imagePath: "/characters/pnml.png",
    oneLiner: "알고리즘이 추천하는 특정 주제에 안정적으로 머물며 긴 콘텐츠 흐름을 따라가는 패턴입니다.",
    tags: ["#자동재생", "#한우물", "#안정흐름"],
    attention: "안정적인 시청 흐름이 이어질수록 새 주제를 우연히 만날 기회가 줄어들 수 있습니다.",
    recovery: "익숙한 채널을 보기 전 전혀 다른 분야의 대표 영상 하나를 의도적으로 열어보세요.",
    visualConcept: "잔잔한 항구에 닻을 내리고 한 주제의 긴 흐름을 지켜보는 캐릭터",
    consumptionPattern: "추천되는 긴 교양, 음악, 취미 채널에 머물며 자동재생 흐름을 따라갑니다."
  }
};

const characterAnimals: Record<string, string> = {
  DWSF: "불꽃 여우",
  DWSL: "질주 토끼",
  DWMF: "구름 다람쥐",
  DWML: "숲길 사슴",
  DNSF: "스파크 고슴도치",
  DNSL: "급류 수달",
  DNMF: "포근 강아지",
  DNML: "달빛 부엉이",
  PWSF: "트렌드 오리",
  PWSL: "와이드 곰",
  PWMF: "포근 양",
  PWML: "숲속 코알라",
  PNSF: "클릭 고양이",
  PNSL: "집중 판다",
  PNMF: "쿠션 물개",
  PNML: "서재 거북이"
};

const accentColors: Record<DsaoCharacterColor, string> = {
  amber: "#d97706",
  blue: "#2563eb",
  cyan: "#0891b2",
  emerald: "#059669",
  fuchsia: "#c026d3",
  indigo: "#4f46e5",
  lime: "#65a30d",
  orange: "#ea580c",
  pink: "#db2777",
  purple: "#7c3aed",
  rose: "#e11d48",
  sky: "#0284c7",
  teal: "#0f766e",
  violet: "#7c3aed"
};

export const dsaoCharacters = Object.fromEntries(
  Object.entries(baseDsaoCharacters).map(([code, character]) => [
    code,
    {
      ...character,
      title: character.name,
      animal: characterAnimals[code] || "미디어 마스코트",
      shortDescription: character.oneLiner,
      strengths: [
        character.tags[0]?.replace("#", "") || "관심 패턴이 선명함",
        character.tags[1]?.replace("#", "") || "콘텐츠 선택 기준이 뚜렷함",
        "나에게 맞는 시청 리듬을 만들기 좋음"
      ],
      cautions: [
        character.attention,
        "추천 흐름과 직접 탐색을 구분해보면 더 선명해집니다.",
        "가끔은 다른 관점의 콘텐츠를 섞어보는 것이 좋습니다."
      ],
      recommendedAction: [
        character.recovery,
        "오늘 본 영상 중 기억나는 키워드 하나를 직접 검색해보세요.",
        "시청 후 남는 생각을 한 줄로 적어 알고리즘 흐름을 잠깐 끊어보세요."
      ],
      accentColor: accentColors[character.color]
    }
  ])
) as Record<string, DsaoCharacter>;

export const dsaoCharacterList = Object.values(dsaoCharacters);

export function getDsaoCharacter(code?: string | null): DsaoCharacter {
  const normalizedCode = code?.toUpperCase() || "PNML";
  return dsaoCharacters[normalizedCode] || dsaoCharacters.PNML;
}
