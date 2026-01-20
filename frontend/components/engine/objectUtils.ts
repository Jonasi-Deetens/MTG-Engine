import { EngineGameObjectSnapshot } from '@/lib/engine';

export const getObjectsByIds = (
  ids: string[],
  objects: EngineGameObjectSnapshot[]
): EngineGameObjectSnapshot[] => {
  const map = new Map(objects.map((obj) => [obj.id, obj]));
  return ids.map((id) => map.get(id)).filter(Boolean) as EngineGameObjectSnapshot[];
};
