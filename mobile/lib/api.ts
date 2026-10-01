/**
 * Any-Family 服务端 API 封装。
 *
 * 服务端默认跑在家庭本地服务器 http://<server-ip>:8080。
 * 真机调试时把 apiBaseUrl 改成电脑在局域网的 IP（见 README）。
 */
import Constants from "expo-constants";

const BASE_URL: string =
  (Constants.expoConfig?.extra?.apiBaseUrl as string) || "http://127.0.0.1:8080";

export type PetProfile = {
  id: string;
  name: string;
  species: "dog" | "cat";
  breed?: string | null;
  age?: number | null;
  sex?: string | null;
  neutered?: boolean | null;
  weight_kg?: number | null;
  trained_commands: string[];
  preferences: Record<string, unknown>;
  habits: Record<string, unknown>;
};

export type Overview = {
  pet_id: string;
  day: string;
  activities: Record<string, number>;
  vocal_count: number;
  actions: Record<string, number>;
  summary: string;
};

export type Interpretation = {
  id: string;
  ts: number;
  label: string;
  confidence: number;
  evidence: string[];
  modalities: string[];
};

export type HealthAlert = {
  id: string;
  region: string;
  severity: "warn" | "urgent";
  finding: string;
  evidence: string[];
  advice: string;
  disclaimer: string;
};

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE_URL}${path}`);
  if (!r.ok) throw new Error(`GET ${path} -> ${r.status}`);
  return (await r.json()) as T;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`POST ${path} -> ${r.status}`);
  return (await r.json()) as T;
}

export const api = {
  baseUrl: BASE_URL,
  getPet: () => get<PetProfile>("/pet"),
  updatePet: (patch: Partial<PetProfile>) => post<PetProfile>("/pet", patch),
  getOverview: () => get<Overview>("/overview"),
  getInterpretations: () => get<Interpretation[]>("/interpretations?limit=12"),
  getHealthAlerts: () => get<HealthAlert[]>("/health-alerts"),
  llmStatus: () => get<{ backend: string; available: boolean }>("/llm-status"),
  ask: (question: string) =>
    post<{ answer: string; evidence: string[]; llm: boolean }>("/ask", { question }),
  speak: (text: string) => post("/speak", { text, voice: "owner" }),
  play: (mode: string) => post("/play", { mode, duration_s: 30 }),
  feed: () => post("/feed", { portion: "small" }),
};
