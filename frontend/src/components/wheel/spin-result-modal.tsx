"use client";

import { useTranslations } from "next-intl";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, SkipForward, Clock } from "lucide-react";
import type { SpinSession } from "@/types/wheel";
import { formatDuration } from "@/lib/utils/format";

interface SpinResultModalProps {
  session: SpinSession | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onComplete: () => void;
  onSkip: () => void;
  isLoading: boolean;
}

/** Modal displaying the spin result with complete/skip actions. */
export function SpinResultModal({
  session,
  open,
  onOpenChange,
  onComplete,
  onSkip,
  isLoading,
}: SpinResultModalProps) {
  const t = useTranslations("wheel");

  if (!session) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader className="text-center">
          <DialogTitle className="text-2xl font-bold text-center">
            {t("result")}
          </DialogTitle>
          <DialogDescription className="sr-only">
            {t("result")}
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col items-center gap-6 py-6">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
            <span className="text-3xl text-white font-bold">
              {session.chore.name.charAt(0).toUpperCase()}
            </span>
          </div>

          <div className="text-center space-y-2">
            <h3 className="text-xl font-bold text-foreground">{session.chore.name}</h3>
            <div className="flex items-center justify-center gap-2">
              <Clock className="size-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                {formatDuration(session.chore.estimated_duration_minutes)}
              </span>
            </div>
            {session.chore.category && (
              <Badge variant="secondary">{session.chore.category}</Badge>
            )}
          </div>
        </div>

        <div className="flex gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onClick={onSkip}
            disabled={isLoading}
          >
            <SkipForward className="size-4" />
            {t("skip")}
          </Button>
          <Button
            className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white"
            onClick={onComplete}
            disabled={isLoading}
          >
            <Check className="size-4" />
            {t("complete")}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
