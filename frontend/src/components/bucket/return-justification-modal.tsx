"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";

interface ReturnJustificationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (justification: string) => Promise<void>;
}

/** Modal with textarea for return justification (min 10 characters). */
export function ReturnJustificationModal({
  open,
  onOpenChange,
  onSubmit,
}: ReturnJustificationModalProps) {
  const t = useTranslations("bucket");
  const tCommon = useTranslations("common");

  const [justification, setJustification] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const charCount = justification.length;
  const isValid = charCount >= 10;

  async function handleSubmit() {
    if (!isValid) {
      setError(t("justificationTooShort"));
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await onSubmit(justification);
      setJustification("");
      onOpenChange(false);
    } catch {
      setError(tCommon("error"));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("justification")}</DialogTitle>
          <DialogDescription className="sr-only">{t("justification")}</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {error && (
            <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="justification">{t("justification")}</Label>
            <Textarea
              id="justification"
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              placeholder={t("justificationPlaceholder")}
              rows={4}
            />
            <div className="flex justify-between text-xs">
              <span
                className={charCount < 10 ? "text-destructive" : "text-muted-foreground"}
              >
                {charCount}/10 min
              </span>
              {!isValid && charCount > 0 && (
                <span className="text-destructive">{t("justificationTooShort")}</span>
              )}
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => onOpenChange(false)}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              className="flex-1 bg-amber-600 hover:bg-amber-700 text-white"
              onClick={handleSubmit}
              disabled={!isValid || isSubmitting}
            >
              {isSubmitting && <Loader2 className="size-4 animate-spin" />}
              {tCommon("confirm")}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
