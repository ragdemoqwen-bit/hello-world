import { useEffect, useState } from "react";
import { BarChart3, DollarSign, FileCheck, FileX, Clock, TrendingUp } from "lucide-react";
import { api, type DashboardStats } from "../services/api";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"];

const STATUS_LABELS: Record<string, string> = {
  draft: "Draft",
  submitted: "Submitted",
  documents_pending: "Docs Pending",
  credit_check: "Credit Check",
  kyc_verification: "KYC",
  employment_verification: "Employment",
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

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboardStats().then(setStats).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!stats) return <div className="text-center text-gray-500 py-12">Failed to load dashboard data</div>;

  const statCards = [
    { label: "Total Applications", value: stats.total_applications, icon: BarChart3, color: "text-blue-600", bg: "bg-blue-50" },
    { label: "Total Requested", value: `$${(stats.total_requested_amount / 1000).toFixed(0)}K`, icon: DollarSign, color: "text-green-600", bg: "bg-green-50" },
    { label: "Approved", value: stats.approved_count, icon: FileCheck, color: "text-emerald-600", bg: "bg-emerald-50" },
    { label: "Denied", value: stats.denied_count, icon: FileX, color: "text-red-600", bg: "bg-red-50" },
    { label: "Pending", value: stats.pending_count, icon: Clock, color: "text-amber-600", bg: "bg-amber-50" },
    { label: "Approval Rate", value: `${stats.approval_rate}%`, icon: TrendingUp, color: "text-purple-600", bg: "bg-purple-50" },
  ];

  const statusData = Object.entries(stats.by_status).map(([key, value]) => ({
    name: STATUS_LABELS[key] || key,
    value,
  }));

  const typeData = Object.entries(stats.by_type).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    count: value,
  }));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {statCards.map((card) => (
          <div key={card.label} className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <div className={`${card.bg} p-2.5 rounded-lg`}>
                <card.icon className={`h-5 w-5 ${card.color}`} />
              </div>
              <div>
                <p className="text-sm text-gray-500">{card.label}</p>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {statusData.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Applications by Status</h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={statusData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                  {statusData.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {typeData.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Applications by Type</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={typeData}>
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
