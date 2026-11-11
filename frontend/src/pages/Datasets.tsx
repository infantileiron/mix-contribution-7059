import {useEffect, useState} from 'react';
import type {Workspace} from '../stores/workspace';
import type {Dataset, Revision} from '../types/domain';
import {PageHeading} from '../components/common/PageHeading';
import {Notice} from '../components/common/Notice';
import {create} from '../api/datasets';
import * as revisionsApi from '../api/revisions';
import {useAsync} from '../hooks/useAsync';
import {number, date} from '../utils/format';
import {rowsAtVersion, changedKeys} from '../utils/revisions';

export function Datasets({data, canWrite, refresh}: { data: Workspace; canWrite: boolean; refresh: () => Promise<void> }) {
  const [selected, setSelected] = useState('');
  const [period, setPeriod] = useState('');
  const [name, setName] = useState('');
  const [source, setSource] = useState('water_observations.json');
  const [text, setText] = useState('');
  const [revisions, setRevisions] = useState<Revision[]>([]);
  const [viewVersion, setViewVersion] = useState<number | null>(null);
  const [editPeriod, setEditPeriod] = useState('');
  const [edits, setEdits] = useState<Record<string, { scale: string; water: string }>>({});
  const [reason, setReason] = useState('');
  const [revBusy, setRevBusy] = useState(false);
  const [revError, setRevError] = useState('');
  const importTask = useAsync();

  const dataset: Dataset | undefined = data.datasets.find(d => d.id === selected) || data.datasets[0];
  const targetVersion = viewVersion ?? dataset?.current_version ?? 1;
  const isHistorical = !!dataset && targetVersion !== dataset.current_version;

  useEffect(() => {
    let alive = true;
    setViewVersion(null);
    setEdits({});
    setRevError('');
    if (!dataset) {
      setRevisions([]);
      return;
    }
    revisionsApi.list(dataset.id)
      .then(rs => {
        if (alive) {
          setRevisions(rs);
        }
      })
      .catch(() => {
        if (alive) {
          setRevisions([]);
        }
      });
    return () => {
      alive = false;
    };
  }, [dataset?.id]);

  const displayRows = dataset ? rowsAtVersion(dataset, revisions, targetVersion) : [];
  const periods = [...new Set(displayRows.map(r => r.period))].sort().reverse();
  const active = periods.includes(period) ? period : periods[0];
  const monthRows = displayRows.filter(r => r.period === active);
  const highlight = changedKeys(revisions, targetVersion);
  const versionOptions = dataset
    ? [...new Set([dataset.current_version, ...revisions.map(r => r.base_version)])].sort((a, b) => b - a)
    : [];

  async function reloadRevisions() {
    if (!dataset) {
      return;
    }
    try {
      setRevisions(await revisionsApi.list(dataset.id));
    } catch {
      /* 留痕加载失败不阻塞观测页 */
    }
  }

  async function submitRevision() {
    if (!dataset) {
      return;
    }
    setRevError('');
    const month = editPeriod || active;
    const currentMonth = dataset.rows.filter(r => r.period === month);
    const payloadRows: { zone: string; period: string; scale: number; water: number }[] = [];
    for (const r of currentMonth) {
      const edit = edits[`${r.zone}|${r.period}`];
      if (!edit) {
        continue;
      }
      const scale = parseFloat(edit.scale);
      const water = parseFloat(edit.water);
      if (!Number.isFinite(scale) || !Number.isFinite(water) || scale <= 0 || water <= 0) {
        setRevError('规模与用水必须为有限正值，零值和负值会被拒绝。');
        return;
      }
      if (scale !== r.scale || water !== r.water) {
        payloadRows.push({zone: r.zone, period: r.period, scale, water});
      }
    }
    if (!payloadRows.length) {
      setRevError('没有检测到数值变化，请先修正至少一个分区的规模或用水。');
      return;
    }
    if (reason.trim().length < 5) {
      setRevError('请填写修订原因（至少5个字），说明本次水表复核的依据。');
      return;
    }
    setRevBusy(true);
    try {
      await revisionsApi.create(dataset.id, {
        reason: reason.trim(),
        base_version: dataset.current_version,
        rows: payloadRows,
      });
      setReason('');
      setEdits({});
      await refresh();
      await reloadRevisions();
    } catch (e) {
      setRevError((e as Error).message);
      // 冲突后基线已变化：刷新工作区并清空编辑，避免再次基于旧版本提交
      setEdits({});
      await refresh();
      await reloadRevisions();
    } finally {
      setRevBusy(false);
    }
  }

  return <>
    <PageHeading label="02 / DISTRICT OBSERVATIONS" title="用同一套分区，读两个月份。">
      规模使用有效作业人日，用水以m³记录。<br/>
      水表复核后可直接修订并写明原因；修订生成新版本，旧版本仍可追溯。
    </PageHeading>

    <section className="paper">
      <div className="section-heading">
        <h2>分区月度观测</h2>
        <div className="filters">
          <select aria-label="选择观测集" value={dataset?.id || ''}
                  onChange={e => {
                    setSelected(e.target.value);
                    setPeriod('');
                    setEditPeriod('');
                  }}>
            {data.datasets.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
          <select aria-label="预览月份" value={active || ''} onChange={e => setPeriod(e.target.value)}>
            {periods.map(p => <option key={p}>{p}</option>)}
          </select>
          {dataset && versionOptions.length > 1 && (
            <select aria-label="观测版本" value={String(targetVersion)}
                    onChange={e => setViewVersion(Number(e.target.value) === dataset.current_version ? null : Number(e.target.value))}>
              {versionOptions.map(v => (
                <option key={v} value={v}>
                  {v === dataset.current_version ? `第${v}版 · 当前` : `第${v}版 · 历史`}
                </option>
              ))}
            </select>
          )}
        </div>
      </div>

      {dataset ? <>
        <div className="data-caption">
          <b>{displayRows.length}条分区月观测</b>
          <span>{dataset.source}</span>
          <span>{periods.length}个月份</span>
          <span className={'version-badge ' + (isHistorical ? 'history' : 'current')}>
            观测版本 v{targetVersion}{isHistorical ? `（当前 v${dataset.current_version}）` : ' · 当前'}
          </span>
        </div>
        {isHistorical && (
          <Notice>正在查看第{targetVersion}版历史观测，数据为只读快照。需要修订请切回「第{dataset.current_version}版 · 当前」。</Notice>
        )}
        <div className="table-scroll">
          <table>
            <thead>
            <tr>
              <th>分区</th>
              <th>月份</th>
              <th>规模 / 人日</th>
              <th>用水 / m³</th>
              <th>单位强度 / m³每人日</th>
            </tr>
            </thead>
            <tbody>
            {monthRows.map(r => {
              const key = `${r.zone}|${r.period}`;
              return <tr key={r.zone} className={highlight.has(key) ? 'row-changed' : undefined}>
                <td>{r.zone}{highlight.has(key) && <span className="rev-flag">已修订</span>}</td>
                <td>{r.period}</td>
                <td>{number(r.scale)}</td>
                <td>{number(r.water, 3)}</td>
                <td>{number(r.water / r.scale, 5)}</td>
              </tr>;
            })}
            </tbody>
          </table>
        </div>
      </> : <Notice>请导入至少两个不同月份的正值观测，再建立两期对照。</Notice>}
    </section>

    {canWrite && dataset && !isHistorical && (
      <section className="paper">
        <h2>修订月度观测（水表复核）</h2>
        <p className="caption">
          修订直接更新当前观测集并生成新版本，需写明复核原因；两人同时修订同一版本时，后提交者会收到冲突提示。
          已排队的分解运行锁定排队时的版本与快照，不受修订影响；修订后可在贡献拆解页用新数据重算。
        </p>
        <div className="grid-form">
          <label>修订月份
            <select aria-label="修订月份" value={editPeriod || active || ''}
                    onChange={e => setEditPeriod(e.target.value)}>
              {[...new Set(dataset.rows.map(r => r.period))].sort().reverse().map(p => <option key={p}>{p}</option>)}
            </select>
          </label>
          <label>修订依据版本
            <input value={`第${dataset.current_version}版（提交时自动校验）`} readOnly/>
          </label>
        </div>
        <div className="table-scroll revision-edit">
          <table>
            <thead>
            <tr><th>分区</th><th>月份</th><th>规模 / 人日</th><th>用水 / m³</th></tr>
            </thead>
            <tbody>
            {dataset.rows.filter(r => r.period === (editPeriod || active)).map(r => {
              const key = `${r.zone}|${r.period}`;
              const edit = edits[key];
              return <tr key={r.zone}>
                <td>{r.zone}</td>
                <td>{r.period}</td>
                <td>
                  <input aria-label={`${r.zone}规模`} inputMode="decimal"
                         value={edit?.scale ?? String(r.scale)}
                         onChange={e => setEdits(prev => ({
                           ...prev,
                           [key]: {scale: e.target.value, water: prev[key]?.water ?? String(r.water)},
                         }))}/>
                </td>
                <td>
                  <input aria-label={`${r.zone}用水`} inputMode="decimal"
                         value={edit?.water ?? String(r.water)}
                         onChange={e => setEdits(prev => ({
                           ...prev,
                           [key]: {scale: prev[key]?.scale ?? String(r.scale), water: e.target.value},
                         }))}/>
                </td>
              </tr>;
            })}
            </tbody>
          </table>
        </div>
        <form className="grid-form" onSubmit={e => {
          e.preventDefault();
          void submitRevision();
        }}>
          <label className="wide">修订原因（必填，至少5个字）
            <textarea aria-label="修订原因" rows={2} required minLength={5} maxLength={500}
                      value={reason} onChange={e => setReason(e.target.value)}
                      placeholder="例如：水表复核发现装配区10月总表与分区表差3.2%，按复核单修正分区水量。"/>
          </label>
          {revError && <Notice error>{revError}</Notice>}
          <button disabled={revBusy}>{revBusy ? '提交中…' : '提交修订并生成新版本'}</button>
        </form>
      </section>
    )}

    {dataset && revisions.length > 0 && (
      <section className="paper">
        <h2>修订历史（{revisions.length}次）</h2>
        {revisions.map(rev => <article key={rev.id} className="revision-record">
          <div className="revision-head">
            <span className="version-badge history">v{rev.base_version} → v{rev.new_version}</span>
            <small>{rev.author} · {date(rev.created_at)}</small>
          </div>
          <p>{rev.reason}</p>
          <div className="table-scroll">
            <table>
              <thead>
              <tr><th>分区</th><th>月份</th><th>规模 旧→新</th><th>用水 旧→新 / m³</th></tr>
              </thead>
              <tbody>
              {rev.changes.map(c => <tr key={`${c.zone}|${c.period}`}>
                <td>{c.zone}</td>
                <td>{c.period}</td>
                <td>{number(c.before.scale)} → <b>{number(c.after.scale)}</b></td>
                <td>{number(c.before.water, 3)} → <b>{number(c.after.water, 3)}</b></td>
              </tr>)}
              </tbody>
            </table>
          </div>
          <small className="checksum-line">旧校验码 {rev.checksum_before.slice(0, 16)}… · 新校验码 {rev.checksum_after.slice(0, 16)}…</small>
        </article>)}
      </section>
    )}

    {canWrite && <section className="paper">
      <h2>导入分区月度数据</h2>
      <form className="grid-form" onSubmit={e => {
        e.preventDefault();
        importTask.execute(async () => {
          await create({name, source, rows: JSON.parse(text)});
          setName('');
          setText('');
          await refresh();
        });
      }}>
        <label>观测集名称<input minLength={2} required value={name} onChange={e => setName(e.target.value)}/></label>
        <label>来源文件名<input value={source} onChange={e => setSource(e.target.value)}/></label>
        <label className="wide">JSON观测数组
          <textarea rows={4} required value={text} onChange={e => setText(e.target.value)}
                    placeholder={'[{"zone":"研发东区","period":"2026-09","scale":2500,"water":230}, …]'}/>
        </label>
        {importTask.error && <Notice error>{importTask.error}</Notice>}
        <button disabled={importTask.busy}>核查并导入</button>
      </form>
    </section>}
  </>;
}
