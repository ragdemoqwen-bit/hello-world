const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export interface Borrower {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  date_of_birth: string;
  ssn_last_four: string;
  address_street: string;
  address_city: string;
  address_state: string;
  address_zip: string;
  employer_name?: string;
  job_title?: string;
  employment_years?: number;
  annual_income: number;
  monthly_debt_payments: number;
}

export interface ApplicationCreate {
  borrower: Borrower;
  loan_type: string;
  requested_amount: number;
  loan_purpose: string;
  loan_term_months: number;
  property_address?: string;
  property_value?: number;
  vehicle_info?: string;
}

export interface ApplicationSummary {
  id: string;
  borrower_name: string;
  loan_type: string;
  requested_amount: number;
  status: string;
  created_at: string;
}

export interface ApplicationResponse {
  id: string;
  borrower_id: string;
  loan_type: string;
  requested_amount: number;
  loan_purpose: string;
  loan_term_months: number;
  property_address?: string;
  property_value?: number;
  vehicle_info?: string;
  status: string;
  created_at: string;
  updated_at: string;
  borrower?: Borrower & { id: string; created_at: string; updated_at: string };
}

export interface CreditReport {
  id: string;
  application_id: string;
  bureau: string;
  credit_score: number;
  total_accounts?: number;
  open_accounts?: number;
  delinquent_accounts?: number;
  total_balance?: number;
  monthly_payments?: number;
  bankruptcies: number;
  collections: number;
  hard_inquiries_last_12m: number;
  pulled_at: string;
}

export interface UnderwritingResult {
  id: string;
  application_id: string;
  credit_score: number;
  dti_ratio: number;
  ltv_ratio?: number;
  risk_score: number;
  risk_level: string;
  decision: string;
  conditions?: string;
  denial_reasons?: string;
  notes?: string;
  decided_at: string;
}

export interface LoanOffer {
  id: string;
  application_id: string;
  approved_amount: number;
  interest_rate: number;
  loan_term_months: number;
  monthly_payment: number;
  apr: number;
  origination_fee: number;
  total_interest: number;
  total_cost: number;
  requires_collateral: boolean;
  status: string;
  expires_at?: string;
  created_at: string;
  accepted_at?: string;
}

export interface StatusHistoryEntry {
  previous_status?: string;
  new_status: string;
  changed_by: string;
  notes?: string;
  created_at: string;
}

export interface FullApplicationDetails {
  application: {
    id: string;
    loan_type: string;
    requested_amount: number;
    loan_purpose: string;
    loan_term_months: number;
    property_address?: string;
    property_value?: number;
    vehicle_info?: string;
    status: string;
    created_at: string;
    updated_at: string;
  };
  borrower: {
    id: string;
    name: string;
    email: string;
    phone: string;
    annual_income: number;
    monthly_debt_payments: number;
    employer_name?: string;
    job_title?: string;
  };
  credit_report?: {
    bureau: string;
    credit_score: number;
    total_accounts?: number;
    open_accounts?: number;
    delinquent_accounts?: number;
    total_balance?: number;
    monthly_payments?: number;
    bankruptcies: number;
    collections: number;
    pulled_at: string;
  };
  underwriting?: {
    credit_score: number;
    dti_ratio: number;
    ltv_ratio?: number;
    risk_score: number;
    risk_level: string;
    decision: string;
    conditions: string[];
    denial_reasons: string[];
    notes?: string;
    decided_at: string;
  };
  loan_offer?: {
    approved_amount: number;
    interest_rate: number;
    loan_term_months: number;
    monthly_payment: number;
    apr: number;
    origination_fee: number;
    total_interest: number;
    total_cost: number;
    requires_collateral: boolean;
    status: string;
    expires_at?: string;
    created_at: string;
  };
  status_history: StatusHistoryEntry[];
}

export interface DashboardStats {
  total_applications: number;
  total_requested_amount: number;
  total_funded_amount: number;
  approved_count: number;
  denied_count: number;
  pending_count: number;
  approval_rate: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
}

// --- API Functions ---

export const api = {
  createApplication: (data: ApplicationCreate) =>
    request<ApplicationResponse>("/api/applications", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  listApplications: (status?: string, loanType?: string) => {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    if (loanType) params.set("loan_type", loanType);
    const qs = params.toString();
    return request<ApplicationSummary[]>(`/api/applications${qs ? `?${qs}` : ""}`);
  },

  getApplication: (id: string) =>
    request<ApplicationResponse>(`/api/applications/${id}`),

  getFullDetails: (id: string) =>
    request<FullApplicationDetails>(`/api/applications/${id}/full-details`),

  runCreditCheck: (id: string) =>
    request<CreditReport>(`/api/applications/${id}/credit-check`, { method: "POST" }),

  runKYC: (id: string) =>
    request<Record<string, unknown>>(`/api/applications/${id}/kyc-verification`, { method: "POST" }),

  runEmploymentVerification: (id: string) =>
    request<Record<string, unknown>>(`/api/applications/${id}/employment-verification`, { method: "POST" }),

  runPropertyAppraisal: (id: string) =>
    request<Record<string, unknown>>(`/api/applications/${id}/property-appraisal`, { method: "POST" }),

  runUnderwriting: (id: string) =>
    request<UnderwritingResult>(`/api/applications/${id}/underwrite`, { method: "POST" }),

  generateOffer: (id: string) =>
    request<LoanOffer>(`/api/applications/${id}/generate-offer`, { method: "POST" }),

  acceptOffer: (id: string, accepted: boolean) =>
    request<Record<string, unknown>>(`/api/applications/${id}/accept-offer`, {
      method: "POST",
      body: JSON.stringify({ accepted }),
    }),

  fundLoan: (id: string) =>
    request<Record<string, unknown>>(`/api/applications/${id}/fund`, { method: "POST" }),

  getStatusHistory: (id: string) =>
    request<StatusHistoryEntry[]>(`/api/applications/${id}/status-history`),

  getDashboardStats: () =>
    request<DashboardStats>("/api/dashboard/stats"),

  getRequiredDocuments: (id: string) =>
    request<Array<{ type: string; label: string; uploaded: boolean; status: string }>>(`/api/documents/${id}/required`),
};
