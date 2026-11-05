import React, { useEffect, useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';

import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';

// Student Pages
import { StudentDashboard } from './pages/student/StudentDashboard';
import { ExperimentWorkspace } from './pages/student/ExperimentWorkspace';
import { VirtualLabPage } from './pages/student/VirtualLabPage';
import { MySubmissionsPage } from './pages/student/MySubmissionsPage';

// Faculty Pages
import { FacultyDashboard } from './pages/faculty/FacultyDashboard';
import { ManualGeneratorPage } from './pages/faculty/ManualGeneratorPage';
import { SubmissionVerificationPage } from './pages/faculty/SubmissionVerificationPage';
import { CourseManagerPage } from './pages/faculty/CourseManagerPage';
import { LiveLabMonitoringPage } from './pages/faculty/LiveLabMonitoringPage';

// HOD Pages
import { HODDashboard } from './pages/hod/HODDashboard';

// Auth Pages
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';

const MainLayout: React.FC = () => {
  const { isAuthenticated, role, loading } = useAuth();

  const [currentTab, setCurrentTab] = useState<string>('student_dashboard');
  const [selectedExperimentId, setSelectedExperimentId] =
    useState<number | undefined>(undefined);
  const [selectedSubmissionId, setSelectedSubmissionId] =
    useState<number | undefined>(undefined);

  const [authView, setAuthView] = useState<'login' | 'register'>(
    window.location.pathname === '/register' ? 'register' : 'login'
  );
  const [prefilledEmail, setPrefilledEmail] = useState<string>('');

  const handleSwitchToLogin = (email?: string) => {
    if (email) setPrefilledEmail(email);
    setAuthView('login');
    if (window.location.pathname !== '/login') {
      window.history.pushState(null, '', '/login');
    }
  };

  const handleSwitchToRegister = () => {
    setAuthView('register');
    if (window.location.pathname !== '/register') {
      window.history.pushState(null, '', '/register');
    }
  };

  // Set the default dashboard based on the authenticated role
  useEffect(() => {
    if (!isAuthenticated) return;

    switch (role) {
      case 'student':
        setCurrentTab('student_dashboard');
        break;

      case 'faculty':
        setCurrentTab('faculty_dashboard');
        break;

      case 'hod':
        setCurrentTab('hod_dashboard');
        break;

      default:
        setCurrentTab('student_dashboard');
    }
  }, [role, isAuthenticated]);

  // Loading Screen
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div
          className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"
          role="status"
          aria-label="Loading"
        />
      </div>
    );
  }

  // Registration Page
  if (!isAuthenticated && authView === 'register') {
    return <RegisterPage onSwitchToLogin={handleSwitchToLogin} />;
  }

  // Login Page
  if (!isAuthenticated) {
    return <LoginPage initialEmail={prefilledEmail} onSwitchToRegister={handleSwitchToRegister} />;
  }

  // Handle experiment selection
  const handleSelectExperiment = (expId: number, labType: string) => {
    setSelectedExperimentId(expId);

    if (labType === 'digital_electronics') {
      setCurrentTab('virtual_lab');
    } else {
      setCurrentTab('coding_workspace');
    }
  };

  // Handle submission review
  const handleReviewSubmission = (subId: number) => {
    setSelectedSubmissionId(subId);
    setCurrentTab('verifications');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 font-sans">
      <Navbar />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
        />

        <main className="flex-1 min-w-0 flex overflow-hidden">
          {/* STUDENT VIEWS */}
          {role === 'student' && (
            <>
              {currentTab === 'student_dashboard' && (
                <StudentDashboard
                  onSelectExperiment={handleSelectExperiment}
                  onOpenVirtualLab={() => setCurrentTab('virtual_lab')}
                  onOpenCompiler={() => setCurrentTab('coding_workspace')}
                />
              )}

              {currentTab === 'coding_workspace' && (
                <ExperimentWorkspace
                  experimentId={selectedExperimentId}
                  onOpenMySubmissions={() =>
                    setCurrentTab('my_submissions')
                  }
                />
              )}

              {currentTab === 'virtual_lab' && (
                <VirtualLabPage />
              )}

              {currentTab === 'my_submissions' && (
                <MySubmissionsPage
                  onOpenWorkspace={(expId) => {
                    setSelectedExperimentId(expId);
                    setCurrentTab('coding_workspace');
                  }}
                />
              )}
            </>
          )}

          {/* FACULTY VIEWS */}
          {role === 'faculty' && (
            <>
              {currentTab === 'faculty_dashboard' && (
                <FacultyDashboard
                  onNavigateTab={setCurrentTab}
                  onReviewSubmission={handleReviewSubmission}
                />
              )}

              {currentTab === 'course_manager' && (
                <CourseManagerPage />
              )}

              {currentTab === 'manual_generator' && (
                <ManualGeneratorPage />
              )}

              {currentTab === 'verifications' && (
                <SubmissionVerificationPage
                  initialSubmissionId={selectedSubmissionId}
                />
              )}

              {currentTab === 'live_monitoring' && (
                <LiveLabMonitoringPage />
              )}
            </>
          )}

          {/* HOD VIEWS */}
          {role === 'hod' && (
            <>
              {currentTab === 'hod_dashboard' && (
                <HODDashboard />
              )}

              {currentTab === 'live_monitoring' && (
                <LiveLabMonitoringPage />
              )}

              {currentTab === 'academic_reports' && (
                <HODDashboard />
              )}
            </>
          )}

          {/* Fallback for invalid tabs */}
          {![
            'student_dashboard',
            'coding_workspace',
            'virtual_lab',
            'my_submissions',
            'faculty_dashboard',
            'course_manager',
            'manual_generator',
            'verifications',
            'live_monitoring',
            'hod_dashboard',
            'academic_reports',
          ].includes(currentTab) && (
              <div className="flex-1 flex items-center justify-center text-slate-400">
                <p>Page not found. Please select a page from the sidebar.</p>
              </div>
            )}
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <MainLayout />
      </AuthProvider>
    </ToastProvider>
  );
}