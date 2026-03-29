export type DrawStatus = "ACTIVE" | "RESOLVED" | "RETURNED";

export interface BucketItem {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  created_at: string;
  updated_at: string;
}

export interface BucketDraw {
  id: string;
  item: BucketItem;
  drawn_at: string;
  status: DrawStatus;
  resolved_at: string | null;
  return_justification: string | null;
}

export interface CreateBucketItemRequest {
  name: string;
  description?: string;
  category?: string;
}

export interface UpdateBucketItemRequest {
  name?: string;
  description?: string;
  category?: string;
}
