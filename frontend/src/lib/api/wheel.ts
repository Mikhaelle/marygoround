import { apiClient } from "./client";
import type { SpinHistoryItem, SpinSession, WheelSegment } from "@/types/wheel";

/** Spin the wheel and get a chore assignment. */
export async function spin(): Promise<SpinSession> {
  const response = await apiClient.post<SpinSession>("/wheel/spin");
  return response.data;
}

/** Mark a spin session as completed. */
export async function completeSession(sessionId: string): Promise<void> {
  await apiClient.put(`/wheel/sessions/${sessionId}/complete`);
}

/** Skip a spin session. */
export async function skipSession(sessionId: string): Promise<void> {
  await apiClient.put(`/wheel/sessions/${sessionId}/skip`);
}

/** Get spin history for the current user. */
export async function getHistory(page = 1, perPage = 20): Promise<{ items: SpinHistoryItem[]; total: number }> {
  const response = await apiClient.get("/wheel/history", {
    params: { page, per_page: perPage },
  });
  return response.data;
}

/** Get the current wheel segments with computed weights. */
export async function getSegments(): Promise<WheelSegment[]> {
  const response = await apiClient.get<WheelSegment[]>("/wheel/segments");
  return response.data;
}
