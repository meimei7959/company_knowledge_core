export type WorkbenchChannel = "internal-dev" | "pilot" | "stable" | "rollback";

export type DesktopShellKind = "tauri-v2" | "electron" | "web";

export type WorkbenchSurface =
  | "home"
  | "runtime-monitor"
  | "requirement-center"
  | "project-console"
  | "agent-team-manager"
  | "agent-ring-console"
  | "result-center"
  | "review-center"
  | "quality-dashboard"
  | "notification-center"
  | "admin-governance"
  | "operations-feedback"
  | "knowledge-query"
  | "settings-security"
  | "recovery-center";

export type CollaborationDeviceReadModel = {
  displayName: string;
  ownerLabel: string;
  availabilityLabel: string;
  workTypeLabels: string[];
  authorizationSummary: string;
  currentTaskLabel: string;
  activeAgentLabels?: string[];
  toolLabels?: string[];
  executorLabel?: "Codex" | "Claude" | "本地模型" | "混合";
  modelUsageLabel?: string;
  tokenUsageLabel?: string;
  lastSeenLabel: string;
  riskLabels: string[];
  primaryAction: WorkbenchAction;
};

export type CollaborationRouteReadModel = {
  taskLabel: string;
  requirementLabel?: string;
  businessStatus: string;
  assignedDeviceLabel: string;
  activeAgentLabel?: string;
  executorLabel?: string;
  modelLabel?: string;
  tokenUsageLabel?: string;
  toolUsageLabel?: string;
  routeReason: string;
  blockerLabel: string;
  nextOwnerLabel: string;
  nextAction: string;
};

export type WorkbenchRegistrationEntry = {
  title: string;
  description: string;
  status: WorkbenchStatus | string;
  statusLabel: string;
  apiPath: string;
  confirmationLabel: string;
  primaryAction: WorkbenchAction;
  guardrailLabel: string;
  auditLabel: string;
};

export type CollaborationWorkbenchReadModel = {
  entryLabel: "项目与电脑接入";
  projectJoinPolicyLabel: string;
  readOnlyNotice?: string;
  availableDeviceCountLabel: string;
  activeRouteSummary: string;
  registrationEntries?: WorkbenchRegistrationEntry[];
  pairingRequests: Record<string, unknown>[];
  devices: CollaborationDeviceReadModel[];
  runners: Record<string, unknown>[];
  routeBoard: CollaborationRouteReadModel[];
  recoveryItems: Record<string, unknown>[];
  evidenceItems: Record<string, unknown>[];
  auditSummaries: Record<string, unknown>[];
  technicalDetails: Record<string, unknown>[];
};

export type WorkbenchStatus =
  | "ready"
  | "waiting_review"
  | "blocked"
  | "running"
  | "degraded"
  | "offline"
  | "stale"
  | "failed"
  | "needs_permission"
  | "safe_fallback";

export type WorkbenchEnvironment = {
  channel: WorkbenchChannel;
  apiBaseUrl: string;
  apiCompatibilityVersion: string;
  frontendAssetHash: string;
  bridgeVersion: string;
};

export type BridgePermission =
  | "file.pick.reference"
  | "notification.permission.request"
  | "notification.show"
  | "deeplink.resolve"
  | "settings.read"
  | "settings.write"
  | "credential.reference.store"
  | "runner.pairing.diagnostics"
  | "runner.pairing.handoff"
  | "diagnostics.redacted.collect";

export type NativeBridgeCommand =
  | "selectSourceFileReference"
  | "requestNotificationPermission"
  | "showNotification"
  | "resolveDeepLink"
  | "readLocalSetting"
  | "writeLocalSetting"
  | "storeCredentialReference"
  | "getRunnerPairingDiagnostics"
  | "handoffRunnerPairingProof"
  | "collectRedactedDiagnostics";

