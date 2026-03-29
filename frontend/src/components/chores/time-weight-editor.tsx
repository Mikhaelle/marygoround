"use client";

import { useTranslations } from "next-intl";
import { formatHour } from "@/lib/utils/format";
import type { TimeWeightRule } from "@/types/chore";

interface TimeWeightEditorProps {
  rules: TimeWeightRule[];
  onChange: (rules: TimeWeightRule[]) => void;
}

/** Visual 24-hour grid editor for time-based chore weights. */
export function TimeWeightEditor({ rules, onChange }: TimeWeightEditorProps) {
  const t = useTranslations("chores");

  function getWeight(hour: number): number {
    const rule = rules.find((r) => r.hour === hour);
    return rule?.weight ?? 1.0;
  }

  function setWeight(hour: number, weight: number) {
    const existing = rules.filter((r) => r.hour !== hour);
    if (weight !== 1.0) {
      existing.push({ hour, weight });
    }
    existing.sort((a, b) => a.hour - b.hour);
    onChange(existing);
  }

  function getBarColor(weight: number): string {
    if (weight > 1.0) return "bg-emerald-500";
    if (weight < 1.0) return "bg-amber-500";
    return "bg-gray-300 dark:bg-gray-600";
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">{t("timeWeights")}</label>
        <span className="text-xs text-muted-foreground">{t("timeWeightsHelp")}</span>
      </div>

      <div className="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-12 gap-1.5">
        {Array.from({ length: 24 }, (_, hour) => {
          const weight = getWeight(hour);
          const barHeight = Math.max(8, (weight / 3) * 100);

          return (
            <div key={hour} className="flex flex-col items-center gap-1">
              <div className="relative h-16 w-full flex items-end justify-center">
                <div
                  className={`w-full rounded-t transition-all duration-200 ${getBarColor(weight)}`}
                  style={{ height: `${barHeight}%` }}
                />
              </div>
              <span className="text-[10px] text-muted-foreground">{formatHour(hour)}</span>
              <input
                type="number"
                min="0"
                max="3"
                step="0.1"
                value={weight}
                onChange={(e) => {
                  const val = parseFloat(e.target.value) || 0;
                  setWeight(hour, Math.min(3, Math.max(0, val)));
                }}
                className="w-full text-center text-xs border rounded px-0.5 py-0.5 bg-background"
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
