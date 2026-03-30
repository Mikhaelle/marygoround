"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { RotateCcw } from "lucide-react";

interface ResetDailyButtonProps {
  onReset: () => Promise<void>;
  disabled?: boolean;
}

/** Button to reset today's wheel spins with a confirmation step. */
export function ResetDailyButton({ onReset, disabled }: ResetDailyButtonProps) {
  const t = useTranslations("wheel");
  const [confirming, setConfirming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
    if (!confirming) {
      setConfirming(true);
      return;
    }

    setIsLoading(true);
    try {
      await onReset();
    } finally {
      setIsLoading(false);
      setConfirming(false);
    }
  };

  const handleBlur = () => {
    setConfirming(false);
  };

  return (
    <Button
      onClick={handleClick}
      onBlur={handleBlur}
      disabled={disabled || isLoading}
      variant={confirming ? "destructive" : "outline"}
      size="sm"
      className="gap-1.5"
    >
      <RotateCcw className="size-3.5" />
      {confirming ? t("resetDailyConfirm") : t("resetDaily")}
    </Button>
  );
}
