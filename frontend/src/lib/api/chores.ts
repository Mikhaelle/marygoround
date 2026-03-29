import { apiClient } from "./client";
import type { Chore, CreateChoreRequest, UpdateChoreRequest } from "@/types/chore";

/** Fetch all chores for the current user. */
export async function listChores(): Promise<Chore[]> {
  const response = await apiClient.get<Chore[]>("/chores");
  return response.data;
}

/** Get a single chore by ID. */
export async function getChore(id: string): Promise<Chore> {
  const response = await apiClient.get<Chore>(`/chores/${id}`);
  return response.data;
}

/** Create a new chore. */
export async function createChore(data: CreateChoreRequest): Promise<Chore> {
  const response = await apiClient.post<Chore>("/chores", data);
  return response.data;
}

/** Update an existing chore. */
export async function updateChore(id: string, data: UpdateChoreRequest): Promise<Chore> {
  const response = await apiClient.put<Chore>(`/chores/${id}`, data);
  return response.data;
}

/** Delete a chore by ID. */
export async function deleteChore(id: string): Promise<void> {
  await apiClient.delete(`/chores/${id}`);
}
