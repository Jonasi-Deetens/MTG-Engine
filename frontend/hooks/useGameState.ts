import { useCallback, useMemo, useRef, useState } from "react";

export type GameStatus = "idle" | "playing" | "paused" | "gameover";

export type Vector2 = {
  x: number;
  y: number;
};

export type OrbType =
  | "normal"
  | "fast"
  | "slow"
  | "splitting"
  | "homing"
  | "phasing";

export type OrbEntity = {
  id: number;
  type: OrbType;
  position: Vector2;
  velocity: Vector2;
  radius: number;
  damage: number;
  isPhasing?: boolean;
  phaseTimerMs?: number;
};

export type ProjectileEntity = {
  id: number;
  position: Vector2;
  velocity: Vector2;
  radius: number;
};

export type LaserEntity = {
  id: number;
  axis: "horizontal" | "vertical";
  position: number;
  warningMs: number;
  firingMs: number;
  status: "warning" | "firing" | "done";
  hasHit: boolean;
};

export type BossEntity = {
  id: number;
  position: Vector2;
  velocity: Vector2;
  radius: number;
  hp: number;
  maxHp: number;
};

type Bounds = {
  width: number;
  height: number;
};

const baseSpawnIntervalMs = 900;
const projectileSpeed = 560;
const outOfBoundsMargin = 48;
const playerRadius = 12;
const laserWarningMs = 1500;
const laserFiringMs = 300;

const orbConfig: Record<
  OrbType,
  { speed: [number, number]; radius: [number, number]; damage: number }
> = {
  normal: { speed: [50, 140], radius: [8, 16], damage: 1 },
  fast: { speed: [160, 220], radius: [5, 8], damage: 1 },
  slow: { speed: [30, 50], radius: [18, 28], damage: 2 },
  splitting: { speed: [60, 100], radius: [12, 16], damage: 1 },
  homing: { speed: [40, 70], radius: [10, 14], damage: 1 },
  phasing: { speed: [50, 90], radius: [10, 14], damage: 1 },
};

const orbWeights: Array<{ type: OrbType; weight: number }> = [
  { type: "normal", weight: 40 },
  { type: "fast", weight: 20 },
  { type: "slow", weight: 15 },
  { type: "splitting", weight: 10 },
  { type: "homing", weight: 10 },
  { type: "phasing", weight: 5 },
];

const clamp = (value: number, min: number, max: number) =>
  Math.max(min, Math.min(max, value));

const normalize = (vec: Vector2): Vector2 => {
  const length = Math.hypot(vec.x, vec.y);
  if (!length) return { x: 0, y: 0 };
  return { x: vec.x / length, y: vec.y / length };
};

const randomBetween = (min: number, max: number) =>
  min + Math.random() * (max - min);

const weightedPick = (weights: Array<{ type: OrbType; weight: number }>) => {
  const total = weights.reduce((sum, item) => sum + item.weight, 0);
  const roll = Math.random() * total;
  let current = 0;
  for (const item of weights) {
    current += item.weight;
    if (roll <= current) return item.type;
  }
  return weights[0].type;
};

const getOrbWeights = (difficulty: number) =>
  orbWeights.map((entry) => {
    if (entry.type === "normal") {
      return { ...entry, weight: Math.max(15, entry.weight - difficulty * 20) };
    }
    if (entry.type === "phasing") {
      return { ...entry, weight: entry.weight + difficulty * 6 };
    }
    if (entry.type === "homing") {
      return { ...entry, weight: entry.weight + difficulty * 6 };
    }
    if (entry.type === "splitting") {
      return { ...entry, weight: entry.weight + difficulty * 4 };
    }
    if (entry.type === "fast") {
      return { ...entry, weight: entry.weight + difficulty * 4 };
    }
    if (entry.type === "slow") {
      return { ...entry, weight: entry.weight + difficulty * 2 };
    }
    return entry;
  });

const getSpawnInterval = (score: number) =>
  Math.max(500, baseSpawnIntervalMs - Math.min(400, Math.floor(score / 250) * 20));

