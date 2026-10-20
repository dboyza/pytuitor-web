// Shapes returned by the local API in src/pytuitor_web/service.py.

export type Status = "new" | "in progress" | "familiar" | "completed";
export type StageName = "build" | "repair";

export type Section = {
  id: string;
  title: string;
  description: string;
  optional: boolean;
};

export type Chapter = {
  id: string;
  number: number;
  title: string;
  outcome: string;
  section_id: string;
  prerequisites: string[];
  activities: string[];
};

export type ActivitySummary = {
  id: string;
  title: string;
  subtitle: string;
  minutes: number;
  concepts: string[];
  chapter_id: string;
  milestone: boolean;
  build_label: string;
};

export type Catalog = {
  version: string;
  counts: { lessons: number; milestones: number; chapters: number };
  sections: Section[];
  chapters: Chapter[];
  activities: Record<string, ActivitySummary>;
  categories: { id: string; title: string; concepts: string[] }[];
};

export type Tally = { completed: number; familiar: number; total: number };

export type AppState = {
  onboarded: boolean;
  familiar: string[];
  last_lesson: string | null;
  statuses: Record<string, Status>;
  next: { id: string; summary: string; note: string; status: Status } | null;
  progress: { core: Tally; optional: Tally };
  review_suggested: string | null;
  settings: { theme: "dark" | "light" | "system" };
  data_dir: string;
};

export type Flags = {
  build: { passed: boolean };
  repair: { passed: boolean; unlocked: boolean };
  completed: boolean;
};

export type Activity = {
  id: string;
  title: string;
  subtitle: string;
  minutes: number;
  milestone: boolean;
  build_label: string;
  chapter: { id: string; title: string };
  body: string;
  brief: string | null;
  outcome: string | null;
  origin: string | null;
  connection: string | null;
  missing: { id: string; title: string }[];
  prediction: {
    prompt: string;
    choices: string[];
    answered: boolean;
    explanation: string | null;
  } | null;
  updated: boolean;
  stage: StageName;
  stages: Flags;
  completed: boolean;
  note: string;
  checkpoint: string | null;
};

export type Observation = {
  label: string;
  actual: string;
  expected: string;
  comparison: string;
  passed: boolean;
};

export type CheckCase = {
  number: number;
  label: string;
  input: string;
  operation: string;
  expected: string;
  expected_output: string | null;
  nudge: string;
  status: "running" | "finished";
  passed?: boolean;
  actual?: string;
  output?: string;
  observations?: Observation[];
};

export type WorkspaceFile = {
  name: string;
  content: string;
  hash: string;
  required: boolean;
};

export type Stage = {
  stage: StageName;
  label: string;
  instructions: string;
  guidance: string | null;
  hints: { revealed: string[]; total: number };
  reference_seen: boolean;
  entrypoint: string;
  run: string;
  files: WorkspaceFile[];
  untracked: { name: string; size: number }[];
  workspace: string;
  report: { cases: CheckCase[]; current: boolean } | null;
  passed: boolean;
  check_count: number;
  view: { active_file: string };
  flags: Flags;
  backup?: string;
};

export type Poll = {
  files: Record<string, string>;
  changed: Record<string, string>;
  untracked: { name: string; size: number }[];
  flags: Flags;
};

export type CheckOutcome = {
  passed: boolean;
  error: string;
  guidance: string;
  summary: string;
  cases: CheckCase[];
  flags: Flags;
};

export type CheckEvent =
  | { type: "case"; case: CheckCase }
  | ({ type: "done" } & CheckOutcome)
  | { type: "failed"; detail: string };

export type ConsoleSession = {
  id: string;
  key: string;
  title: string;
  number: number;
  alive: boolean;
  exit_code: number | null;
};

export type Milestone = {
  id: string;
  number: number;
  title: string;
  minutes: number;
  chapter_id: string;
  status: Status;
  optional: boolean;
  outcome: string;
  origin: string;
  supplied_base: boolean;
  started: boolean;
};

export type Checkpoint = {
  id: string;
  milestone: string;
  title: string;
  revision: number;
  created: string;
  supported: boolean;
  bytes: number;
  capabilities: string[];
};

export type Game = {
  title: string;
  description: string;
  progress: { core: Tally; optional: Tally };
  last_milestone: string | null;
  milestones: Milestone[];
  checkpoints: Checkpoint[];
};

export type ReviewChapter = {
  id: string;
  title: string;
  section_id: string;
  label: "Suggested" | "Available" | "Preview";
  passed: number;
  total: number;
  finished: boolean;
  started: boolean;
  due: string | null;
};

export type ReviewSessionInfo = {
  chapter: string;
  title: string;
  index: number;
  tasks: {
    title: string;
    kind: "predict" | "debug" | "code";
    passed: boolean;
  }[];
};

export type ReviewTask = {
  index: number;
  title: string;
  kind: "predict" | "debug" | "code";
  prompt: string;
  choices: string[];
  code: string;
  choice: number | null;
  passed: boolean;
  last: boolean;
};
