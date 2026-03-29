import { apiClient } from "./client";
import type { BucketItem, BucketDraw } from "@/types/bucket";
import type { CreateBucketItemRequest, UpdateBucketItemRequest } from "@/types/bucket";

/** Fetch all bucket items. */
export async function listItems(): Promise<BucketItem[]> {
  const response = await apiClient.get<BucketItem[]>("/bucket/items");
  return response.data;
}

/** Create a new bucket item. */
export async function createItem(data: CreateBucketItemRequest): Promise<BucketItem> {
  const response = await apiClient.post<BucketItem>("/bucket/items", data);
  return response.data;
}

/** Update an existing bucket item. */
export async function updateItem(id: string, data: UpdateBucketItemRequest): Promise<BucketItem> {
  const response = await apiClient.put<BucketItem>(`/bucket/items/${id}`, data);
  return response.data;
}

/** Delete a bucket item. */
export async function deleteItem(id: string): Promise<void> {
  await apiClient.delete(`/bucket/items/${id}`);
}

/** Draw a random item from the bucket. */
export async function draw(): Promise<BucketDraw> {
  const response = await apiClient.post<BucketDraw>("/bucket/draw");
  return response.data;
}

/** Get the currently active draw, if any. */
export async function getActiveDraw(): Promise<BucketDraw | null> {
  try {
    const response = await apiClient.get<BucketDraw | null>("/bucket/draws/active");
    return response.data;
  } catch {
    return null;
  }
}

/** Resolve the active draw (mark as done). */
export async function resolveDraw(drawId: string): Promise<BucketDraw> {
  const response = await apiClient.put<BucketDraw>(`/bucket/draws/${drawId}/resolve`);
  return response.data;
}

/** Return a drawn item back to the bucket with justification. */
export async function returnDraw(drawId: string, justification: string): Promise<BucketDraw> {
  const response = await apiClient.put<BucketDraw>(`/bucket/draws/${drawId}/return`, {
    justification,
  });
  return response.data;
}