const spawnFromEdge = (bounds: Bounds, radius: number) => {
  const edge = Math.floor(Math.random() * 4);
  let position: Vector2 = { x: 0, y: 0 };
  let direction: Vector2 = { x: 0, y: 0 };

  if (edge === 0) {
    position = { x: Math.random() * bounds.width, y: -radius };
    direction = { x: randomBetween(-0.4, 0.4), y: 1 };
  } else if (edge === 1) {
    position = { x: bounds.width + radius, y: Math.random() * bounds.height };
    direction = { x: -1, y: randomBetween(-0.4, 0.4) };
  } else if (edge === 2) {
    position = { x: Math.random() * bounds.width, y: bounds.height + radius };
    direction = { x: randomBetween(-0.4, 0.4), y: -1 };
  } else {
    position = { x: -radius, y: Math.random() * bounds.height };
    direction = { x: 1, y: randomBetween(-0.4, 0.4) };
  }

  return { position, direction: normalize(direction) };
};

const createOrb = (
  bounds: Bounds,
  id: number,
  weights: Array<{ type: OrbType; weight: number }> = orbWeights
): OrbEntity => {
  const type = weightedPick(weights);
  const config = orbConfig[type];
  const radius = randomBetween(config.radius[0], config.radius[1]);
  const { position, direction } = spawnFromEdge(bounds, radius);
  const speed = randomBetween(config.speed[0], config.speed[1]);

  return {
    id,
    type,
    position,
    velocity: { x: direction.x * speed, y: direction.y * speed },
    radius,
    damage: config.damage,
    isPhasing: type === "phasing" ? false : undefined,
    phaseTimerMs: type === "phasing" ? randomBetween(350, 650) : undefined,
  };
};

const createSplitOrb = (source: OrbEntity, id: number): OrbEntity => {
  const radius = randomBetween(6, 9);
  const direction = normalize({
    x: randomBetween(-1, 1),
    y: randomBetween(-1, 1),
  });
  const speed = randomBetween(120, 180);
  return {
    id,
    type: "fast",
    position: { ...source.position },
    velocity: { x: direction.x * speed, y: direction.y * speed },
    radius,
    damage: 1,
  };
};

