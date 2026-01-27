import { useCallback, useEffect, useRef, useState } from "react";

type GameLoopCallback = (deltaMs: number) => void;

export function useGameLoop(onFrame: GameLoopCallback) {
  const [isRunning, setIsRunning] = useState(false);
  const frameRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number | null>(null);

  const loop = useCallback(
    (time: number) => {
      if (!isRunning) return;
      if (lastTimeRef.current === null) {
        lastTimeRef.current = time;
      }
      const deltaMs = time - (lastTimeRef.current ?? time);
      lastTimeRef.current = time;
      onFrame(deltaMs);
      frameRef.current = window.requestAnimationFrame(loop);
    },
    [isRunning, onFrame]
  );

  const start = useCallback(() => setIsRunning(true), []);
  const stop = useCallback(() => setIsRunning(false), []);

  useEffect(() => {
    if (!isRunning) {
      if (frameRef.current !== null) {
        window.cancelAnimationFrame(frameRef.current);
        frameRef.current = null;
      }
      lastTimeRef.current = null;
      return;
    }

    frameRef.current = window.requestAnimationFrame(loop);
    return () => {
      if (frameRef.current !== null) {
        window.cancelAnimationFrame(frameRef.current);
      }
      frameRef.current = null;
      lastTimeRef.current = null;
    };
  }, [isRunning, loop]);

  return { isRunning, start, stop };
}
