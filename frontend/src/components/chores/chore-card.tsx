"use client";

import { useTranslations } from "next-intl";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Pencil, Trash2, Clock, Layers } from "lucide-react";
import type { Chore } from "@/types/chore";
import { formatDuration } from "@/lib/utils/format";

interface ChoreCardProps {
  chore: Chore;
  onEdit: (chore: Chore) => void;
  onDelete: (chore: Chore) => void;
}

/** Card displaying a single chore with edit/delete actions. */
export function ChoreCard({ chore, onEdit, onDelete }: ChoreCardProps) {
  const t = useTranslations("chores");

  return (
    <Card className="group hover:shadow-md transition-all duration-200 hover:border-indigo-200 dark:hover:border-indigo-800">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-foreground truncate">{chore.name}</h3>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <Badge variant="outline" className="gap-1">
                <Clock className="size-3" />
                {formatDuration(chore.estimated_duration_minutes)}
              </Badge>
              {chore.category && <Badge variant="secondary">{chore.category}</Badge>}
              {chore.wheel_config.multiplicity > 1 && (
                <Badge
                  variant="outline"
                  className="gap-1 border-amber-300 text-amber-700 dark:border-amber-600 dark:text-amber-400"
                >
                  <Layers className="size-3" />
                  {chore.wheel_config.multiplicity}x
                </Badge>
              )}
            </div>
          </div>

          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button variant="ghost" size="icon-sm" onClick={() => onEdit(chore)}>
              <Pencil className="size-3.5" />
              <span className="sr-only">{t("editChore")}</span>
            </Button>
            <Button
              variant="ghost"
              size="icon-sm"
              className="hover:text-destructive"
              onClick={() => onDelete(chore)}
            >
              <Trash2 className="size-3.5" />
              <span className="sr-only">{t("deleteChore")}</span>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
