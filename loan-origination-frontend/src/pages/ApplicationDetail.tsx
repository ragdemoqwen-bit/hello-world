import { useEffect, useState, useCallback } from "react";
import {
  ArrowLeft, CreditCard, Shield, Briefcase, Home, FileSignature,
  CheckCircle2, XCircle, AlertTriangle, Clock, DollarSign, TrendingUp,
  ChevronRight, Banknote,
} from "lucide-react";
import { api, type FullApplicationDetails } from "../services/api";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  submitted: "bg-blue-100 text-blue-700",
  documents_pending: "bg-yellow-100 text-yellow-700",
  credit_check: "bg-purple-100 text-purple-700",
  kyc_verification: "bg-indigo-100 text-indigo-700",
  employment_verification: "bg-cyan-100 text-cyan-700",
  appraisal: "bg-teal-100 text-teal-700",
  underwriting: "bg-orange-100 text-orange-700",
  approved: "bg-green-100 text-green-700",
  conditionally_approved: "bg-emerald-100 text-emerald-700",
  denied: "bg-red-100 text-red-700",
  loan_offered: "bg-blue-100 text-blue-700",
  offer_accepted: "bg-green-100 text-green-700",
  closing: "bg-amber-100 text-amber-700",
  funded: "bg-green-200 text-green-800",
  withdrawn: "bg-gray-200 text-gray-600",
};

const STATUS_LABELS: Record<string, string> = {
  draft: "Draft", submitted: "Submitted", documents_pending: "Docs Pending",
  credit_check: "Credit Check", kyc_verification: "KYC Verification",
  employment_verification: "Employment Verify", appraisal: "Appraisal",
  underwriting: "Underwriting", approved: "Approved",
  conditionally_approved: "Conditionally Approved", denied: "Denied",
  loan_offered: "Offer Sent", offer_accepted: "Offer Accepted",
  closing: "Closing", funded: "Funded", withdrawn: "Withdrawn",
};

const DECISION_ICONS: Record<string, typeof CheckCircle2> = {
  approved: CheckCircle2,
  conditionally_approved: AlertTriangle,
  denied: XCircle,
  manual_review: Clock,
};

const DECISION_COLORS: Record<string, string> = {
  approved: "text-green-600",
  conditionally_approved: "text-amber-600",
  denied: "text-red-600",
  manual_review: "text-orange-600",
};

interface Props {
  applicationId: string;
  onBack: () => void;
}

