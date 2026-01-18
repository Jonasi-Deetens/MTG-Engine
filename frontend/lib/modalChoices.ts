export type ModalChoiceOption = {
  id: string;
  label: string;
};

export type ModalChoiceConfig = {
  min: number;
  max: number | null;
  modes: ModalChoiceOption[];
};

const extractRootModal = (graph: any): ModalChoiceConfig | null => {
  if (!graph || !Array.isArray(graph.nodes)) return null;
  const rootId = graph.rootNodeId;
  const rootNode = graph.nodes.find((node: any) => node?.id === rootId);
  const modal = rootNode?.data?.modal;
  if (!modal || typeof modal !== 'object') return null;
  return normalizeModalConfig(modal);
};

const normalizeModalConfig = (modal: any): ModalChoiceConfig | null => {
  if (!modal || typeof modal !== 'object') return null;
  const modes = Array.isArray(modal.modes) ? modal.modes : [];
  const normalizedModes = modes
    .map((mode: any) => {
      if (!mode || typeof mode !== 'object') return null;
      const id = typeof mode.id === 'string' ? mode.id.trim() : '';
      if (!id) return null;
      const label = typeof mode.label === 'string' && mode.label.trim() ? mode.label.trim() : id;
      return { id, label };
    })
    .filter(Boolean) as ModalChoiceOption[];
  if (normalizedModes.length === 0) return null;
  const min = Number.isInteger(modal.min) && modal.min >= 0 ? modal.min : 1;
  const max = Number.isInteger(modal.max) && modal.max > 0 ? modal.max : null;
  return { min, max, modes: normalizedModes };
};

const inferModalFromEffects = (graph: any): ModalChoiceConfig | null => {
  if (!graph || !Array.isArray(graph.nodes)) return null;
  const seen = new Set<string>();
  const modes: ModalChoiceOption[] = [];
  graph.nodes.forEach((node: any) => {
    if (node?.type !== 'EFFECT') return;
    const modeId = node?.data?.modeId;
    if (typeof modeId !== 'string' || !modeId.trim()) return;
    const id = modeId.trim();
    if (seen.has(id)) return;
    seen.add(id);
    const label =
      typeof node?.data?.modeLabel === 'string' && node.data.modeLabel.trim()
        ? node.data.modeLabel.trim()
        : id;
    modes.push({ id, label });
  });
  if (modes.length === 0) return null;
  return { min: 1, max: 1, modes };
};

export const deriveModalConfig = (graph: any): ModalChoiceConfig | null => {
  if (!graph) return null;
  if (graph.modal && typeof graph.modal === 'object') {
    const normalized = normalizeModalConfig(graph.modal);
    if (normalized) return normalized;
  }
  const root = extractRootModal(graph);
  if (root) return root;
  return inferModalFromEffects(graph);
};

export const isEffectActiveForModes = (
  effect: any,
  modalConfig: ModalChoiceConfig | null,
  selectedModes: string[]
) => {
  if (!modalConfig) return true;
  const modeId = effect?.modeId;
  if (!modeId || typeof modeId !== 'string') return true;
  if (!Array.isArray(selectedModes) || selectedModes.length === 0) return false;
  return selectedModes.includes(modeId);
};

export const buildModalChoiceErrors = (
  config: ModalChoiceConfig | null,
  selectedModes: string[]
): string[] => {
  if (!config) return [];
  const choices = Array.isArray(selectedModes) ? selectedModes.filter(Boolean) : [];
  if (choices.length === 0 && config.min > 0) {
    return ['Select modal choices before casting.'];
  }
  if (choices.length === 0 && config.min === 0) {
    return [];
  }
  if (choices.some((choice) => !config.modes.some((mode) => mode.id === choice))) {
    return ['Selected mode is not available.'];
  }
  if (choices.length < config.min) {
    return [`Select at least ${config.min} mode(s).`];
  }
  if (config.max !== null && choices.length > config.max) {
    return [`Select no more than ${config.max} mode(s).`];
  }
  return [];
};

