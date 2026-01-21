import { EngineGameObjectSnapshot } from '@/lib/engine';

export const getObjectsByIds = (
  ids: string[],
  objects: EngineGameObjectSnapshot[],
  expectedZone?: EngineGameObjectSnapshot['zone']
): EngineGameObjectSnapshot[] => {
  const map = new Map(objects.map((obj) => [obj.id, obj]));
  return ids
    .map((id) => map.get(id))
    .filter((obj): obj is EngineGameObjectSnapshot => Boolean(obj))
    .filter((obj) => (expectedZone ? obj.zone === expectedZone : true));
};