export function useGameState() {
  const [score, setScore] = useState(0);
  const [lives, setLives] = useState(3);
  const [status, setStatusState] = useState<GameStatus>("idle");
  const [elapsedMs, setElapsedMs] = useState(0);

  const scoreRef = useRef(score);
  const livesRef = useRef(lives);
  const statusRef = useRef<GameStatus>(status);
  const elapsedRef = useRef(elapsedMs);

  const orbsRef = useRef<OrbEntity[]>([]);
  const projectilesRef = useRef<ProjectileEntity[]>([]);
  const lasersRef = useRef<LaserEntity[]>([]);
  const bossesRef = useRef<BossEntity[]>([]);
  const pointerRef = useRef<Vector2>({ x: 0, y: 0 });
  const spawnTimerRef = useRef(0);
  const laserSpawnTimerRef = useRef(randomBetween(8000, 12000));
  const nextOrbIdRef = useRef(1);
  const nextProjectileIdRef = useRef(1);
  const nextLaserIdRef = useRef(1);
  const nextBossIdRef = useRef(1);
  const nextBossScoreRef = useRef(2000);

  const setStatus = useCallback((next: GameStatus) => {
    statusRef.current = next;
    setStatusState(next);
  }, []);

  const updateScore = useCallback((next: number) => {
    scoreRef.current = next;
    setScore(next);
  }, []);

  const updateLives = useCallback((next: number) => {
    livesRef.current = next;
    setLives(next);
  }, []);

  const updateElapsed = useCallback((next: number) => {
    elapsedRef.current = next;
    setElapsedMs(next);
  }, []);

  const resetState = useCallback(() => {
    orbsRef.current = [];
    projectilesRef.current = [];
    lasersRef.current = [];
    bossesRef.current = [];
    spawnTimerRef.current = 0;
    laserSpawnTimerRef.current = randomBetween(8000, 12000);
    nextBossScoreRef.current = 2000;
    updateScore(0);
    updateLives(3);
    updateElapsed(0);
  }, [updateElapsed, updateLives, updateScore]);

  const startGame = useCallback(() => {
    resetState();
    updateElapsed(0);
    setStatus("playing");
  }, [resetState, setStatus, updateElapsed]);

  const resetGame = useCallback(() => {
    resetState();
    setStatus("idle");
  }, [resetState, setStatus]);

  const pauseGame = useCallback(() => {
    if (statusRef.current === "playing") {
      setStatus("paused");
    }
  }, [setStatus]);

  const resumeGame = useCallback(() => {
    if (statusRef.current === "paused") {
      setStatus("playing");
    }
  }, [setStatus]);

  const setPointer = useCallback((next: Vector2) => {
    pointerRef.current = next;
  }, []);

  const shoot = useCallback((origin: Vector2, target: Vector2) => {
    if (statusRef.current !== "playing") return;
    const direction = normalize({ x: target.x - origin.x, y: target.y - origin.y });
    if (direction.x === 0 && direction.y === 0) return;

    const projectile: ProjectileEntity = {
      id: nextProjectileIdRef.current++,
      position: { ...origin },
      velocity: {
        x: direction.x * projectileSpeed,
        y: direction.y * projectileSpeed,
      },
      radius: 3,
    };

    projectilesRef.current = [...projectilesRef.current, projectile];
  }, []);

  const update = useCallback(
    (deltaMs: number, bounds: Bounds, playerPosition: Vector2) => {
      if (statusRef.current !== "playing") return;
      if (bounds.width <= 0 || bounds.height <= 0) return;

      const deltaSec = deltaMs / 1000;
      const nextElapsed = elapsedRef.current + deltaMs;
      updateElapsed(nextElapsed);
      let damageTaken = 0;
      let scoreDelta = 0;

      const targetMs = 6 * 60 * 1000;
      const easeOutQuad = (t: number) => 1 - (1 - t) * (1 - t);
      const difficulty = easeOutQuad(Math.min(nextElapsed / targetMs, 1));

      const spawnInterval = Math.max(
        500,
        getSpawnInterval(scoreRef.current) - difficulty * 180
      );
      spawnTimerRef.current += deltaMs;
      const weights = getOrbWeights(difficulty);
      while (spawnTimerRef.current >= spawnInterval) {
        spawnTimerRef.current -= spawnInterval;
        orbsRef.current = [
          ...orbsRef.current,
          createOrb(bounds, nextOrbIdRef.current++, weights),
        ];
      }

      const laserWindowMin = 4000 + (1 - difficulty) * 2000;
      const laserWindowMax = 7000 + (1 - difficulty) * 4000;
      laserSpawnTimerRef.current -= deltaMs;
      if (laserSpawnTimerRef.current <= 0) {
        laserSpawnTimerRef.current = randomBetween(laserWindowMin, laserWindowMax);
        const axis = Math.random() > 0.5 ? "horizontal" : "vertical";
        const position =
          axis === "horizontal"
            ? randomBetween(bounds.height * 0.15, bounds.height * 0.85)
            : randomBetween(bounds.width * 0.15, bounds.width * 0.85);
        lasersRef.current = [
          ...lasersRef.current,
          {
            id: nextLaserIdRef.current++,
            axis,
            position,
            warningMs: laserWarningMs,
            firingMs: laserFiringMs,
            status: "warning",
            hasHit: false,
          },
        ];
      }

      const updatedLasers: LaserEntity[] = lasersRef.current
        .map<LaserEntity>((laser) => {
          if (laser.status === "warning") {
            const nextWarning = laser.warningMs - deltaMs;
            if (nextWarning <= 0) {
              return { ...laser, warningMs: 0, status: "firing" };
            }
            return { ...laser, warningMs: nextWarning };
          }
          if (laser.status === "firing") {
            const nextFiring = laser.firingMs - deltaMs;
            if (nextFiring <= 0) {
              return { ...laser, firingMs: 0, status: "done" };
            }
            return { ...laser, firingMs: nextFiring };
          }
          return laser;
        })
        .filter((laser): laser is LaserEntity => laser.status !== "done");

      lasersRef.current = updatedLasers;

      lasersRef.current = lasersRef.current.map((laser) => {
        if (laser.status !== "firing" || laser.hasHit) return laser;
        const hit =
          laser.axis === "horizontal"
            ? Math.abs(playerPosition.y - laser.position) <= playerRadius
            : Math.abs(playerPosition.x - laser.position) <= playerRadius;
        if (hit) {
          damageTaken += 1;
          return { ...laser, hasHit: true };
        }
        return laser;
      });

      if (
        bossesRef.current.length === 0 &&
        scoreRef.current >= nextBossScoreRef.current
      ) {
        const radius = randomBetween(40, 60);
        const bossBaseHp = Math.max(5, Math.floor(scoreRef.current / 1000) + 4);
        const bossHp = Math.round(bossBaseHp + difficulty * 4);
        bossesRef.current = [
          {
            id: nextBossIdRef.current++,
            position: { x: bounds.width * 0.5, y: radius + 8 },
            velocity: {
              x: randomBetween(-20, 20),
              y: randomBetween(10, 25),
            },
            radius,
            hp: bossHp,
            maxHp: bossHp,
          },
        ];
        nextBossScoreRef.current += 2000;
      }

      const updatedProjectiles = projectilesRef.current
        .map((projectile) => ({
          ...projectile,
          position: {
            x: projectile.position.x + projectile.velocity.x * deltaSec,
            y: projectile.position.y + projectile.velocity.y * deltaSec,
          },
        }))
        .filter(
          (projectile) =>
            projectile.position.x >= -outOfBoundsMargin &&
            projectile.position.x <= bounds.width + outOfBoundsMargin &&
            projectile.position.y >= -outOfBoundsMargin &&
            projectile.position.y <= bounds.height + outOfBoundsMargin
        );

      const updatedOrbs: OrbEntity[] = [];

      orbsRef.current.forEach((orb) => {
        let nextVelocity = orb.velocity;
        if (orb.type === "homing") {
          const toPlayer = normalize({
            x: playerPosition.x - orb.position.x,
            y: playerPosition.y - orb.position.y,
          });
          const speed = Math.hypot(orb.velocity.x, orb.velocity.y);
          const steer = 0.9;
          nextVelocity = normalize({
            x: orb.velocity.x + toPlayer.x * steer,
            y: orb.velocity.y + toPlayer.y * steer,
          });
          nextVelocity = {
            x: nextVelocity.x * speed,
            y: nextVelocity.y * speed,
          };
        }

        let nextPhaseTimer = orb.phaseTimerMs;
        let nextIsPhasing = orb.isPhasing;
        if (orb.type === "phasing" && typeof nextPhaseTimer === "number") {
          nextPhaseTimer -= deltaMs;
          if (nextPhaseTimer <= 0) {
            nextIsPhasing = !nextIsPhasing;
            nextPhaseTimer = randomBetween(400, 700);
          }
        }

        const nextPosition = {
          x: orb.position.x + nextVelocity.x * deltaSec,
          y: orb.position.y + nextVelocity.y * deltaSec,
        };
        const outOfBounds =
          nextPosition.x < -outOfBoundsMargin ||
          nextPosition.x > bounds.width + outOfBoundsMargin ||
          nextPosition.y < -outOfBoundsMargin ||
          nextPosition.y > bounds.height + outOfBoundsMargin;

        if (outOfBounds) return;

        updatedOrbs.push({
          ...orb,
          position: nextPosition,
          velocity: nextVelocity,
          isPhasing: nextIsPhasing,
          phaseTimerMs: nextPhaseTimer,
        });
      });

      const playerHitOrbs = new Set<number>();
      updatedOrbs.forEach((orb, index) => {
        const dx = orb.position.x - playerPosition.x;
        const dy = orb.position.y - playerPosition.y;
        const distanceSq = dx * dx + dy * dy;
        const radiusSum = orb.radius + playerRadius;
        if (distanceSq <= radiusSum * radiusSum) {
          playerHitOrbs.add(index);
          damageTaken += orb.damage;
        }
      });

      const hitOrbs = new Set<number>();
      const hitProjectiles = new Set<number>();
      const spawnedOrbs: OrbEntity[] = [];

      updatedOrbs.forEach((orb, orbIndex) => {
        if (playerHitOrbs.has(orbIndex)) return;
        updatedProjectiles.forEach((projectile, projectileIndex) => {
          if (hitOrbs.has(orbIndex) || hitProjectiles.has(projectileIndex)) return;
          if (orb.type === "phasing" && orb.isPhasing) return;
          const dx = orb.position.x - projectile.position.x;
          const dy = orb.position.y - projectile.position.y;
          const distanceSq = dx * dx + dy * dy;
          const radiusSum = orb.radius + projectile.radius;
          if (distanceSq <= radiusSum * radiusSum) {
            hitOrbs.add(orbIndex);
            hitProjectiles.add(projectileIndex);
            scoreDelta += orb.type === "slow" ? 150 : 100;
            if (orb.type === "splitting") {
              const splitCount = Math.floor(randomBetween(2, 4));
              for (let i = 0; i < splitCount; i += 1) {
                spawnedOrbs.push(
                  createSplitOrb(orb, nextOrbIdRef.current++)
                );
              }
            }
          }
        });
      });

      const remainingOrbs = updatedOrbs.filter(
        (_, index) => !hitOrbs.has(index) && !playerHitOrbs.has(index)
      );
      orbsRef.current = [...remainingOrbs, ...spawnedOrbs];

      if (bossesRef.current.length) {
        const updatedBosses: BossEntity[] = [];
        bossesRef.current.forEach((boss) => {
          let nextPosition = {
            x: boss.position.x + boss.velocity.x * deltaSec,
            y: boss.position.y + boss.velocity.y * deltaSec,
          };
          let nextVelocity = { ...boss.velocity };

          if (nextPosition.x < boss.radius || nextPosition.x > bounds.width - boss.radius) {
            nextVelocity.x *= -1;
            nextPosition = {
              x: clamp(nextPosition.x, boss.radius, bounds.width - boss.radius),
              y: nextPosition.y,
            };
          }
          if (nextPosition.y < boss.radius || nextPosition.y > bounds.height * 0.5) {
            nextVelocity.y *= -1;
            nextPosition = {
              x: nextPosition.x,
              y: clamp(nextPosition.y, boss.radius, bounds.height * 0.5),
            };
          }

          let hp = boss.hp;
          updatedProjectiles.forEach((projectile, projectileIndex) => {
            if (hitProjectiles.has(projectileIndex)) return;
            const dx = boss.position.x - projectile.position.x;
            const dy = boss.position.y - projectile.position.y;
            const distanceSq = dx * dx + dy * dy;
            const radiusSum = boss.radius + projectile.radius;
            if (distanceSq <= radiusSum * radiusSum) {
              hitProjectiles.add(projectileIndex);
              hp -= 1;
            }
          });

          const dx = boss.position.x - playerPosition.x;
          const dy = boss.position.y - playerPosition.y;
          if (dx * dx + dy * dy <= (boss.radius + playerRadius) ** 2) {
            damageTaken += 2;
          }

          if (hp > 0) {
            updatedBosses.push({
              ...boss,
              position: nextPosition,
              velocity: nextVelocity,
              hp,
            });
          } else {
            scoreDelta += 500;
          }
        });

        bossesRef.current = updatedBosses;
      }

      const remainingProjectiles = updatedProjectiles.filter(
        (_, index) => !hitProjectiles.has(index)
      );
      projectilesRef.current = remainingProjectiles;

      if (scoreDelta) {
        updateScore(scoreRef.current + scoreDelta);
      }

      if (damageTaken) {
        const nextLives = clamp(livesRef.current - damageTaken, 0, 99);
        updateLives(nextLives);
        if (nextLives <= 0) {
          setStatus("gameover");
        }
      }
    },
    [setStatus, updateLives, updateScore]
  );

  const actions = useMemo(
    () => ({
      setPointer,
      shoot,
      update,
      startGame,
      resetGame,
      pauseGame,
      resumeGame,
    }),
    [pauseGame, resetGame, resumeGame, setPointer, shoot, startGame, update]
  );

  return {
    state: { score, lives, status, elapsedMs },
    refs: { orbsRef, projectilesRef, lasersRef, bossesRef, pointerRef },
    actions,
  };
}
