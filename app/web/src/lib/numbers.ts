// The headline numbers, read from the eval's own output. Missing = "—", never a guess.
import data from "@/data/eval.json";

const show = (n: number | null, suffix = "") => (n === null || n === undefined ? "—" : `${n}${suffix}`);

export const ATTACKS = show(data.attacks);
export const UNSAFE_NAMES = show(data.unsafe_tool_name_policy);
export const UNSAFE_GUARD = show(data.unsafe_dejo_guard);
export const FALSE_HOLDS = show(data.false_hold_rate, "%");
export const JOURNEYS = show(data.journeys);
