export interface User{email:string;role:string}
export interface Observation{zone:string;period:string;scale:number;water:number}
export interface Dataset{id:string;name:string;source:string;rows:Observation[];created_at:string}
export interface Comparison{id:string;name:string;dataset_id:string;period_before:string;period_after:string;created_at:string}
export interface Factors{scale:number;structure:number;intensity:number}
export interface ZoneContribution extends Factors{zone:string}
export interface Decomposition{contributions:Factors;residual:number;zones:ZoneContribution[];method:string}
export interface Result{period_before:string;period_after:string;water_before:number;water_after:number;delta:number;scale_before:number;scale_after:number;share_sum_before:number;share_sum_after:number;shapley:Decomposition;lmdi:Decomposition;observations:{zone:string;scale_before:number;scale_after:number;share_before:number;share_after:number;intensity_before:number;intensity_after:number;water_before:number;water_after:number}[];checksum:string;assumptions:string[]}
export interface Run{id:string;comparison_id:string;status:string;result:Result;error:string;created_at:string}
export interface Review{id:string;run_id:string;note:string;decision:string;author:string;created_at:string}
export interface Report{id:string;run_id:string;title:string;published_by:string;created_at:string}
export interface Audit{id:string;actor:string;action:string;status:number;created_at:string}
