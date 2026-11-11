import * as datasets from '../api/datasets';import * as comparisons from '../api/comparisons';import * as runs from '../api/runs';import * as reviews from '../api/reviews';import * as reports from '../api/reports';import * as audit from '../api/audit';
export async function loadWorkspace(){const [d,c,r,v,p,a]=await Promise.all([datasets.list(),comparisons.list(),runs.list(),reviews.list(),reports.list(),audit.list()]);return {datasets:d,comparisons:c,runs:r,reviews:v,reports:p,audit:a}}
export type Workspace=Awaited<ReturnType<typeof loadWorkspace>>;
