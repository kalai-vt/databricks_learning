export interface AuthUser {
  id: number;
  name: string;
  email: string;
  role: "SUPER_ADMIN" | "HOSPITAL_ADMIN" | "DOCTOR";
  tenant_code: string | null;
  tenant_name: string | null;
}

export interface TraceStep {
  step: number;
  label: string;
  status: string;
  detail: string;
}

export interface ChatResponse {
  action: "ALLOW" | "BLOCK" | "MASK" | "HUMAN_REVIEW";
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  policy_code: string;
  policies_triggered: string[];
  message: string;
  llm_invoked: boolean;
  model: string;
  provider: string;
  mock_mode: boolean;
  trace: TraceStep[];
  pii_detected: { field: string; patient: string; masked: string }[];
  cross_tenant: { authenticated_tenant: string; requested_tenant: string } | null;
}

export interface ChatTurn {
  id: string;
  request: string;
  response: ChatResponse;
  timestamp: string;
}
