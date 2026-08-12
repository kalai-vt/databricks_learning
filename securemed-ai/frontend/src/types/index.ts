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

export interface RetrievedDocument {
  title: string;
  score: number;
}

export interface ChatResponse {
  action: "ALLOW" | "BLOCK";
  risk_level: "LOW" | "CRITICAL";
  policy_code: string;
  policies_triggered: string[];
  message: string;
  llm_invoked: boolean;
  model: string;
  provider: string;
  mock_mode: boolean;
  tool_used: "SQL" | "RAG" | null;
  retrieved_documents: RetrievedDocument[];
  trace: TraceStep[];
  cross_tenant: { authenticated_tenant: string; requested_tenant: string } | null;
}

export interface ChatTurn {
  id: string;
  request: string;
  response: ChatResponse;
  timestamp: string;
}
