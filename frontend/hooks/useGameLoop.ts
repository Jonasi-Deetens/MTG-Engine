import { useCallback, useEffect, useRef, useState } from "react";

type GameLoopCallback = (deltaMs: number) => void;

export function useGameLoop(onFrame: GameLoopCallback) {
  const [isRunning, setIsRunning] = useState(false);
  const frameRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number | null>(null);
  const isRunningRef = useRef(false);
  const onFrameRef = useRef(onFrame);

  useEffect(() => {
    onFrameRef.current = onFrame;
  }, [onFrame]);

  const loop = useCallback((time: number) => {
    if (!isRunningRef.current) return;
    if (lastTimeRef.current === null) {
      lastTimeRef.current = time;
    }
    const deltaMs = time - (lastTimeRef.current ?? time);
    lastTimeRef.current = time;
    onFrameRef.current(deltaMs);
    frameRef.current = window.requestAnimationFrame(loop);
  }, []);

  const start = useCallback(() => {
    if (isRunningRef.current) return;
    isRunningRef.current = true;
    setIsRunning(true);
    frameRef.current = window.requestAnimationFrame(loop);
  }, [loop]);
  const stop = useCallback(() => {
    if (!isRunningRef.current) return;
    isRunningRef.current = false;
    setIsRunning(false);
    if (frameRef.current !== null) {
      window.cancelAnimationFrame(frameRef.current);
      frameRef.current = null;
    }
    lastTimeRef.current = null;
  }, []);

  useEffect(() => {
    if (!isRunning) {
      return;
    }

    return () => {
      stop();
    };
  }, [isRunning, stop]);

  return { isRunning, start, stop };
}
