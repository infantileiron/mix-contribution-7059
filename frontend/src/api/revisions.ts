import {request,post} from './client';
import type {Revision} from '../types/domain';

export const list=(datasetId:string)=>request<Revision[]>(`/datasets/${datasetId}/revisions`);
export const create=(datasetId:string,data:unknown)=>post<{revision:Revision}>(`/datasets/${datasetId}/revisions`,data);
