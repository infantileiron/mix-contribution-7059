import type {Dataset, Observation, Revision} from '../types/domain';

/**
 * 重建指定版本的观测行：从当前行出发，倒序回滚 base_version >= target 的修订。
 * target 等于当前版本时直接返回当前行。
 */
export function rowsAtVersion(dataset: Dataset, revisions: Revision[], target: number): Observation[] {
  if (target >= dataset.current_version) {
    return dataset.rows.map(r => ({...r}));
  }
  const rows = new Map(dataset.rows.map(r => [`${r.zone}|${r.period}`, {...r}]));
  const ordered = [...revisions].sort((a, b) => b.new_version - a.new_version);
  for (const rev of ordered) {
    if (rev.base_version < target) {
      break;
    }
    for (const change of rev.changes) {
      const key = `${change.zone}|${change.period}`;
      const row = rows.get(key);
      if (row) {
        row.scale = change.before.scale;
        row.water = change.before.water;
      }
    }
  }
  return [...rows.values()];
}

/** 当前版本中已被修订过的分区月份键集合，用于历史视图高亮差异。 */
export function changedKeys(revisions: Revision[], target: number): Set<string> {
  const keys = new Set<string>();
  for (const rev of revisions) {
    if (rev.base_version >= target) {
      for (const change of rev.changes) {
        keys.add(`${change.zone}|${change.period}`);
      }
    }
  }
  return keys;
}