export default function ApplicationDetail({ applicationId, onBack }: Props) {
  const [details, setDetails] = useState<FullApplicationDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [actionResult, setActionResult] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const loadDetails = useCallback(() => {
    setLoading(true);
    api.getFullDetails(applicationId)
      .then(setDetails)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [applicationId]);

  useEffect(() => { loadDetails(); }, [loadDetails]);

  const runAction = async (action: string, fn: () => Promise<unknown>) => {
    setActionLoading(action);
    setActionResult(null);
    try {
      const result = await fn();
      const msg = typeof result === "object" && result !== null && "message" in result
        ? String((result as Record<string, unknown>).message)
        : `${action} completed successfully`;
      setActionResult({ type: "success", message: msg });
      loadDetails();
    } catch (err) {
      setActionResult({ type: "error", message: err instanceof Error ? err.message : "Action failed" });
    } finally {
      setActionLoading("");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!details) return <div className="text-center text-gray-500 py-12">Application not found</div>;

  const { application: app, borrower, credit_report, underwriting, loan_offer, status_history } = details;
  const status = app.status;

  const workflowSteps = [
    { key: "credit_check", label: "Credit Check", icon: CreditCard, action: () => api.runCreditCheck(applicationId), done: !!credit_report },
    { key: "kyc", label: "KYC Verification", icon: Shield, action: () => api.runKYC(applicationId), done: status_history.some(h => h.new_status === "kyc_verification") },
    { key: "employment", label: "Employment Verify", icon: Briefcase, action: () => api.runEmploymentVerification(applicationId), done: status_history.some(h => h.new_status === "employment_verification") },
    ...(app.loan_type === "mortgage" ? [{ key: "appraisal", label: "Property Appraisal", icon: Home, action: () => api.runPropertyAppraisal(applicationId), done: status_history.some(h => h.new_status === "appraisal") }] : []),
    { key: "underwrite", label: "Underwriting", icon: TrendingUp, action: () => api.runUnderwriting(applicationId), done: !!underwriting },
    { key: "offer", label: "Generate Offer", icon: DollarSign, action: () => api.generateOffer(applicationId), done: !!loan_offer },
  ];

  const canAcceptOffer = loan_offer && loan_offer.status === "sent";
  const canFund = status === "closing";

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <button onClick={onBack} className="flex items-center gap-1 text-sm text-gray-600 hover:text-blue-600">
        <ArrowLeft className="h-4 w-4" /> Back to Applications
      </button>

      {/* Header */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-gray-900">{borrower.name}</h1>
            <p className="text-sm text-gray-500">{borrower.email} | {borrower.phone}</p>
            <p className="text-xs text-gray-400 mt-1">ID: {app.id}</p>
          </div>
          <div className="text-right">
            <span className={`inline-block px-3 py-1.5 rounded-full text-sm font-medium ${STATUS_COLORS[status] || "bg-gray-100"}`}>
              {STATUS_LABELS[status] || status}
            </span>
            <p className="text-2xl font-bold text-gray-900 mt-1">${app.requested_amount.toLocaleString()}</p>
            <p className="text-sm text-gray-500 capitalize">{app.loan_type} | {app.loan_term_months} months</p>
          </div>
        </div>
      </div>

      {/* Action Result */}
      {actionResult && (
        <div className={`rounded-lg p-3 text-sm ${actionResult.type === "success" ? "bg-green-50 border border-green-200 text-green-700" : "bg-red-50 border border-red-200 text-red-700"}`}>
          {actionResult.message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Workflow Actions */}
        <div className="lg:col-span-2 space-y-6">
          {/* Origination Workflow */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Origination Workflow</h3>
            <div className="space-y-3">
              {workflowSteps.map((step, idx) => (
                <div key={step.key} className="flex items-center gap-3">
                  <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${step.done ? "bg-green-100" : "bg-gray-100"}`}>
                    {step.done ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : (
                      <step.icon className="h-4 w-4 text-gray-500" />
                    )}
                  </div>
                  <div className="flex-1">
                    <span className={`text-sm font-medium ${step.done ? "text-green-700" : "text-gray-700"}`}>
                      {step.label}
                    </span>
                  </div>
                  {!step.done && !["denied", "withdrawn", "funded"].includes(status) && (
                    <button
                      onClick={() => runAction(step.key, step.action)}
                      disabled={!!actionLoading}
                      className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                      {actionLoading === step.key ? (
                        <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white" />
                      ) : (
                        <>Run <ChevronRight className="h-3 w-3" /></>
                      )}
                    </button>
                  )}
                  {idx < workflowSteps.length - 1 && (
                    <div className="hidden" /> 
                  )}
                </div>
              ))}

              {/* Accept/Decline Offer */}
              {canAcceptOffer && (
                <div className="flex items-center gap-3 pt-3 border-t border-gray-200">
                  <div className="flex-shrink-0 h-8 w-8 rounded-full bg-amber-100 flex items-center justify-center">
                    <FileSignature className="h-4 w-4 text-amber-600" />
                  </div>
                  <span className="flex-1 text-sm font-medium text-gray-700">Accept/Decline Offer</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => runAction("accept", () => api.acceptOffer(applicationId, true))}
                      disabled={!!actionLoading}
                      className="px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      {actionLoading === "accept" ? "..." : "Accept"}
                    </button>
                    <button
                      onClick={() => runAction("decline", () => api.acceptOffer(applicationId, false))}
                      disabled={!!actionLoading}
                      className="px-3 py-1.5 bg-red-600 text-white text-xs font-medium rounded-lg hover:bg-red-700 disabled:opacity-50"
                    >
                      Decline
                    </button>
                  </div>
                </div>
              )}

              {/* Fund Loan */}
              {canFund && (
                <div className="flex items-center gap-3 pt-3 border-t border-gray-200">
                  <div className="flex-shrink-0 h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                    <Banknote className="h-4 w-4 text-green-600" />
                  </div>
                  <span className="flex-1 text-sm font-medium text-gray-700">Fund Loan</span>
                  <button
                    onClick={() => runAction("fund", () => api.fundLoan(applicationId))}
                    disabled={!!actionLoading}
                    className="px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded-lg hover:bg-green-700 disabled:opacity-50"
                  >
                    {actionLoading === "fund" ? "..." : "Fund"}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Credit Report */}
          {credit_report && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Credit Report</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <p className="text-3xl font-bold text-blue-700">{credit_report.credit_score}</p>
                  <p className="text-xs text-gray-500">Credit Score</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-lg font-bold text-gray-700">{credit_report.total_accounts}</p>
                  <p className="text-xs text-gray-500">Total Accounts</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-lg font-bold text-gray-700">{credit_report.delinquent_accounts}</p>
                  <p className="text-xs text-gray-500">Delinquent</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-lg font-bold text-gray-700">{credit_report.bankruptcies}</p>
                  <p className="text-xs text-gray-500">Bankruptcies</p>
                </div>
              </div>
              <p className="text-xs text-gray-400 mt-3">Bureau: {credit_report.bureau} | Pulled: {new Date(credit_report.pulled_at).toLocaleDateString()}</p>
            </div>
          )}

          {/* Underwriting Result */}
          {underwriting && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Underwriting Decision</h3>
              <div className="flex items-center gap-3 mb-4">
                {(() => {
                  const Icon = DECISION_ICONS[underwriting.decision] || Clock;
                  const color = DECISION_COLORS[underwriting.decision] || "text-gray-600";
                  return (
                    <>
                      <Icon className={`h-8 w-8 ${color}`} />
                      <div>
                        <p className={`text-lg font-bold capitalize ${color}`}>
                          {underwriting.decision.replace(/_/g, " ")}
                        </p>
                        <p className="text-sm text-gray-500">Risk Level: <span className="capitalize font-medium">{underwriting.risk_level}</span></p>
                      </div>
                    </>
                  );
                })()}
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
                <div className="p-3 bg-gray-50 rounded-lg text-center">
                  <p className="text-lg font-bold text-gray-700">{(underwriting.dti_ratio * 100).toFixed(1)}%</p>
                  <p className="text-xs text-gray-500">DTI Ratio</p>
                </div>
                {underwriting.ltv_ratio != null && (
                  <div className="p-3 bg-gray-50 rounded-lg text-center">
                    <p className="text-lg font-bold text-gray-700">{(underwriting.ltv_ratio * 100).toFixed(1)}%</p>
                    <p className="text-xs text-gray-500">LTV Ratio</p>
                  </div>
                )}
                <div className="p-3 bg-gray-50 rounded-lg text-center">
                  <p className="text-lg font-bold text-gray-700">{underwriting.risk_score}</p>
                  <p className="text-xs text-gray-500">Risk Score</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg text-center">
                  <p className="text-lg font-bold text-gray-700">{underwriting.credit_score}</p>
                  <p className="text-xs text-gray-500">Credit Score</p>
                </div>
              </div>
              {underwriting.conditions.length > 0 && (
                <div className="mb-3">
                  <p className="text-sm font-medium text-amber-700 mb-1">Conditions:</p>
                  <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                    {underwriting.conditions.map((c, i) => <li key={i}>{c}</li>)}
                  </ul>
                </div>
              )}
              {underwriting.denial_reasons.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-red-700 mb-1">Denial Reasons:</p>
                  <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                    {underwriting.denial_reasons.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              )}
              {underwriting.notes && <p className="text-sm text-gray-500 mt-2 italic">{underwriting.notes}</p>}
            </div>
          )}

          {/* Loan Offer */}
          {loan_offer && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Loan Offer</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                <div className="p-3 bg-green-50 rounded-lg text-center">
                  <p className="text-xl font-bold text-green-700">${loan_offer.approved_amount.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">Approved Amount</p>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg text-center">
                  <p className="text-xl font-bold text-blue-700">{(loan_offer.interest_rate * 100).toFixed(2)}%</p>
                  <p className="text-xs text-gray-500">Interest Rate</p>
                </div>
                <div className="p-3 bg-purple-50 rounded-lg text-center">
                  <p className="text-xl font-bold text-purple-700">${loan_offer.monthly_payment.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">Monthly Payment</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg text-center">
                  <p className="text-lg font-bold text-gray-700">{(loan_offer.apr * 100).toFixed(2)}%</p>
                  <p className="text-xs text-gray-500">APR</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg text-center">
                  <p className="text-lg font-bold text-gray-700">${loan_offer.total_interest.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">Total Interest</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg text-center">
                  <p className="text-lg font-bold text-gray-700">${loan_offer.origination_fee.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">Origination Fee</p>
                </div>
              </div>
              <div className="flex items-center justify-between mt-4 text-sm text-gray-500">
                <span>Term: {loan_offer.loan_term_months} months</span>
                <span>Total Cost: ${loan_offer.total_cost.toLocaleString()}</span>
                <span className={`font-medium ${loan_offer.status === "accepted" ? "text-green-600" : loan_offer.status === "declined" ? "text-red-600" : "text-blue-600"}`}>
                  Status: {loan_offer.status}
                </span>
              </div>
              {loan_offer.expires_at && (
                <p className="text-xs text-gray-400 mt-2">Expires: {new Date(loan_offer.expires_at).toLocaleDateString()}</p>
              )}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Borrower Info */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Borrower Details</h3>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Income</dt>
                <dd className="font-medium">${borrower.annual_income.toLocaleString()}/yr</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Monthly Debt</dt>
                <dd className="font-medium">${borrower.monthly_debt_payments.toLocaleString()}</dd>
              </div>
              {borrower.employer_name && (
                <div className="flex justify-between">
                  <dt className="text-gray-500">Employer</dt>
                  <dd className="font-medium">{borrower.employer_name}</dd>
                </div>
              )}
              {borrower.job_title && (
                <div className="flex justify-between">
                  <dt className="text-gray-500">Title</dt>
                  <dd className="font-medium">{borrower.job_title}</dd>
                </div>
              )}
            </dl>
          </div>

          {/* Loan Details */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Loan Details</h3>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Type</dt>
                <dd className="font-medium capitalize">{app.loan_type}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Purpose</dt>
                <dd className="font-medium">{app.loan_purpose}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Term</dt>
                <dd className="font-medium">{app.loan_term_months} months</dd>
              </div>
              {app.property_address && (
                <div className="flex justify-between">
                  <dt className="text-gray-500">Property</dt>
                  <dd className="font-medium text-right text-xs">{app.property_address}</dd>
                </div>
              )}
              {app.property_value && (
                <div className="flex justify-between">
                  <dt className="text-gray-500">Property Value</dt>
                  <dd className="font-medium">${app.property_value.toLocaleString()}</dd>
                </div>
              )}
            </dl>
          </div>

          {/* Status Timeline */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Status History</h3>
            <div className="space-y-3">
              {status_history.map((entry, i) => (
                <div key={i} className="flex gap-3">
                  <div className="flex flex-col items-center">
                    <div className="h-2 w-2 rounded-full bg-blue-500 mt-1.5" />
                    {i < status_history.length - 1 && <div className="w-px flex-1 bg-gray-200 mt-1" />}
                  </div>
                  <div className="pb-3">
                    <p className="text-sm font-medium text-gray-900">
                      {STATUS_LABELS[entry.new_status] || entry.new_status}
                    </p>
                    {entry.notes && <p className="text-xs text-gray-500 mt-0.5">{entry.notes}</p>}
                    <p className="text-xs text-gray-400 mt-0.5">
                      {new Date(entry.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
