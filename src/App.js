import { useState } from 'react';
import { ThemeProvider, CssBaseline, Box, useMediaQuery, Typography, IconButton } from '@mui/material';
import { Menu as MenuIcon } from '@mui/icons-material';
import { createTheme } from '@mui/material/styles';
import Sidebar from './components/Sidebar';
import { default as AdminDashboard } from './components/Dashboard';
import UserDashboard from './components/UserDashboard';
import UploadManager from './components/UploadManager';
import PredictionResults from './components/PredictionResults';
import HistoryView from './components/HistoryView';
import UserManagement from './components/UserManagement';
import Login from './components/Login';
import { ToastContainer } from 'react-toastify';

import 'react-toastify/dist/ReactToastify.css';
import { getFromLocal, removeFromLocal } from './functions/localStorage';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2D3436',
      light: '#636e72',
      dark: '#1e272e',
    },
    secondary: {
      main: '#00B894',
      light: '#55efc4',
      dark: '#00b894',
    },
    background: {
      default: '#f5f6fa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(getFromLocal('user') !== null);
  const [userRole, setUserRole] = useState(getFromLocal('user') ? getFromLocal('user').role : null);
  const [currentView, setCurrentView] = useState('dashboard');
  const [darkMode, setDarkMode] = useState(false);
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);
  // Show sidebar toggle button if sidebar is closed
  const showSidebarToggle = isLoggedIn && !sidebarOpen;

  const renderCurrentView = () => {
    switch(currentView) {
      case 'upload':
        return <UploadManager />;
      case 'predict':
        return <PredictionResults />;
      case 'history':
        return <HistoryView />;
      case 'users':
        return <UserManagement />;
      default:
        return userRole === 'admin' ? <AdminDashboard /> : <UserDashboard />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box 
        sx={{ 
          minHeight: '100vh',
          display: 'flex',
          flexDirection: !isLoggedIn ? 'column' : 'row',
          background: !isLoggedIn ? 'linear-gradient(135deg, #00B894 0%, #2D3436 100%)' : 'none'
        }}
      >
        {!isLoggedIn ? (
          <Box 
            sx={{ 
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              p: 3
            }}
          >
            <Box sx={{ maxWidth: 400, width: '100%', mb: 4, textAlign: 'center' }}>
              <Typography variant="h3" component="h1" fontWeight="bold" gutterBottom>
                AI Song Detection
              </Typography>
              <Typography variant="h6" sx={{ opacity: 0.9, mb: 4 }}>
                Detect AI-generated music with our advanced machine learning models
              </Typography>
            </Box>
            <Login onLogin={(role) => {
              setIsLoggedIn(true);
              setUserRole(role);
            }} />
          </Box>
        ) : (
          <Box sx={{ 
            display: 'flex', 
            width: '100%',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <Sidebar 
              open={sidebarOpen}
              onClose={() => setSidebarOpen(false)}
              currentView={currentView}
              onViewChange={setCurrentView}
              onToggleDarkMode={() => setDarkMode(!darkMode)}
              userRole={userRole}
              onLogout={() => {
                removeFromLocal('user');
                setIsLoggedIn(false);
                setUserRole(null);
              }}
            />
            <Box sx={{ 
              flexGrow: 1,
              minHeight: '100vh',
              transition: theme.transitions.create(['margin', 'width'], {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
              marginLeft: { xs: 0, md: sidebarOpen ? '240px' : '0' },
              width: { xs: '100%', md: `calc(100% - ${sidebarOpen ? 240 : 0}px)` },
              bgcolor: 'background.default',
              position: 'relative'
            }}>
              {/* <Navbar 
                onMenuClick={() => setSidebarOpen(!sidebarOpen)} 
                userRole={userRole}
                onLogout={() => {
                  setIsLoggedIn(false);
                  setUserRole(null);
                }}
              /> */}
              <Box 
                sx={{ 
                  p: { xs: 2, md: 3 },
                  mt: { xs: '64px', sm: '70px' },
                  height: 'calc(100vh - 70px)',
                  overflowY: 'auto'
                }}
              >
                {renderCurrentView()}
              </Box>
              {showSidebarToggle && (
                <Box sx={{ position: 'fixed', left: 16, top: 80, zIndex: 1200 }}>
                  <IconButton
                    color="secondary"
                    onClick={() => setSidebarOpen(true)}
                    sx={{ 
                      bgcolor: 'white', 
                      boxShadow: 3,
                      '&:hover': { bgcolor: 'white', opacity: 0.9 }
                    }}
                    size="large"
                  >
                    <MenuIcon />
                  </IconButton>
                </Box>
              )}
            </Box>
          </Box>
        )}
      </Box>
      <ToastContainer position="bottom-right" />
    </ThemeProvider>
  );
}

export default App;