/**
 * Game Feature Contexts
 * 
 * These contexts were extracted from the monolithic PlayState.tsx (1,332 lines)
 * to create focused, single-responsibility state management units.
 * 
 * Architecture:
 * - Each context manages a specific domain of game state
 * - Contexts can be composed together in a provider tree
 * - The original PlayState remains functional for backward compatibility
 * 
 * Context Responsibilities:
 * - GameContext: Core game state (gameId, gameState, cardMap, priority, engine actions)
 * - CombatContext: Combat phase (attackers, blockers, damage assignments, validation)
 * - CastingContext: Spell casting (preparation, mana payment, all cost types)
 * - TargetingContext: Target selection (objects, players, copy targets, validation)
 * - ChoicesContext: Game choices (modal modes, ETB choices, search, replacements, ward)
 * 
 * Usage:
 * @example
 * // In a page component
 * <GameProvider>
 *   <CombatProvider gameState={gameState} cardMap={cardMap} priorityPlayer={priority}>
 *     <YourComponent />
 *   </CombatProvider>
 * </GameProvider>
 * 
 * @example
 * // In a child component
 * const { gameState, runEngineAction } = useGame();
 * const { selectedAttackers, toggleAttacker } = useCombat();
 */

export { GameProvider, useGame, type GameContextValue } from './GameContext';
export { CombatProvider, useCombat, type CombatContextValue } from './CombatContext';
export { CastingProvider, useCasting, type CastingContextValue } from './CastingContext';
export { TargetingProvider, useTargetingContext, type TargetingContextValue } from './TargetingContext';
export { ChoicesProvider, useChoices, type ChoicesContextValue } from './ChoicesContext';
