"use client";

import { useCallback, useEffect, useState } from "react";
import type { NotificationPreference } from "@/types/notification";
import * as notifApi from "@/lib/api/notifications";

/**
 * Manage push notification subscriptions and preferences.
 * @returns Notification state, permission status, and control functions.
 */
export function useNotifications() {
  const [preferences, setPreferences] = useState<NotificationPreference | null>(null);
  const [permission, setPermission] = useState<NotificationPermission>("default");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (typeof window !== "undefined" && "Notification" in window) {
      setPermission(Notification.permission);
    }
  }, []);

  const fetchPreferences = useCallback(async () => {
    setIsLoading(true);
    try {
      const prefs = await notifApi.getPreferences();
      setPreferences(prefs);
    } catch {
      /* preferences may not exist yet */
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  const requestPermission = useCallback(async (): Promise<NotificationPermission> => {
    if (typeof window === "undefined" || !("Notification" in window)) {
      return "denied";
    }
    const result = await Notification.requestPermission();
    setPermission(result);
    return result;
  }, []);

  const subscribeToPush = useCallback(async () => {
    if (!("serviceWorker" in navigator)) return;

    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY,
    });

    const json = subscription.toJSON();
    await notifApi.subscribe({
      endpoint: json.endpoint!,
      p256dh_key: json.keys!.p256dh!,
      auth_key: json.keys!.auth!,
    });
  }, []);

  const unsubscribeFromPush = useCallback(async () => {
    await notifApi.unsubscribe();
  }, []);

  const updatePreferences = useCallback(
    async (prefs: Partial<NotificationPreference>) => {
      const updated = await notifApi.updatePreferences(prefs);
      setPreferences(updated);
      return updated;
    },
    [],
  );

  return {
    preferences,
    permission,
    isLoading,
    requestPermission,
    subscribeToPush,
    unsubscribeFromPush,
    updatePreferences,
    fetchPreferences,
  };
}
