"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import type { WheelSegment } from "@/types/wheel";

const WHEEL_COLORS = [
  "#6366f1", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6",
  "#ec4899", "#14b8a6", "#f97316", "#06b6d4", "#84cc16",
  "#e879f9", "#22d3ee", "#facc15", "#a78bfa", "#fb923c",
  "#34d399", "#f472b6", "#2dd4bf", "#fbbf24", "#818cf8",
];

interface SpinningWheelProps {
  segments: WheelSegment[];
  onSpinStart: () => void;
  onSpinEnd: (segmentIndex: number) => void;
  isSpinning: boolean;
  targetSegmentIndex: number | null;
}

/**
 * Canvas-based spinning wheel with deceleration animation.
 * Draws proportional segments based on effective weight and spins to a target.
 */
export function SpinningWheel({
  segments,
  onSpinStart,
  onSpinEnd,
  isSpinning,
  targetSegmentIndex,
}: SpinningWheelProps) {
  const t = useTranslations("wheel");
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number>(0);
  const [rotation, setRotation] = useState(0);
  const [size, setSize] = useState(400);
  const currentRotationRef = useRef(0);

  useEffect(() => {
    function handleResize() {
      if (containerRef.current) {
        const containerWidth = containerRef.current.clientWidth;
        const newSize = Math.min(containerWidth - 32, 500);
        setSize(Math.max(280, newSize));
      }
    }
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const totalWeight = segments.reduce((sum, s) => sum + s.effective_weight, 0);

  const drawWheel = useCallback(
    (ctx: CanvasRenderingContext2D, canvasSize: number, currentRotation: number) => {
      const centerX = canvasSize / 2;
      const centerY = canvasSize / 2;
      const radius = canvasSize / 2 - 16;
      const dpr = window.devicePixelRatio || 1;

      ctx.clearRect(0, 0, canvasSize * dpr, canvasSize * dpr);
      ctx.save();
      ctx.scale(dpr, dpr);

      if (segments.length === 0) {
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.fillStyle = "#e5e7eb";
        ctx.fill();
        ctx.strokeStyle = "#d1d5db";
        ctx.lineWidth = 3;
        ctx.stroke();

        ctx.fillStyle = "#9ca3af";
        ctx.font = `bold ${canvasSize * 0.04}px sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(t("noChores"), centerX, centerY);
        ctx.restore();
        return;
      }

      let startAngle = currentRotation - Math.PI / 2;

      segments.forEach((segment, i) => {
        const sliceAngle = (segment.effective_weight / totalWeight) * Math.PI * 2;
        const endAngle = startAngle + sliceAngle;

        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, startAngle, endAngle);
        ctx.closePath();

        ctx.fillStyle = WHEEL_COLORS[i % WHEEL_COLORS.length];
        ctx.fill();

        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.stroke();

        const textAngle = startAngle + sliceAngle / 2;
        const textRadius = radius * 0.62;
        const textX = centerX + Math.cos(textAngle) * textRadius;
        const textY = centerY + Math.sin(textAngle) * textRadius;

        ctx.save();
        ctx.translate(textX, textY);
        ctx.rotate(textAngle);

        const maxTextWidth = radius * 0.42;
        const fontSize = Math.max(9, Math.min(13, canvasSize * 0.028));
        ctx.font = `bold ${fontSize}px sans-serif`;
        ctx.fillStyle = "#ffffff";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.shadowColor = "rgba(0,0,0,0.6)";
        ctx.shadowBlur = 3;

        let displayName = segment.name;
        if (ctx.measureText(displayName).width > maxTextWidth) {
          while (ctx.measureText(displayName + "...").width > maxTextWidth && displayName.length > 3) {
            displayName = displayName.slice(0, -1);
          }
          displayName += "...";
        }
        ctx.fillText(displayName, 0, 0);
        ctx.restore();

        startAngle = endAngle;
      });

      const outerRingGrad = ctx.createRadialGradient(
        centerX, centerY, radius - 8,
        centerX, centerY, radius,
      );
      outerRingGrad.addColorStop(0, "rgba(255,255,255,0)");
      outerRingGrad.addColorStop(1, "rgba(255,255,255,0.3)");
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.strokeStyle = outerRingGrad;
      ctx.lineWidth = 8;
      ctx.stroke();

      const centerRadius = radius * 0.18;
      const gradient = ctx.createRadialGradient(
        centerX - centerRadius * 0.3,
        centerY - centerRadius * 0.3,
        0,
        centerX,
        centerY,
        centerRadius,
      );
      gradient.addColorStop(0, "#ffffff");
      gradient.addColorStop(1, "#f3f4f6");
      ctx.beginPath();
      ctx.arc(centerX, centerY, centerRadius, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.fill();
      ctx.strokeStyle = "#d1d5db";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.shadowColor = "transparent";
      ctx.shadowBlur = 0;
      ctx.fillStyle = "#6366f1";
      ctx.font = `bold ${centerRadius * 0.65}px sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(t("spin"), centerX, centerY);

      const pointerSize = canvasSize * 0.04;
      ctx.beginPath();
      ctx.moveTo(centerX - pointerSize, 8);
      ctx.lineTo(centerX + pointerSize, 8);
      ctx.lineTo(centerX, 8 + pointerSize * 1.6);
      ctx.closePath();
      ctx.fillStyle = "#ef4444";
      ctx.fill();
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.restore();
    },
    [segments, totalWeight, t],
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    drawWheel(ctx, size, rotation);
  }, [size, rotation, drawWheel]);

  useEffect(() => {
    if (!isSpinning || targetSegmentIndex === null || targetSegmentIndex === undefined || segments.length === 0) return;

    const targetIdx = targetSegmentIndex;

    let cumulativeAngle = 0;
    for (let i = 0; i < targetIdx; i++) {
      cumulativeAngle += (segments[i].effective_weight / totalWeight) * Math.PI * 2;
    }
    const segmentAngle = (segments[targetIdx].effective_weight / totalWeight) * Math.PI * 2;
    const targetAngleInWheel = cumulativeAngle + segmentAngle / 2;

    const extraTurns = (Math.floor(Math.random() * 5) + 6) * Math.PI * 2;
    const targetRotation = extraTurns + (Math.PI * 2 - targetAngleInWheel);

    const startRotation = currentRotationRef.current;
    const totalDelta = targetRotation;
    const duration = 4500;
    const startTime = performance.now();

    function easeOutCubic(x: number): number {
      return 1 - Math.pow(1 - x, 3);
    }

    function animate(now: number) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutCubic(progress);

      const currentAngle = startRotation + totalDelta * eased;
      currentRotationRef.current = currentAngle;
      setRotation(currentAngle);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        onSpinEnd(targetIdx);
      }
    }

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isSpinning, targetSegmentIndex, segments, totalWeight, onSpinEnd]);

  function handleClick(e: React.MouseEvent<HTMLCanvasElement>) {
    if (isSpinning || segments.length === 0) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    const dist = Math.sqrt(x * x + y * y);
    const centerRadius = (size / 2 - 16) * 0.18;

    if (dist <= centerRadius) {
      onSpinStart();
    }
  }

  return (
    <div ref={containerRef} className="flex flex-col items-center justify-center w-full">
      <div className="relative">
        <canvas
          ref={canvasRef}
          onClick={handleClick}
          className={`cursor-pointer transition-shadow duration-300 rounded-full ${
            isSpinning ? "shadow-2xl shadow-indigo-500/30" : "shadow-lg hover:shadow-xl hover:shadow-indigo-500/20"
          }`}
          style={{ width: size, height: size }}
        />
      </div>
    </div>
  );
}
