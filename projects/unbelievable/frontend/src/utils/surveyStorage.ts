export interface SelfSurveyResult {
  answers: Record<string, number>;
  axisScores: {
    D: number;
    P: number;
    W: number;
    N: number;
    S: number;
    M: number;
    F: number;
    L: number;
  };
  axisMargins: {
    DP: number;
    WN: number;
    SM: number;
    FL: number;
  };
  resultCode: string;
  resultName: string;
  createdAt: string;
  schemaVersion: string;
}

const STORAGE_KEY = "unbelievable_self_survey";

/**
 * Saves the self-survey result object.
 * MVP: Saves to browser's localStorage.
 * Future migration note: Replace this implementation with an asynchronous POST request to the API
 * (e.g. POST /api/v1/survey/save) to persist in Supabase Postgres.
 */
export const saveSelfSurveyResult = (result: SelfSurveyResult): void => {
  if (typeof window !== "undefined") {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(result));
    } catch (e) {
      console.error("Failed to save self-survey result to localStorage:", e);
    }
  }
};

/**
 * Loads the saved self-survey result.
 * MVP: Fetches from browser's localStorage.
 * Future migration note: Replace this implementation with an asynchronous GET request to the API
 * (e.g. GET /api/v1/survey/load) to retrieve from Supabase Postgres.
 */
export const loadSelfSurveyResult = (): SelfSurveyResult | null => {
  if (typeof window !== "undefined") {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      console.error("Failed to load self-survey result from localStorage:", e);
      return null;
    }
  }
  return null;
};
