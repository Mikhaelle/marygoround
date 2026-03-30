"use client";

import { useTranslations } from "next-intl";
import { useLocale } from "next-intl";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Clock, Check, SkipForward, Hourglass } from "lucide-react";
import type { SpinHistoryItem } from "@/types/wheel";
import { formatDateTime } from "@/lib/utils/format";

interface SpinHistoryProps {
  history: SpinHistoryItem[];
}

/** Displays recent spin sessions with their status. */
export function SpinHistory({ history }: SpinHistoryProps) {
  const t = useTranslations("wheel");
  const locale = useLocale();

  if (history.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t("recentSpins")}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-4">{t("noHistory")}</p>
        </CardContent>
      </Card>
    );
  }

  function getStatusIcon(status: string) {
    switch (status) {
      case "COMPLETED":
        return <Check className="size-3.5" />;
      case "SKIPPED":
        return <SkipForward className="size-3.5" />;
      default:
        return <Hourglass className="size-3.5" />;
    }
  }

  function getStatusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
    switch (status) {
      case "COMPLETED":
        return "default";
      case "SKIPPED":
        return "secondary";
      default:
        return "outline";
    }
  }

  function getStatusLabel(status: string) {
    switch (status) {
      case "COMPLETED":
        return t("completed");
      case "SKIPPED":
        return t("skipped");
      default:
        return t("pending");
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{t("recentSpins")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {history.slice(0, 10).map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between gap-3 p-3 rounded-lg bg-muted/50"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{item.chore_name}</p>
              <div className="flex items-center gap-1 text-xs text-muted-foreground mt-0.5">
                <Clock className="size-3" />
                {formatDateTime(item.spun_at, locale)}
              </div>
            </div>
            <Badge variant={getStatusVariant(item.status)} className="gap-1 shrink-0">
              {getStatusIcon(item.status)}
              {getStatusLabel(item.status)}
            </Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
