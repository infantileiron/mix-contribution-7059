export const ROLES:Record<string,string>={admin:'管理员',analyst:'用水分析员',viewer:'只读复核员'};
export const RUN_STATUS:Record<string,string>={queued:'排队中',running:'分解中',completed:'已完成',failed:'失败'};
export const FACTORS={scale:'规模变化',structure:'结构变化',intensity:'强度变化'};
export const DECISIONS:Record<string,string>={accepted:'接受并记录口径',needs_attention:'需继续核查'};
