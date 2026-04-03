import { useState } from "react";
import { LayoutDashboard, FileText, Landmark } from "lucide-react";
import Dashboard from "./pages/Dashboard";
import ApplicationList from "./pages/ApplicationList";
import ApplicationForm from "./pages/ApplicationForm";
import ApplicationDetail from "./pages/ApplicationDetail";

type Page = "dashboard" | "applications" | "new-application" | "application-detail";

function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [selectedAppId, setSelectedAppId] = useState<string>("");

  const navItems = [
    { key: "dashboard" as Page, label: "Dashboard", icon: LayoutDashboard },
    { key: "applications" as Page, label: "Applications", icon: FileText },
  ];

  const handleSelectApplication = (id: string) => {
    setSelectedAppId(id);
    setPage("application-detail");
  };

  const handleApplicationCreated = (id: string) => {
    setSelectedAppId(id);
    setPage("application-detail");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => setPage("dashboard")}>
              <div className="bg-blue-600 p-1.5 rounded-lg">
                <Landmark className="h-5 w-5 text-white" />
              </div>
              <span className="text-lg font-bold text-gray-900">LoanOS</span>
              <span className="text-xs text-gray-400 hidden sm:inline ml-1">Loan Origination System</span>
            </div>
            <nav className="flex items-center gap-1">
              {navItems.map((item) => (
                <button
                  key={item.key}
                  onClick={() => setPage(item.key)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    page === item.key || (item.key === "applications" && (page === "new-application" || page === "application-detail"))
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  <item.icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{item.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {page === "dashboard" && <Dashboard />}
        {page === "applications" && (
          <ApplicationList
            onNewApplication={() => setPage("new-application")}
            onSelectApplication={handleSelectApplication}
          />
        )}
        {page === "new-application" && (
          <ApplicationForm
            onBack={() => setPage("applications")}
            onCreated={handleApplicationCreated}
          />
        )}
        {page === "application-detail" && selectedAppId && (
          <ApplicationDetail
            applicationId={selectedAppId}
            onBack={() => setPage("applications")}
          />
        )}
      </main>
    </div>
  );
}

export default App;
