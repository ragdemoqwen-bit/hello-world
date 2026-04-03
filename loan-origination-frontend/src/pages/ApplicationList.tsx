import { useEffect, useState } from "react";
import { Plus, Search, Filter } from "lucide-react";
import { api, type ApplicationSummary } from "../services/api";

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
  draft: "Draft",
  submitted: "Submitted",
  documents_pending: "Docs Pending",
  credit_check: "Credit Check",
  kyc_verification: "KYC Verification",
  employment_verification: "Employment Verify",
  appraisal: "Appraisal",
  underwriting: "Underwriting",
  approved: "Approved",
  conditionally_approved: "Cond. Approved",
  denied: "Denied",
  loan_offered: "Offer Sent",
  offer_accepted: "Offer Accepted",
  closing: "Closing",
  funded: "Funded",
  withdrawn: "Withdrawn",
};

interface Props {
  onNewApplication: () => void;
  onSelectApplication: (id: string) => void;
}

export default function ApplicationList({ onNewApplication, onSelectApplication }: Props) {
  const [applications, setApplications] = useState<ApplicationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState("");
  const [filterType, setFilterType] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    setLoading(true);
    api.listApplications(filterStatus || undefined, filterType || undefined)
      .then(setApplications)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filterStatus, filterType]);

  const filtered = applications.filter((app) =>
    !searchTerm || app.borrower_name.toLowerCase().includes(searchTerm.toLowerCase()) || app.id.includes(searchTerm)
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h1 className="text-2xl font-bold text-gray-900">Loan Applications</h1>
        <button
          onClick={onNewApplication}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4" /> New Application
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="pl-10 pr-8 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
            >
              <option value="">All Statuses</option>
              {Object.entries(STATUS_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="">All Types</option>
            <option value="mortgage">Mortgage</option>
            <option value="auto">Auto</option>
            <option value="personal">Personal</option>
            <option value="business">Business</option>
            <option value="student">Student</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <p className="text-gray-500 mb-4">No applications found</p>
          <button onClick={onNewApplication} className="text-blue-600 hover:text-blue-700 text-sm font-medium">
            Create your first application
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Applicant</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((app) => (
                <tr
                  key={app.id}
                  onClick={() => onSelectApplication(app.id)}
                  className="border-b border-gray-100 hover:bg-blue-50 cursor-pointer transition-colors"
                >
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">{app.borrower_name}</div>
                    <div className="text-xs text-gray-400">{app.id.slice(0, 8)}...</div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 capitalize">{app.loan_type}</td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    ${app.requested_amount.toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[app.status] || "bg-gray-100 text-gray-700"}`}>
                      {STATUS_LABELS[app.status] || app.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {new Date(app.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
