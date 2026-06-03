import { useCallback, useMemo, useRef, useState } from "react";
import {
  enemyProjectileDamage,
  enemyProjectileRadius,
  enemyProjectileSpeed,
  laserFiringMs,
  laserWarningMs,
  orbShootConfig,
  outOfBoundsMargin,
  playerRadius,
  projectileSpeed,
} from "@/game/config";
import { getDifficulty, getLaserWindow, getSpawnIntervalBase } from "@/game/difficulty";
import { createOrb, createSplitOrb, getOrbWeights } from "@/game/spawn";
import {
  ascendedBossConfig,
  bossBaseConfig,
  bossDeathConfig,
  bossProjectileConfig,
} from "@/game/boss/config";
import { checkPhaseTransition, createBoss, updateBoss } from "@/game/boss/behavior";
import { devConfig } from "@/game/devConfig";
import type {
  BossEntity,
  Bounds,
  EnemyProjectileEntity,
  GameMode,
  GameStatus,
  LaserEntity,
  NpcEntity,
  NpcProjectileEntity,
  OrbEntity,
  PlayerStats,
  ProjectileEntity,
  RewardEntity,
  StoryPhase,
  UpgradeOption,
  Vector2,
} from "@/game/types";
import { pickUpgrades } from "@/game/upgrades";
import { clamp, normalize, randomBetween } from "@/game/utils";
import { playerConfig } from "@/game/playerConfig";

