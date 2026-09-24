import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import Layout from "./components/Layout.js";
import { LoadingState } from "./components/Common.js";
import { useAuth } from "./context/AuthContext.js";
import DashboardPage from "./pages/DashboardPage.js";
import LeadDetailPage from "./pages/LeadDetailPage.js";
import LeadsPage from "./pages/LeadsPage.js";
import LoginPage from "./pages/LoginPage.js";
import ReportsPage from "./pages/ReportsPage.js";
import UsersPage from "./pages/UsersPage.js";

function ProtectedLayout() {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) {
    return <div className="full-page-state"><LoadingState label="Validando sessão..." /></div>;
  }
  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <Layout />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedLayout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/leads" element={<LeadsPage />} />
        <Route path="/leads/:id" element={<LeadDetailPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/users" element={<UsersPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
