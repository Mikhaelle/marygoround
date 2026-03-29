import { apiClient } from "./client";
import type { NotificationPreference, PushSubscriptionPayload } from "@/types/notification";

/** Subscribe for push notifications. */
export async function subscribe(subscription: PushSubscriptionPayload): Promise<void> {
  await apiClient.post("/notifications/subscribe", subscription);
}

/** Unsubscribe from push notifications. */
export async function unsubscribe(): Promise<void> {
  await apiClient.delete("/notifications/unsubscribe");
}

/** Get current notification preferences. */
export async function getPreferences(): Promise<NotificationPreference> {
  const response = await apiClient.get<NotificationPreference>("/notifications/preferences");
  return response.data;
}

/** Update notification preferences. */
export async function updatePreferences(
  prefs: Partial<NotificationPreference>,
): Promise<NotificationPreference> {
  const response = await apiClient.put<NotificationPreference>(
    "/notifications/preferences",
    prefs,
  );
  return response.data;
}