export type BridgeRequest<Payload = unknown> = {
  command: NativeBridgeCommand;
  permission: BridgePermission;
  payload: Payload;
  idempotencyKey: string;
};

export type BridgeSuccess<Value = unknown> = {
  ok: true;
  value: Value;
  auditEvent?: {
    action: string;
    targetRef: string;
  };
};

export type BridgeFailure = {
  ok: false;
  errorCode:
    | "permission_denied"
    | "unsupported_shell"
    | "unavailable"
    | "external_proof_blocked"
    | "central_api_required"
    | "redacted_diagnostics_only";
  displayMessage: string;
  retryable: boolean;
};

export type BridgeResult<Value = unknown> = BridgeSuccess<Value> | BridgeFailure;

export type NativeBridgePort = {
  shell: DesktopShellKind;
  invoke<Value = unknown, Payload = unknown>(request: BridgeRequest<Payload>): Promise<BridgeResult<Value>>;
};

export type WorkbenchShellAdapter = {
  environment: WorkbenchEnvironment;
  bridge: NativeBridgePort;
};

export type SourceFileReference = {
  fileName: string;
  mediaType: string;
  byteSize: number;
  sourceRef: string;
};

export type RunnerPairingProof = {
  runnerId: string;
  pairingProofRef: string;
  expiresAt: string;
  issuedBy: "central-api";
};

export type RunnerPairingHandoff = {
  runnerId: string;
  pairingProofRef: string;
  userConfirmed: boolean;
};

export type RunnerPairingDiagnostics = {
  runnerDetected: boolean;
  runnerId?: string;
  heartbeatStatus?: "online" | "degraded" | "offline";
  centralApiPairingRequired: true;
};

export type DisplayObjectRef = {
  label: string;
  objectType: string;
  objectRef: string;
  technicalRef?: string;
};

export type WorkbenchAction = {
  id: string;
  label: string;
  permission: string;
  idempotencyKey: string;
  serverGate: "required";
  auditRef?: string;
  displayMessage?: string;
  auditSummary?: string;
  disabledReason?: string;
};

export type WorkbenchPanelState = {
  id: string;
  title: string;
  status: WorkbenchStatus;
  owner: string;
  nextAction: string;
  evidenceRefs: DisplayObjectRef[];
  fallbackState: string;
};

export type RunnerLeaseState = {
  runner: DisplayObjectRef;
  lease: DisplayObjectRef;
  status: "active" | "completed" | "failed" | "stale" | "cancelled" | "retried" | "escalated";
  heartbeat: "online" | "degraded" | "offline";
  nextAction: string;
  scopeAudit: WorkbenchPanelState;
};

export type PMControlLeaseState = {
  primaryPm: DisplayObjectRef;
  lease: DisplayObjectRef;
  project: DisplayObjectRef;
  status: "healthy" | "expiring" | "stale" | "expired" | "released" | "taken_over" | "missing";
  heartbeat: "online" | "degraded" | "offline";
  expiresAt: string;
  lastHeartbeatAt: string;
  leaseGenerationLabel?: string;
  fencingTokenLabel?: string;
  nextAction: string;
  takeoverAction?: WorkbenchAction;
  releaseAction?: WorkbenchAction;
  auditRefs: DisplayObjectRef[];
};

export type ProjectPMParticipantState = {
  pm: DisplayObjectRef;
  role: "primary" | "collaborator" | "standby";
  status: WorkbenchStatus;
  runner?: DisplayObjectRef;
  device?: DisplayObjectRef;
  standbyPriority?: number;
  capabilities: string[];
  nextAction: string;
};

export type PMControlTakeoverRecordState = {
  recordRef: string;
  occurredAt: string;
  fromPm: DisplayObjectRef;
  toPm: DisplayObjectRef;
  operator: string;
  reason: string;
  previousLeaseStatus: string;
  newLeaseIdLabel: string;
  auditRef: DisplayObjectRef;
};

