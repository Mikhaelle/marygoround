export interface NotificationPreference {
  interval_minutes: number;
  enabled: boolean;
  quiet_hours_start: number | null;
  quiet_hours_end: number | null;
}

export interface PushSubscriptionPayload {
  endpoint: string;
  p256dh_key: string;
  auth_key: string;
}
