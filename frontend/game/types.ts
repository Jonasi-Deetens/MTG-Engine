export type GameStatus = "idle" | "playing" | "paused" | "gameover";

export type GameMode = "classic" | "story";

export type StoryPhase =
  | "intro_dialogue"
  | "harmless_throwing"
  | "first_kill_triggered"
  | "escalation"
  | "boss_fight"
  | "post_second_rebirth";

export type Vector2 = {
  x: number;
  y: number;
};

export type PlayerStats = {
  moveSpeed: number;
  fireCooldownMs: number;
  fireOnHold: boolean;
  damagePerShot: number;
};

export type UpgradeId =
  | "damage"
  | "fire_rate"
  | "move_speed"
  | "heal"
  | "max_lives";

export type UpgradeOption = {
  id: UpgradeId;
  title: string;
  description: string;
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
  hp: number;
  maxHp: number;
  damage: number;
  isPhasing?: boolean;
  phaseTimerMs?: number;
  shootCooldownMs?: number;
};

export type ProjectileEntity = {
  id: number;
  position: Vector2;
  velocity: Vector2;
  radius: number;
};

export type EnemyProjectileEntity = {
  id: number;
  position: Vector2;
  velocity: Vector2;
  radius: number;
  damage: number;
  source: "orb" | "boss" | "npc";
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

export type RewardEntity = {
  id: number;
  position: Vector2;
  radius: number;
  pulseMs: number;
};

export type NpcMood = "friendly" | "hostile";

export type NpcEntity = {
  id: number;
  groupId: number;
  position: Vector2;
  radius: number;
  hp: number;
  maxHp: number;
  mood: NpcMood;
  isAlive: boolean;
};

export type NpcProjectileEntity = {
  id: number;
  position: Vector2;
  velocity: Vector2;
  radius: number;
  damage: number;
};

export type { BossEntity, BossPhase, BossAttackState, BossAttackType } from "@/game/boss/types";

export type Bounds = {
  width: number;
  height: number;
};
