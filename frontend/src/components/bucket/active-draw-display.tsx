"use client";

import { useTranslations, useLocale } from "next-intl";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Check, RotateCcw, Calendar } from "lucide-react";
import type { BucketDraw } from "@/types/bucket";
import { formatDate } from "@/lib/utils/format";

interface ActiveDrawDisplayProps {
  draw: BucketDraw;
  onResolve: () => void;
  onReturn: () => void;
  isLoading: boolean;
}

/** Prominent card showing the currently active drawn bucket item. */
export function ActiveDrawDisplay({ draw, onResolve, onReturn, isLoading }: ActiveDrawDisplayProps) {
  const t = useTranslations("bucket");
  const locale = useLocale();

  const daysSinceDrawn = Math.floor(
    (Date.now() - new Date(draw.drawn_at).getTime()) / (1000 * 60 * 60 * 24),
  );

  return (
    <Card className="border-2 border-indigo-200 dark:border-indigo-800 bg-gradient-to-br from-indigo-50/50 to-purple-50/50 dark:from-indigo-950/30 dark:to-purple-950/30">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg text-indigo-700 dark:text-indigo-300">
            {t("activeDraw")}
          </CardTitle>
          <Badge variant="outline" className="border-indigo-300 text-indigo-600 dark:border-indigo-600 dark:text-indigo-400">
            {daysSinceDrawn === 0 ? "Today" : `${daysSinceDrawn}d`}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h3 className="text-xl font-bold text-foreground">{draw.item.name}</h3>
          {draw.item.description && (
            <p className="text-sm text-muted-foreground mt-1">{draw.item.description}</p>
          )}
          <div className="flex items-center gap-1 text-xs text-muted-foreground mt-2">
            <Calendar className="size-3" />
            {t("drawnOn")} {formatDate(draw.drawn_at, locale)}
          </div>
          {draw.item.category && (
            <Badge variant="secondary" className="mt-2">
              {draw.item.category}
            </Badge>
          )}
        </div>

        <div className="flex gap-3">
          <Button
            variant="outline"
            className="flex-1 border-amber-300 text-amber-700 hover:bg-amber-50 dark:border-amber-600 dark:text-amber-400 dark:hover:bg-amber-950"
            onClick={onReturn}
            disabled={isLoading}
          >
            <RotateCcw className="size-4" />
            {t("return")}
          </Button>
          <Button
            className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white"
            onClick={onResolve}
            disabled={isLoading}
          >
            <Check className="size-4" />
            {t("resolve")}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