export function useGameState() {
  const [score, setScore] = useState(0);
  const [lives, setLives] = useState(3);
  const [maxLives, setMaxLives] = useState(3);
  const [status, setStatusState] = useState<GameStatus>("idle");
  const [elapsedMs, setElapsedMs] = useState(0);
  const [playerStats, setPlayerStats] = useState<PlayerStats>(playerConfig);
  const [upgradeOptions, setUpgradeOptions] = useState<UpgradeOption[]>([]);
  const [boss, setBoss] = useState<BossEntity | null>(null);
  const [missionComplete, setMissionComplete] = useState(false);
  const [mode] = useState<GameMode>(devConfig.storyMode ? "story" : "classic");
  const [storyPhase, setStoryPhaseState] = useState<StoryPhase>("intro_dialogue");
  const [npcDialogueIndex, setNpcDialogueIndex] = useState(0);
  const [npcs, setNpcs] = useState<NpcEntity[]>([]);
  const [npcBubbleVisibleMs, setNpcBubbleVisibleMs] = useState(0);
  const [bossDialogueIndex, setBossDialogueIndex] = useState(0);
  const [bossBubbleVisibleMs, setBossBubbleVisibleMs] = useState(0);
  const [bossPhaseMessage, setBossPhaseMessage] = useState("");
  const [bossPhaseMessageMs, setBossPhaseMessageMs] = useState(0);

  const scoreRef = useRef(score);
  const livesRef = useRef(lives);
  const statusRef = useRef<GameStatus>(status);
  const elapsedRef = useRef(elapsedMs);
  const maxLivesRef = useRef(maxLives);
  const playerStatsRef = useRef<PlayerStats>(playerStats);
  const upgradeOptionsRef = useRef<UpgradeOption[]>(upgradeOptions);
  const bossRef = useRef<BossEntity | null>(boss);
  const storyPhaseRef = useRef<StoryPhase>(storyPhase);
  const npcDialogueIndexRef = useRef(npcDialogueIndex);

  const orbsRef = useRef<OrbEntity[]>([]);
  const projectilesRef = useRef<ProjectileEntity[]>([]);
  const enemyProjectilesRef = useRef<EnemyProjectileEntity[]>([]);
  const lasersRef = useRef<LaserEntity[]>([]);
  const bossesRef = useRef<BossEntity[]>([]);
  const npcsRef = useRef<NpcEntity[]>([]);
  const npcProjectilesRef = useRef<NpcProjectileEntity[]>([]);
  const rewardRef = useRef<RewardEntity | null>(null);
  const pendingAscensionWaveRef = useRef<number | null>(null);
  const ascendedSpawnedRef = useRef(false);
  const storyKillTriggeredRef = useRef(false);
  const storyPhaseTimerRef = useRef(0);
  const npcThrowTimerRef = useRef(0);
  const npcDialogueTimerRef = useRef(0);
  const npcBubbleTimerRef = useRef(0);
  const lastStoryPhaseRef = useRef<StoryPhase | null>(null);
  const bossBubbleTimerRef = useRef(0);
  const bossDialogueShownRef = useRef(false);
  const lastBossPhaseRef = useRef<BossEntity["phase"] | null>(null);
  const bossPhaseMessageTimerRef = useRef(0);
  const rebirthBossKillsRef = useRef(0);
  const noSpawnsRef = useRef(false);
  const pointerRef = useRef<Vector2>({ x: 0, y: 0 });
  const spawnTimerRef = useRef(0);
  const initialLaserWindow = getLaserWindow(0);
  const laserSpawnTimerRef = useRef(
    randomBetween(initialLaserWindow.min, initialLaserWindow.max)
  );
  const nextOrbIdRef = useRef(1);
  const nextProjectileIdRef = useRef(1);
  const nextEnemyProjectileIdRef = useRef(1);
  const nextLaserIdRef = useRef(1);
  const nextBossIdRef = useRef(1);
  const nextRewardIdRef = useRef(1);
  const nextBossScoreRef = useRef(3000);
  const bossWaveRef = useRef(1);
  const wasBossFightRef = useRef(false);
  const nextUpgradeScoreRef = useRef(1000);

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

  const updateMaxLives = useCallback((next: number) => {
    maxLivesRef.current = next;
    setMaxLives(next);
  }, []);

  const updateElapsed = useCallback((next: number) => {
    elapsedRef.current = next;
    setElapsedMs(next);
  }, []);

  const updatePlayerStats = useCallback((next: PlayerStats) => {
    playerStatsRef.current = next;
    setPlayerStats(next);
  }, []);

  const updateUpgradeOptions = useCallback((next: UpgradeOption[]) => {
    upgradeOptionsRef.current = next;
    setUpgradeOptions(next);
  }, []);

  const updateBossSnapshot = useCallback((next: BossEntity | null) => {
    bossRef.current = next;
    setBoss(next);
  }, []);

  const setStoryPhase = useCallback((next: StoryPhase) => {
    storyPhaseRef.current = next;
    setStoryPhaseState(next);
  }, []);

  const updateNpcDialogueIndex = useCallback((next: number) => {
    npcDialogueIndexRef.current = next;
    setNpcDialogueIndex(next);
  }, []);

  const updateNpcSnapshot = useCallback((next: NpcEntity[]) => {
    npcsRef.current = next;
    setNpcs(next);
  }, []);

  const updateNpcBubbleVisible = useCallback((next: number) => {
    setNpcBubbleVisibleMs(next);
  }, []);

  const updateBossBubbleVisible = useCallback((next: number) => {
    setBossBubbleVisibleMs(next);
  }, []);

  const updateBossPhaseMessage = useCallback((message: string, durationMs: number) => {
    setBossPhaseMessage(message);
    setBossPhaseMessageMs(durationMs);
    bossPhaseMessageTimerRef.current = durationMs;
  }, []);

  const resetState = useCallback(() => {
    orbsRef.current = [];
    projectilesRef.current = [];
    enemyProjectilesRef.current = [];
    lasersRef.current = [];
    bossesRef.current = [];
    npcsRef.current = [];
    npcProjectilesRef.current = [];
    rewardRef.current = null;
    pendingAscensionWaveRef.current = null;
    ascendedSpawnedRef.current = false;
    storyKillTriggeredRef.current = false;
    storyPhaseTimerRef.current = 0;
    npcThrowTimerRef.current = 0;
    npcDialogueTimerRef.current = 0;
    npcBubbleTimerRef.current = 0;
    lastStoryPhaseRef.current = null;
    bossBubbleTimerRef.current = 0;
    bossDialogueShownRef.current = false;
    lastBossPhaseRef.current = null;
    bossPhaseMessageTimerRef.current = 0;
    rebirthBossKillsRef.current = 0;
    noSpawnsRef.current = false;
    spawnTimerRef.current = 0;
    const resetLaserWindow = getLaserWindow(0);
    laserSpawnTimerRef.current = randomBetween(
      resetLaserWindow.min,
      resetLaserWindow.max
    );
    nextBossScoreRef.current = 3000;
    nextUpgradeScoreRef.current = 1000;
    bossWaveRef.current = 1;
    wasBossFightRef.current = false;
    updateScore(0);
    updateLives(3);
    updateMaxLives(3);
    updateElapsed(0);
    updatePlayerStats(playerConfig);
    updateUpgradeOptions([]);
    updateBossSnapshot(null);
    setMissionComplete(false);
    updateNpcSnapshot([]);
    updateNpcDialogueIndex(0);
    setStoryPhase(mode === "story" ? "intro_dialogue" : "escalation");
    setNpcBubbleVisibleMs(0);
    setBossDialogueIndex(0);
    setBossBubbleVisibleMs(0);
    setBossPhaseMessage("");
    setBossPhaseMessageMs(0);
  }, [
    updateElapsed,
    updateLives,
    updateMaxLives,
    updateBossSnapshot,
    updateNpcSnapshot,
    updateNpcDialogueIndex,
    updatePlayerStats,
    updateScore,
    updateUpgradeOptions,
    setStoryPhase,
    mode,
    updateBossBubbleVisible,
    updateBossPhaseMessage,
  ]);

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

  const createStoryNpcs = useCallback((bounds: Bounds) => {
    const groupCount = Math.floor(randomBetween(5, 7));
    const npcRadius = 16;
    const npcs: NpcEntity[] = [];
    let nextId = 1;

    const screenCenters = [
      { x: 0.2, y: 0.22 },
      { x: 0.8, y: 0.24 },
      { x: 0.2, y: 0.48 },
      { x: 0.8, y: 0.5 },
      { x: 0.5, y: 0.2 },
    ];
    const pickedCenters: Array<{ x: number; y: number }> = [];

    for (let groupId = 1; groupId <= groupCount; groupId += 1) {
      let center = screenCenters[Math.floor(Math.random() * screenCenters.length)];
      let tries = 0;
      while (
        pickedCenters.some(
          (other) => Math.hypot(other.x - center.x, other.y - center.y) < 0.28
        ) &&
        tries < 8
      ) {
        center = screenCenters[Math.floor(Math.random() * screenCenters.length)];
        tries += 1;
      }
      pickedCenters.push(center);
      const centerX = bounds.width * center.x + randomBetween(-20, 20);
      const centerY = bounds.height * center.y + randomBetween(-16, 16);
      const groupSize = Math.round(randomBetween(1, 3));
      const offsets =
        groupSize === 1
          ? [0]
          : groupSize === 2
          ? [-npcRadius * 0.9, npcRadius * 0.9]
          : [-npcRadius * 1.4, 0, npcRadius * 1.4];
      offsets.forEach((offset, offsetIndex) => {
        const position = {
          x: clamp(
            centerX + offset + randomBetween(-6, 6),
            npcRadius,
            bounds.width - npcRadius
          ),
          y: clamp(
            centerY +
              (offsetIndex % 2 === 0 ? -npcRadius * 0.7 : npcRadius * 0.7) +
              randomBetween(-6, 6),
            npcRadius,
            bounds.height - npcRadius
          ),
        };
        const overlaps = npcs.some(
          (existing) =>
            Math.hypot(existing.position.x - position.x, existing.position.y - position.y) <
            npcRadius * 2.1
        );
        if (overlaps) return;
        npcs.push({
          id: nextId++,
          groupId,
          position,
          radius: npcRadius,
          hp: 3,
          maxHp: 3,
          mood: "friendly",
          isAlive: true,
        });
      });
    }

    return npcs;
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

  const spawnEnemyProjectiles = useCallback(
    (
      origin: Vector2,
      baseDirection: Vector2,
      mode: "single" | "spread",
      count: number,
      spreadDeg: number,
      speedOverride?: number,
      source: EnemyProjectileEntity["source"] = "orb"
    ) => {
      const speed = speedOverride ?? enemyProjectileSpeed;
      const baseAngle = Math.atan2(baseDirection.y, baseDirection.x);
      const projectiles: EnemyProjectileEntity[] = [];
      const angleStep =
        count > 1 ? (spreadDeg * (Math.PI / 180)) / (count - 1) : 0;
      const startAngle =
        mode === "spread" && count > 1
          ? baseAngle - angleStep * (count - 1) * 0.5
          : baseAngle;

      for (let i = 0; i < count; i += 1) {
        const angle = mode === "spread" ? startAngle + angleStep * i : baseAngle;
        projectiles.push({
          id: nextEnemyProjectileIdRef.current++,
          position: { ...origin },
          velocity: { x: Math.cos(angle) * speed, y: Math.sin(angle) * speed },
          radius: enemyProjectileRadius,
          damage: enemyProjectileDamage,
          source,
        });
      }

      enemyProjectilesRef.current = [
        ...enemyProjectilesRef.current,
        ...projectiles,
      ];
    },
    []
  );

  const update = useCallback(
    (deltaMs: number, bounds: Bounds, playerPosition: Vector2) => {
      if (statusRef.current !== "playing") return;
      if (bounds.width <= 0 || bounds.height <= 0) return;

      const deltaSec = deltaMs / 1000;
      const nextElapsed = elapsedRef.current + deltaMs;
      updateElapsed(nextElapsed);
      let damageTaken = 0;
      let scoreDelta = 0;

      const difficulty = getDifficulty(nextElapsed);
      const isStoryMode = mode === "story";
      const isBossOnly = devConfig.bossOnly;
      const currentStoryPhase = storyPhaseRef.current;

      if (isStoryMode) {
        if (lastStoryPhaseRef.current !== currentStoryPhase) {
          lastStoryPhaseRef.current = currentStoryPhase;
          if (
            currentStoryPhase === "intro_dialogue" ||
            currentStoryPhase === "harmless_throwing"
          ) {
            npcBubbleTimerRef.current = 9000;
            updateNpcBubbleVisible(9000);
          } else if (
            currentStoryPhase === "first_kill_triggered" ||
            currentStoryPhase === "escalation"
          ) {
            npcBubbleTimerRef.current = 7000;
            updateNpcBubbleVisible(7000);
          } else {
            npcBubbleTimerRef.current = 0;
            updateNpcBubbleVisible(0);
          }
        }

        if (npcBubbleTimerRef.current > 0) {
          npcBubbleTimerRef.current = Math.max(0, npcBubbleTimerRef.current - deltaMs);
          updateNpcBubbleVisible(npcBubbleTimerRef.current);
        }
      }

      if (bossBubbleTimerRef.current > 0) {
        bossBubbleTimerRef.current = Math.max(0, bossBubbleTimerRef.current - deltaMs);
        updateBossBubbleVisible(bossBubbleTimerRef.current);
      }

      if (bossPhaseMessageTimerRef.current > 0) {
        bossPhaseMessageTimerRef.current = Math.max(
          0,
          bossPhaseMessageTimerRef.current - deltaMs
        );
        setBossPhaseMessageMs(bossPhaseMessageTimerRef.current);
        if (bossPhaseMessageTimerRef.current === 0) {
          setBossPhaseMessage("");
        }
      }

      if (
        isStoryMode &&
        npcsRef.current.length === 0 &&
        !storyKillTriggeredRef.current &&
        currentStoryPhase !== "escalation" &&
        currentStoryPhase !== "boss_fight"
      ) {
        const initialNpcs = createStoryNpcs(bounds);
        updateNpcSnapshot(initialNpcs);
      }

      if (isStoryMode) {
        if (currentStoryPhase === "intro_dialogue") {
          storyPhaseTimerRef.current += deltaMs;
          if (storyPhaseTimerRef.current >= 3500) {
            storyPhaseTimerRef.current = 0;
            setStoryPhase("harmless_throwing");
          }
        } else if (currentStoryPhase === "first_kill_triggered") {
          storyPhaseTimerRef.current -= deltaMs;
          if (storyPhaseTimerRef.current <= 0) {
            setStoryPhase("escalation");
          }
        }

        if (
          currentStoryPhase === "intro_dialogue" ||
          currentStoryPhase === "harmless_throwing"
        ) {
          npcDialogueTimerRef.current += deltaMs;
          if (npcDialogueTimerRef.current >= 2600) {
            npcDialogueTimerRef.current = 0;
            updateNpcDialogueIndex(npcDialogueIndexRef.current + 1);
          }
        }
      }
      if (isBossOnly && bossesRef.current.length === 0) {
        const spawnWave = bossWaveRef.current;
        const boss = createBoss(bounds, spawnWave);
        bossesRef.current = [{ ...boss, id: nextBossIdRef.current++ }];
        bossWaveRef.current += 1;
        wasBossFightRef.current = true;
        noSpawnsRef.current = true;
        orbsRef.current = [];
        enemyProjectilesRef.current = [];
        lasersRef.current = [];
        spawnTimerRef.current = 0;
        if (spawnWave === 1 && !bossDialogueShownRef.current) {
          bossDialogueShownRef.current = true;
          bossBubbleTimerRef.current = 6500;
          setBossDialogueIndex(0);
          updateBossBubbleVisible(6500);
        }
      }
      const isBossFight = bossesRef.current.length > 0;
      const allowSpawns =
        !noSpawnsRef.current &&
        (!isStoryMode ||
          currentStoryPhase === "escalation" ||
          currentStoryPhase === "boss_fight");

      if (isStoryMode && isBossFight && currentStoryPhase !== "boss_fight") {
        setStoryPhase("boss_fight");
      }

      if (!isBossFight && allowSpawns) {
        const spawnInterval = Math.max(
          450,
          getSpawnIntervalBase(scoreRef.current) - difficulty * 180
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
      }

      if (!isBossFight && allowSpawns) {
        const laserWindow = getLaserWindow(difficulty);
        laserSpawnTimerRef.current -= deltaMs;
        if (laserSpawnTimerRef.current <= 0) {
          laserSpawnTimerRef.current = randomBetween(laserWindow.min, laserWindow.max);
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
        !isBossOnly &&
        !isBossFight &&
        allowSpawns &&
        scoreRef.current >= nextBossScoreRef.current
      ) {
        const spawnWave = bossWaveRef.current;
        const boss = createBoss(bounds, spawnWave);
        bossesRef.current = [{ ...boss, id: nextBossIdRef.current++ }];
        bossWaveRef.current += 1;
        nextBossScoreRef.current += 3000;
        wasBossFightRef.current = true;
        noSpawnsRef.current = true;
        orbsRef.current = [];
        enemyProjectilesRef.current = [];
        lasersRef.current = [];
        spawnTimerRef.current = 0;
        if (spawnWave === 1 && !bossDialogueShownRef.current) {
          bossDialogueShownRef.current = true;
          bossBubbleTimerRef.current = 6500;
          setBossDialogueIndex(0);
          updateBossBubbleVisible(6500);
        }
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

      const npcHitProjectiles = new Set<number>();

      if (isStoryMode && isBossFight && npcsRef.current.length) {
        updateNpcSnapshot([]);
      }

      if (isStoryMode && npcsRef.current.length) {
        let killTriggered = storyKillTriggeredRef.current;
        const nextNpcs: NpcEntity[] = [];

        npcsRef.current.forEach((npc) => {
          let hp = npc.hp;
          let position = npc.position;
          if (npc.mood === "hostile") {
            const toPlayer = normalize({
              x: playerPosition.x - npc.position.x,
              y: playerPosition.y - npc.position.y,
            });
            const speed = 28;
            position = {
              x: npc.position.x + toPlayer.x * speed * deltaSec,
              y: npc.position.y + toPlayer.y * speed * deltaSec,
            };
          }
          if (npc.isAlive) {
            for (let i = 0; i < updatedProjectiles.length; i += 1) {
              const projectile = updatedProjectiles[i];
              const dx = position.x - projectile.position.x;
              const dy = position.y - projectile.position.y;
              const distanceSq = dx * dx + dy * dy;
              const radiusSum = npc.radius + projectile.radius;
              if (distanceSq <= radiusSum * radiusSum) {
                npcHitProjectiles.add(i);
                hp -= playerStatsRef.current.damagePerShot;
                break;
              }
            }
          }

          if (hp > 0) {
            nextNpcs.push({
              ...npc,
              hp,
              position,
              mood: killTriggered ? "hostile" : npc.mood,
              isAlive: true,
            });
          } else if (!killTriggered && npc.isAlive) {
            killTriggered = true;
          }
        });

        if (killTriggered && !storyKillTriggeredRef.current) {
          storyKillTriggeredRef.current = true;
          storyPhaseTimerRef.current = 1200;
          setStoryPhase("first_kill_triggered");
          npcProjectilesRef.current = [];
          npcThrowTimerRef.current = 0;
          updateNpcDialogueIndex(0);
          npcBubbleTimerRef.current = 7000;
          updateNpcBubbleVisible(7000);
        }

        if (killTriggered) {
          const hostileNpcs = nextNpcs.map((npc) => ({
            ...npc,
            mood: "hostile" as const,
          }));
          updateNpcSnapshot(hostileNpcs);
        } else {
          updateNpcSnapshot(nextNpcs);
        }
      }

      if (isStoryMode && currentStoryPhase === "harmless_throwing" && npcsRef.current.length) {
        npcThrowTimerRef.current -= deltaMs;
        if (npcThrowTimerRef.current <= 0) {
          const source = npcsRef.current[Math.floor(Math.random() * npcsRef.current.length)];
          const direction = normalize({
            x: playerPosition.x - source.position.x,
            y: playerPosition.y - source.position.y,
          });
          npcProjectilesRef.current = [
            ...npcProjectilesRef.current,
            {
              id: nextEnemyProjectileIdRef.current++,
              position: { ...source.position },
              velocity: { x: direction.x * 160, y: direction.y * 160 },
              radius: 5,
              damage: 0,
            },
          ];
          npcThrowTimerRef.current = randomBetween(1200, 2000);
        }
      }

      if (
        isStoryMode &&
        (currentStoryPhase === "escalation" || currentStoryPhase === "boss_fight") &&
        npcsRef.current.length
      ) {
        npcThrowTimerRef.current -= deltaMs;
        if (npcThrowTimerRef.current <= 0) {
          const source = npcsRef.current[Math.floor(Math.random() * npcsRef.current.length)];
          const direction = normalize({
            x: playerPosition.x - source.position.x,
            y: playerPosition.y - source.position.y,
          });
          spawnEnemyProjectiles(
            source.position,
            direction,
            "single",
            1,
            0,
            undefined,
            "npc"
          );
          npcThrowTimerRef.current = randomBetween(900, 1400);
        }
      }

      const updatedNpcProjectiles = npcProjectilesRef.current
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

      npcProjectilesRef.current = updatedNpcProjectiles;

      const updatedOrbs: OrbEntity[] = [];

      if (!isBossFight) {
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

          const shootConfig = orbShootConfig[orb.type];
          let nextShootCooldown = orb.shootCooldownMs;
          if (shootConfig && typeof nextShootCooldown === "number") {
            nextShootCooldown -= deltaMs;
            if (nextShootCooldown <= 0) {
              const direction = normalize({
                x: playerPosition.x - nextPosition.x,
                y: playerPosition.y - nextPosition.y,
              });
              const difficultyScale = 1 - difficulty * 0.35;
              const cooldown = randomBetween(
                shootConfig.cooldown[0] * difficultyScale,
                shootConfig.cooldown[1] * difficultyScale
              );
              spawnEnemyProjectiles(
                nextPosition,
                direction,
                shootConfig.mode,
                shootConfig.count,
                shootConfig.spreadDeg,
                shootConfig.projectileSpeed,
                "orb"
              );
              nextShootCooldown = cooldown;
            }
          }

          updatedOrbs.push({
            ...orb,
            position: nextPosition,
            velocity: nextVelocity,
            isPhasing: nextIsPhasing,
            phaseTimerMs: nextPhaseTimer,
            shootCooldownMs: nextShootCooldown,
          });
        });
      } else if (orbsRef.current.length) {
        orbsRef.current = [];
      }

      const playerHitOrbs = new Set<number>();
      const hitProjectiles = new Set<number>(npcHitProjectiles);
      const spawnedOrbs: OrbEntity[] = [];
      const remainingOrbs: OrbEntity[] = [];

      if (!isBossFight) {
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

        updatedOrbs.forEach((orb, orbIndex) => {
          if (playerHitOrbs.has(orbIndex)) return;
          let nextHp = orb.hp;
          let destroyed = false;

          if (!(orb.type === "phasing" && orb.isPhasing)) {
            for (let i = 0; i < updatedProjectiles.length; i += 1) {
              if (hitProjectiles.has(i)) continue;
              const projectile = updatedProjectiles[i];
              const dx = orb.position.x - projectile.position.x;
              const dy = orb.position.y - projectile.position.y;
              const distanceSq = dx * dx + dy * dy;
              const radiusSum = orb.radius + projectile.radius;
              if (distanceSq <= radiusSum * radiusSum) {
                hitProjectiles.add(i);
                nextHp -= playerStatsRef.current.damagePerShot;
                if (nextHp <= 0) {
                  destroyed = true;
                  scoreDelta += orb.type === "slow" ? 150 : 100;
                  if (orb.type === "splitting") {
                    const splitCount = Math.floor(randomBetween(2, 4));
                    for (let j = 0; j < splitCount; j += 1) {
                      spawnedOrbs.push(
                        createSplitOrb(orb, nextOrbIdRef.current++)
                      );
                    }
                  }
                }
                break;
              }
            }
          }

          if (!destroyed) {
            remainingOrbs.push({
              ...orb,
              hp: nextHp,
            });
          }
        });

        orbsRef.current = [...remainingOrbs, ...spawnedOrbs];
      }

      const bossEvents: Array<ReturnType<typeof updateBoss>["events"][number]> = [];
      if (bossesRef.current.length) {
        const updatedBosses: BossEntity[] = [];
        bossesRef.current.forEach((boss) => {
          let hp = boss.hp;
          if (!boss.isInvulnerable) {
            updatedProjectiles.forEach((projectile, projectileIndex) => {
              if (hitProjectiles.has(projectileIndex)) return;
              const dx = boss.position.x - projectile.position.x;
              const dy = boss.position.y - projectile.position.y;
              const distanceSq = dx * dx + dy * dy;
              const radiusSum = boss.radius + projectile.radius;
              if (distanceSq <= radiusSum * radiusSum) {
                hitProjectiles.add(projectileIndex);
                hp -= playerStatsRef.current.damagePerShot;
              }
            });
          }

          const dx = boss.position.x - playerPosition.x;
          const dy = boss.position.y - playerPosition.y;
          if (dx * dx + dy * dy <= (boss.radius + playerRadius) ** 2) {
            damageTaken += 2;
          }

          if (hp <= 0) {
            const isEnteringDeath = boss.phase !== "dying";
            const dyingBoss: BossEntity = isEnteringDeath
              ? {
                  ...boss,
                  hp: 0,
                  phase: "dying",
                  isInvulnerable: true,
                  deathTimerMs: bossDeathConfig.deathDurationMs,
                }
              : { ...boss, hp: 0 };
            if (isEnteringDeath) {
              scoreDelta += 900;
            }
            const { boss: nextBoss } = updateBoss(
              dyingBoss,
              deltaMs,
              bounds,
              playerPosition
            );
            if (nextBoss.deathTimerMs <= 0) {
              if (nextBoss.isAscended) {
                rebirthBossKillsRef.current += 1;
                noSpawnsRef.current = true;
                if (mode === "story") {
                  setStoryPhase("post_second_rebirth");
                }
                orbsRef.current = [];
                enemyProjectilesRef.current = [];
                lasersRef.current = [];
              }
              if (!rewardRef.current) {
                rewardRef.current = {
                  id: nextRewardIdRef.current++,
                  position: { ...nextBoss.position },
                  radius: bossDeathConfig.rewardRadius,
                  pulseMs: 0,
                };
                pendingAscensionWaveRef.current = nextBoss.wave;
              }
              return;
            }
            updatedBosses.push(nextBoss);
            return;
          }

          let updatedBoss = { ...boss, hp };
          updatedBoss = checkPhaseTransition(updatedBoss);
          const { boss: nextBoss, events } = updateBoss(
            updatedBoss,
            deltaMs,
            bounds,
            playerPosition
          );
          bossEvents.push(...events);
          updatedBosses.push(nextBoss);
        });

        bossesRef.current = updatedBosses;
      }

      if (rewardRef.current) {
        rewardRef.current = {
          ...rewardRef.current,
          pulseMs: rewardRef.current.pulseMs + deltaMs,
        };
        const dx = rewardRef.current.position.x - playerPosition.x;
        const dy = rewardRef.current.position.y - playerPosition.y;
        if (dx * dx + dy * dy <= (rewardRef.current.radius + playerRadius) ** 2) {
          const ascensionWave = pendingAscensionWaveRef.current;
          rewardRef.current = null;
          pendingAscensionWaveRef.current = null;
          if (ascensionWave === 1 && bossesRef.current.length === 0) {
            if (ascendedSpawnedRef.current) {
              setMissionComplete(true);
              setStatus("paused");
              return;
            }
            const ascendedBoss = createBoss(bounds, ascensionWave);
            bossesRef.current = [
              {
                ...ascendedBoss,
                id: nextBossIdRef.current++,
                hp: Math.round(ascendedBoss.maxHp * ascendedBossConfig.hpMultiplier),
                maxHp: Math.round(ascendedBoss.maxHp * ascendedBossConfig.hpMultiplier),
                phase: "ascending",
                isAscended: true,
                isInvulnerable: true,
                ascendTimerMs: bossBaseConfig.entryInvulnerableMs,
              },
            ];
            ascendedSpawnedRef.current = true;
            bossBubbleTimerRef.current = 6500;
            setBossDialogueIndex(0);
            updateBossBubbleVisible(6500);
          }
        }
      }

      if (bossEvents.length) {
        const bossProjectiles: EnemyProjectileEntity[] = [];
        bossEvents.forEach((event) => {
          if (event.type === "projectiles") {
            event.velocities.forEach((velocity) => {
              bossProjectiles.push({
                id: nextEnemyProjectileIdRef.current++,
                position: { ...event.origin },
                velocity,
                radius: bossProjectileConfig.radius,
                damage: bossProjectileConfig.damage,
                source: "boss",
              });
            });
          } else {
            lasersRef.current = [
              ...lasersRef.current,
              {
                id: nextLaserIdRef.current++,
                axis: event.axis,
                position: event.position,
                warningMs: event.warningMs,
                firingMs: event.firingMs,
                status: "warning",
                hasHit: false,
              },
            ];
          }
        });
        if (bossProjectiles.length) {
          enemyProjectilesRef.current = [
            ...enemyProjectilesRef.current,
            ...bossProjectiles,
          ];
        }
      }

      if (wasBossFightRef.current && bossesRef.current.length === 0) {
        wasBossFightRef.current = false;
        spawnTimerRef.current = 0;
        const resetLaserWindow = getLaserWindow(difficulty);
        laserSpawnTimerRef.current = randomBetween(
          resetLaserWindow.min,
          resetLaserWindow.max
        );
      }

      if (
        isStoryMode &&
        !isBossFight &&
        currentStoryPhase === "boss_fight" &&
        !noSpawnsRef.current
      ) {
        setStoryPhase("escalation");
      }

      updateBossSnapshot(bossesRef.current[0] ?? null);

      if (bossesRef.current.length) {
        const currentPhase = bossesRef.current[0].phase;
        if (lastBossPhaseRef.current !== currentPhase) {
          lastBossPhaseRef.current = currentPhase;
          const isAscendedBoss = bossesRef.current[0].isAscended;
          if (currentPhase === "transition") {
            updateBossPhaseMessage(
              isAscendedBoss ? "ASCENSION RISES. KNEEL." : "ENOUGH. YOU FORCE MY HAND.",
              2400
            );
          } else if (currentPhase === "phase2") {
            updateBossPhaseMessage(
              isAscendedBoss ? "YOUR END IS WRITTEN." : "I WILL SHATTER YOU.",
              2200
            );
          } else if (currentPhase === "phase3") {
            updateBossPhaseMessage(
              isAscendedBoss ? "I AM BEYOND YOU." : "THIS ENDS NOW.",
              2400
            );
          }
        }
      } else if (lastBossPhaseRef.current) {
        lastBossPhaseRef.current = null;
      }

      const remainingProjectiles = updatedProjectiles.filter(
        (_, index) => !hitProjectiles.has(index)
      );
      projectilesRef.current = remainingProjectiles;

      const updatedEnemyProjectiles = enemyProjectilesRef.current
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

      const enemyHitProjectiles = new Set<number>();
      updatedEnemyProjectiles.forEach((projectile, index) => {
        const dx = projectile.position.x - playerPosition.x;
        const dy = projectile.position.y - playerPosition.y;
        if (dx * dx + dy * dy <= (projectile.radius + playerRadius) ** 2) {
          enemyHitProjectiles.add(index);
          damageTaken += projectile.damage;
        }
      });
      enemyProjectilesRef.current = updatedEnemyProjectiles.filter(
        (_, index) => !enemyHitProjectiles.has(index)
      );

      if (scoreDelta) {
        updateScore(scoreRef.current + scoreDelta);
      }

      if (damageTaken) {
        const nextLives = clamp(livesRef.current - damageTaken, 0, maxLivesRef.current);
        updateLives(nextLives);
        if (nextLives <= 0) {
          setStatus("gameover");
        }
      }

      if (
        statusRef.current === "playing" &&
        upgradeOptionsRef.current.length === 0
      ) {
        const nextScore = scoreRef.current + scoreDelta;
        if (nextScore >= nextUpgradeScoreRef.current) {
          nextUpgradeScoreRef.current += 1200;
          setStatus("paused");
          updateUpgradeOptions(pickUpgrades(3));
        }
      }
    },
    [
      createStoryNpcs,
      mode,
      setStoryPhase,
      updateBossSnapshot,
      updateLives,
      updateBossBubbleVisible,
      updateBossPhaseMessage,
      updateNpcBubbleVisible,
      updateNpcDialogueIndex,
      updateNpcSnapshot,
      updateScore,
      updateUpgradeOptions,
      setStatus,
    ]
  );

  const applyUpgrade = useCallback(
    (upgradeId: UpgradeOption["id"]) => {
      const currentStats = playerStatsRef.current;
      if (upgradeId === "damage") {
        updatePlayerStats({
          ...currentStats,
          damagePerShot: currentStats.damagePerShot + 1,
        });
      } else if (upgradeId === "fire_rate") {
        updatePlayerStats({
          ...currentStats,
          fireCooldownMs: Math.max(60, Math.round(currentStats.fireCooldownMs * 0.85)),
        });
      } else if (upgradeId === "move_speed") {
        updatePlayerStats({
          ...currentStats,
          moveSpeed: Math.round(currentStats.moveSpeed * 1.15),
        });
      } else if (upgradeId === "heal") {
        updateLives(clamp(livesRef.current + 1, 0, maxLivesRef.current));
      } else if (upgradeId === "max_lives") {
        const nextMax = maxLivesRef.current + 1;
        updateMaxLives(nextMax);
        updateLives(clamp(livesRef.current + 1, 0, nextMax));
      }

      updateUpgradeOptions([]);
      if (statusRef.current !== "gameover") {
        setStatus("playing");
      }
    },
    [setStatus, updateLives, updateMaxLives, updatePlayerStats, updateUpgradeOptions]
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
      applyUpgrade,
    }),
    [applyUpgrade, pauseGame, resetGame, resumeGame, setPointer, shoot, startGame, update]
  );

  return {
    state: {
      score,
      lives,
      maxLives,
      status,
      elapsedMs,
      playerStats,
      upgradeOptions,
      boss,
      missionComplete,
      mode,
      storyPhase,
      npcDialogueIndex,
      npcBubbleVisibleMs,
      bossDialogueIndex,
      bossBubbleVisibleMs,
      bossPhaseMessage,
      bossPhaseMessageMs,
      npcs,
    },
    refs: {
      orbsRef,
      projectilesRef,
      enemyProjectilesRef,
      lasersRef,
      bossesRef,
      npcsRef,
      npcProjectilesRef,
      rewardRef,
      pointerRef,
    },
    actions,
  };
}
