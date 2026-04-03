import { useState } from "react";
import { ArrowLeft, Send } from "lucide-react";
import { api, type ApplicationCreate } from "../services/api";

const LOAN_TYPES = [
  { value: "mortgage", label: "Mortgage" },
  { value: "auto", label: "Auto Loan" },
  { value: "personal", label: "Personal Loan" },
  { value: "business", label: "Business Loan" },
  { value: "student", label: "Student Loan" },
];

const US_STATES = [
  "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
  "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
  "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
  "VA","WA","WV","WI","WY",
];

interface Props {
  onBack: () => void;
  onCreated: (id: string) => void;
}

export default function ApplicationForm({ onBack, onCreated }: Props) {
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [loanType, setLoanType] = useState("personal");
  const [requestedAmount, setRequestedAmount] = useState("");
  const [loanPurpose, setLoanPurpose] = useState("");
  const [loanTermMonths, setLoanTermMonths] = useState("60");
  const [propertyAddress, setPropertyAddress] = useState("");
  const [propertyValue, setPropertyValue] = useState("");
  const [vehicleInfo, setVehicleInfo] = useState("");

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [dob, setDob] = useState("");
  const [ssnLastFour, setSsnLastFour] = useState("");
  const [street, setStreet] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("IL");
  const [zip, setZip] = useState("");

  const [employerName, setEmployerName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [employmentYears, setEmploymentYears] = useState("");
  const [annualIncome, setAnnualIncome] = useState("");
  const [monthlyDebt, setMonthlyDebt] = useState("0");

  const handleSubmit = async () => {
    setSubmitting(true);
    setError("");
    try {
      const data: ApplicationCreate = {
        borrower: {
          first_name: firstName,
          last_name: lastName,
          email,
          phone,
          date_of_birth: dob,
          ssn_last_four: ssnLastFour,
          address_street: street,
          address_city: city,
          address_state: state,
          address_zip: zip,
          employer_name: employerName || undefined,
          job_title: jobTitle || undefined,
          employment_years: employmentYears ? parseFloat(employmentYears) : undefined,
          annual_income: parseFloat(annualIncome),
          monthly_debt_payments: parseFloat(monthlyDebt) || 0,
        },
        loan_type: loanType,
        requested_amount: parseFloat(requestedAmount),
        loan_purpose: loanPurpose,
        loan_term_months: parseInt(loanTermMonths),
        property_address: propertyAddress || undefined,
        property_value: propertyValue ? parseFloat(propertyValue) : undefined,
        vehicle_info: vehicleInfo || undefined,
      };
      const result = await api.createApplication(data);
      onCreated(result.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit application");
    } finally {
      setSubmitting(false);
    }
  };

  const inputClass = "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";

  return (
    <div className="max-w-3xl mx-auto">
      <button onClick={onBack} className="flex items-center gap-1 text-sm text-gray-600 hover:text-blue-600 mb-4">
        <ArrowLeft className="h-4 w-4" /> Back to Applications
      </button>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
        <div className="border-b border-gray-200 px-6 py-4">
          <h2 className="text-xl font-bold text-gray-900">New Loan Application</h2>
          <div className="flex gap-2 mt-3">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center gap-2">
                <div className={`h-8 w-8 rounded-full flex items-center justify-center text-sm font-medium ${step >= s ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-500"}`}>
                  {s}
                </div>
                <span className="text-sm text-gray-600 hidden sm:inline">
                  {s === 1 ? "Loan Details" : s === 2 ? "Personal Info" : "Employment & Income"}
                </span>
                {s < 3 && <div className="w-8 h-px bg-gray-300 hidden sm:block" />}
              </div>
            ))}
          </div>
        </div>

        <div className="p-6">
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <label className={labelClass}>Loan Type *</label>
                <select value={loanType} onChange={(e) => setLoanType(e.target.value)} className={inputClass}>
                  {LOAN_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Requested Amount ($) *</label>
                  <input type="number" value={requestedAmount} onChange={(e) => setRequestedAmount(e.target.value)} placeholder="250000" className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Loan Term (months) *</label>
                  <select value={loanTermMonths} onChange={(e) => setLoanTermMonths(e.target.value)} className={inputClass}>
                    <option value="12">12 months</option>
                    <option value="24">24 months</option>
                    <option value="36">36 months</option>
                    <option value="48">48 months</option>
                    <option value="60">60 months (5 years)</option>
                    <option value="84">84 months (7 years)</option>
                    <option value="120">120 months (10 years)</option>
                    <option value="180">180 months (15 years)</option>
                    <option value="240">240 months (20 years)</option>
                    <option value="360">360 months (30 years)</option>
                  </select>
                </div>
              </div>
              <div>
                <label className={labelClass}>Loan Purpose *</label>
                <input type="text" value={loanPurpose} onChange={(e) => setLoanPurpose(e.target.value)} placeholder="Home purchase, debt consolidation, etc." className={inputClass} />
              </div>
              {loanType === "mortgage" && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className={labelClass}>Property Address</label>
                    <input type="text" value={propertyAddress} onChange={(e) => setPropertyAddress(e.target.value)} className={inputClass} />
                  </div>
                  <div>
                    <label className={labelClass}>Estimated Property Value ($)</label>
                    <input type="number" value={propertyValue} onChange={(e) => setPropertyValue(e.target.value)} className={inputClass} />
                  </div>
                </div>
              )}
              {loanType === "auto" && (
                <div>
                  <label className={labelClass}>Vehicle Information</label>
                  <input type="text" value={vehicleInfo} onChange={(e) => setVehicleInfo(e.target.value)} placeholder="Year, Make, Model" className={inputClass} />
                </div>
              )}
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>First Name *</label>
                  <input type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Last Name *</label>
                  <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} className={inputClass} />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Email *</label>
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Phone *</label>
                  <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="555-123-4567" className={inputClass} />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Date of Birth *</label>
                  <input type="date" value={dob} onChange={(e) => setDob(e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>SSN (Last 4 digits) *</label>
                  <input type="text" maxLength={4} value={ssnLastFour} onChange={(e) => setSsnLastFour(e.target.value.replace(/\D/g, ""))} placeholder="1234" className={inputClass} />
                </div>
              </div>
              <div>
                <label className={labelClass}>Street Address *</label>
                <input type="text" value={street} onChange={(e) => setStreet(e.target.value)} className={inputClass} />
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="col-span-2">
                  <label className={labelClass}>City *</label>
                  <input type="text" value={city} onChange={(e) => setCity(e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>State *</label>
                  <select value={state} onChange={(e) => setState(e.target.value)} className={inputClass}>
                    {US_STATES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className={labelClass}>ZIP *</label>
                  <input type="text" maxLength={10} value={zip} onChange={(e) => setZip(e.target.value)} className={inputClass} />
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Employer Name</label>
                  <input type="text" value={employerName} onChange={(e) => setEmployerName(e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Job Title</label>
                  <input type="text" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} className={inputClass} />
                </div>
              </div>
              <div>
                <label className={labelClass}>Years at Current Employer</label>
                <input type="number" step="0.5" value={employmentYears} onChange={(e) => setEmploymentYears(e.target.value)} className={inputClass} />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Annual Income ($) *</label>
                  <input type="number" value={annualIncome} onChange={(e) => setAnnualIncome(e.target.value)} placeholder="85000" className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Monthly Debt Payments ($)</label>
                  <input type="number" value={monthlyDebt} onChange={(e) => setMonthlyDebt(e.target.value)} placeholder="800" className={inputClass} />
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                <h4 className="font-medium text-blue-900 mb-2">Application Summary</h4>
                <div className="grid grid-cols-2 gap-2 text-sm text-blue-800">
                  <div>Loan Type: <span className="font-medium">{LOAN_TYPES.find(t => t.value === loanType)?.label}</span></div>
                  <div>Amount: <span className="font-medium">${parseFloat(requestedAmount || "0").toLocaleString()}</span></div>
                  <div>Applicant: <span className="font-medium">{firstName} {lastName}</span></div>
                  <div>Income: <span className="font-medium">${parseFloat(annualIncome || "0").toLocaleString()}/yr</span></div>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="flex justify-between mt-6">
            <button
              onClick={() => setStep(Math.max(1, step - 1))}
              disabled={step === 1}
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 disabled:opacity-40"
            >
              Previous
            </button>
            {step < 3 ? (
              <button
                onClick={() => setStep(step + 1)}
                className="px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
              >
                Continue
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={submitting || !annualIncome || !requestedAmount}
                className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                <Send className="h-4 w-4" />
                {submitting ? "Submitting..." : "Submit Application"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
