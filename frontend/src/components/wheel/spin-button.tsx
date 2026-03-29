"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Loader2, Disc3 } from "lucide-react";

interface SpinButtonProps {
  onSpin: () => void;
  isSpinning: boolean;
  disabled?: boolean;
}

/** Large call-to-action button to trigger the wheel spin. */
export function SpinButton({ onSpin, isSpinning, disabled }: SpinButtonProps) {
  const t = useTranslations("wheel");

  return (
    <Button
      onClick={onSpin}
      disabled={isSpinning || disabled}
      size="lg"
      className="w-full max-w-xs h-14 text-lg font-bold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 rounded-xl"
    >
      {isSpinning ? (
        <>
          <Loader2 className="size-5 animate-spin" />
          {t("spinning")}
        </>
      ) : (
        <>
          <Disc3 className="size-5" />
          {t("spin")}
        </>
      )}
    </Button>
  );
}
