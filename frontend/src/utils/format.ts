export const number=(v:number|undefined,d=2)=>v==null?'—':v.toLocaleString('zh-CN',{minimumFractionDigits:d,maximumFractionDigits:d});
export const signed=(v:number)=>`${v>=0?'+':''}${number(v)}`;
export const percent=(v:number)=>number(v*100,2)+'%';
export const date=(v:string)=>new Date(v).toLocaleString('zh-CN',{hour12:false});
