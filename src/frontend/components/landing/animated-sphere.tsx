"use client";

import { useEffect, useRef } from "react";

const CHARS = "░▒▓█▀▄▌▐│─┤├┴┬╭╮╰╯";

export function AnimatedSphere() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frameRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d", { alpha: true });
    if (!ctx) return;

    let time = 0;
    let lastFrame = 0;
    let visible = true;
    let pageVisible = document.visibilityState === "visible";

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 1.25);
      const rect = canvas.getBoundingClientRect();
      canvas.width = Math.max(1, Math.floor(rect.width * dpr));
      canvas.height = Math.max(1, Math.floor(rect.height * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    resize();
    window.addEventListener("resize", resize);

    const intersection = new IntersectionObserver(
      ([entry]) => {
        visible = entry.isIntersecting;
      },
      { threshold: 0.05 },
    );
    intersection.observe(canvas);

    const onVisibility = () => {
      pageVisible = document.visibilityState === "visible";
    };
    document.addEventListener("visibilitychange", onVisibility);

    const render = (now: number) => {
      frameRef.current = requestAnimationFrame(render);
      if (!visible || !pageVisible || now - lastFrame < 33) {
        return;
      }
      lastFrame = now;

      const rect = canvas.getBoundingClientRect();
      ctx.clearRect(0, 0, rect.width, rect.height);

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const radius = Math.min(rect.width, rect.height) * 0.525;
      ctx.font = "12px monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      const points: { x: number; y: number; z: number; char: string }[] = [];
      const rotY = time * 0.3;
      const rotX = time * 0.2;
      const cosY = Math.cos(rotY);
      const sinY = Math.sin(rotY);
      const cosX = Math.cos(rotX);
      const sinX = Math.sin(rotX);
      const spin = time * 0.5;

      for (let phi = 0; phi < Math.PI * 2; phi += 0.2) {
        for (let theta = 0; theta < Math.PI; theta += 0.2) {
          const x = Math.sin(theta) * Math.cos(phi + spin);
          const y = Math.sin(theta) * Math.sin(phi + spin);
          const z = Math.cos(theta);
          const newX = x * cosY - z * sinY;
          const newZ = x * sinY + z * cosY;
          const newY = y * cosX - newZ * sinX;
          const finalZ = y * sinX + newZ * cosX;
          const depth = (finalZ + 1) / 2;
          points.push({
            x: centerX + newX * radius,
            y: centerY + newY * radius,
            z: finalZ,
            char: CHARS[Math.floor(depth * (CHARS.length - 1))],
          });
        }
      }

      points.sort((a, b) => a.z - b.z);
      for (const point of points) {
        const alpha = 0.2 + (point.z + 1) * 0.4;
        ctx.fillStyle = `rgba(0, 0, 0, ${alpha})`;
        ctx.fillText(point.char, point.x, point.y);
      }

      time += 0.033;
    };

    frameRef.current = requestAnimationFrame(render);

    return () => {
      window.removeEventListener("resize", resize);
      document.removeEventListener("visibilitychange", onVisibility);
      intersection.disconnect();
      cancelAnimationFrame(frameRef.current);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="h-full w-full"
      style={{ display: "block" }}
      aria-hidden
    />
  );
}