export type PMControlDenialSummaryState = {
  auditRef: string;
  timestamp: string;
  requestPm: DisplayObjectRef;
  action: string;
  reasonCode: string;
  displayMessage: string;
  nextAction: string;
};

export type PMControlWorkbenchReadModel = {
  currentLease: PMControlLeaseState;
  participants: ProjectPMParticipantState[];
  takeoverRecords: PMControlTakeoverRecordState[];
  denialSummaries: PMControlDenialSummaryState[];
  healthExplanation: WorkbenchPanelState;
};

export type DesktopWorkbenchReadModel = {
  schemaVersion: "desktop-workbench-read-model.v1";
  sourceOfTruth: "central-api-read-model";
  runtimeReadModelKind?: "real-v1-runtime-read-model";
  fixture?: boolean;
  projectId?: string;
  generatedAt: string;
  staleStatePolicy: "show-safe-fallback-not-current";
  surfaces: WorkbenchSurface[];
  home: WorkbenchPanelState[];
  projectProgress: WorkbenchPanelState[];
  agentCurrentWork: WorkbenchPanelState[];
  runnerLeases: RunnerLeaseState[];
  approvals: WorkbenchPanelState[];
  notifications: WorkbenchPanelState[];
  recovery: WorkbenchPanelState[];
  settingsSecurity: WorkbenchPanelState[];
  permissionGatedActions: WorkbenchAction[];
  runtimeMetrics?: Record<string, string | number | boolean>;
  devices?: Record<string, unknown>[];
  agentSessions?: Record<string, unknown>[];
  agentMessages?: Record<string, unknown>[];
  taskPackages?: Record<string, unknown>[];
  worktrees?: Record<string, unknown>[];
  taskFlow?: Record<string, unknown>[];
  taskResults?: Record<string, unknown>[];
  acceptanceEvidence?: WorkbenchPanelState[];
  collaborationWorkbench?: CollaborationWorkbenchReadModel;
  pmControl?: PMControlWorkbenchReadModel;
};

export const forbiddenLocalRunnerMutations = [
  "claimTaskLease",
  "mutateTaskLease",
  "writeTaskResult",
  "writeAgentRun",
  "executeUnregisteredTool",
  "storeRawCredential",
] as const;

export function createWorkbenchFoundation(adapter: WorkbenchShellAdapter) {
  return {
    environment: adapter.environment,
    shell: adapter.bridge.shell,
    selectSourceFileReference(payload: { projectId: string; sensitivityHint?: string }) {
      return adapter.bridge.invoke<SourceFileReference>({
        command: "selectSourceFileReference",
        permission: "file.pick.reference",
        payload,
        idempotencyKey: `file-reference:${payload.projectId}`,
      });
    },
    requestNotificationPermission(reason: string) {
      return adapter.bridge.invoke<{ granted: boolean }>({
        command: "requestNotificationPermission",
        permission: "notification.permission.request",
        payload: { reason },
        idempotencyKey: `notification-permission:${reason}`,
      });
    },
    getRunnerPairingDiagnostics() {
      return adapter.bridge.invoke<RunnerPairingDiagnostics>({
        command: "getRunnerPairingDiagnostics",
        permission: "runner.pairing.diagnostics",
        payload: { centralApiPairingRequired: true },
        idempotencyKey: "runner-pairing-diagnostics",
      });
    },
    handoffRunnerPairingProof(payload: RunnerPairingHandoff) {
      return adapter.bridge.invoke<{ accepted: boolean }>({
        command: "handoffRunnerPairingProof",
        permission: "runner.pairing.handoff",
        payload,
        idempotencyKey: `runner-pairing:${payload.runnerId}:${payload.pairingProofRef}`,
      });
    },
    assertCentralReadModel(readModel: DesktopWorkbenchReadModel) {
      return readModel.sourceOfTruth === "central-api-read-model" &&
        readModel.staleStatePolicy === "show-safe-fallback-not-current";
    },
  };
}
