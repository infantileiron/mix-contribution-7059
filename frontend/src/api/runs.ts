import {request,post} from './client';
import type {Run} from '../types/domain';
export const list=()=>request<Run[]>('/runs');
export const create=(data:unknown)=>post<Run>('/runs',data);
export const recompute=(id:string)=>post<Run>(`/runs/${id}/recompute`,{});
