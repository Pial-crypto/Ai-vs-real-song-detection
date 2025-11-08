import React from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Box,
  Avatar,
  useTheme,
  useMediaQuery,
  Menu,
  MenuItem,
  Chip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  ExitToApp as LogoutIcon,
  MusicNote as MusicIcon,
} from '@mui/icons-material';
const Navbar = ({ onMenuClick, userRole, onLogout }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [menuOpen, setMenuOpen] = React.useState(false);
  const menuAnchorRef = React.useRef(null);

  const handleMenuClick = () => {
    setMenuOpen((prevOpen) => !prevOpen);
  };

  const handleClose = (event) => {
    if (menuAnchorRef.current && menuAnchorRef.current.contains(event.target)) {
      return;
    }
    setMenuOpen(false);
  };

  return (
    <AppBar 
      position="fixed"
      elevation={0} 
      sx={{ 
        backgroundColor: 'background.paper',
        backdropFilter: 'blur(8px)',
        borderBottom: '1px solid',
        borderColor: 'divider',
        background: 'rgba(255, 255, 255, 0.9)',
        width: { xs: '100%', md: `calc(100% - ${onMenuClick ? '0px' : '240px'})` },
        ml: { xs: 0, md: onMenuClick ? '0px' : '240px' },
        transition: theme.transitions.create(['width', 'margin'], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        }),
      }}
    >
      <Toolbar sx={{ minHeight: { xs: '64px', sm: '70px' } }}>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={onMenuClick}
          sx={{ mr: 2, display: { md: 'none' } }}
        >
          <MenuIcon />
        </IconButton>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <MusicIcon sx={{ color: 'secondary.main', fontSize: 28 }} />
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 700,
              background: 'linear-gradient(45deg, #2D3436 30%, #00B894 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              display: { xs: 'none', sm: 'block' }
            }}
          >
            AI Song Detector
          </Typography>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, sm: 2 } }}>
       
          
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              padding: '4px 12px',
              borderRadius: '8px',
            }}
          >
            <Avatar
              sx={{
                bgcolor: 'secondary.main',
                width: 32,
                height: 32,
              }}
            >
              {userRole === 'admin' ? 'A' : 'U'}
            </Avatar>
            <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.main' }}>
                {userRole === 'admin' ? 'Admin User' : 'Regular User'}
              </Typography>
              <Chip
                label={userRole === 'admin' ? 'Administrator' : 'User'}
                size="small"
                color={userRole === 'admin' ? 'secondary' : 'primary'}
                sx={{ height: 20, fontSize: '0.7rem' }}
              />
            </Box>
          </Box>

          <Menu
            anchorEl={menuAnchorRef.current}
            open={menuOpen}
            onClose={handleClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'center',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'center',
            }}
            PaperProps={{
              elevation: 6,
              sx: {
                overflow: 'visible',
                mt: 0.5,
                borderRadius: '8px',
                border: '1px solid',
                borderColor: 'divider',
                backgroundColor: 'background.paper',
                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                minWidth: '160px',
                '&:before': {
                  display: 'none'
                },
                '& .MuiMenuItem-root': {
                  px: 2,
                  py: 1.5,
                  borderRadius: 1,
                  margin: '4px 8px',
                  '&:hover': {
                    backgroundColor: 'error.lighter',
                  },
                  '&:first-of-type': {
                    mt: '8px',
                  },
                  '&:last-child': {
                    mb: '8px',
                  },
                },
                '&:before': {
                  content: '""',
                  display: 'block',
                  position: 'absolute',
                  top: -6,
                  left: '50%',
                  width: 12,
                  height: 12,
                  bgcolor: 'background.paper',
                  transform: 'translate(-50%, -50%) rotate(45deg)',
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRight: 'none',
                  borderBottom: 'none',
                  zIndex: 0,
                },
              },
            }}
            slotProps={{
              paper: {
                sx: {
                  width: 180,
                  marginTop: '45px'
                }
              }
            }}
          >
            <Box sx={{ p: 0.5 }}>
              <MenuItem 
                onClick={onLogout}
                sx={{
                  color: 'error.main',
                  transition: 'all 0.2s',
                  borderRadius: '6px',
                  py: 0.75,
                  px: 1.5,
                  minHeight: 'unset',
                  '&:hover': {
                    backgroundColor: 'error.lighter',
                  },
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                }}
              >
                <LogoutIcon sx={{ 
                  fontSize: 16,
                }} />
                <Typography 
                  variant="body2"
                  sx={{ 
                    fontWeight: 500,
                    fontSize: '0.8125rem',
                  }}
                >
                  Logout
                </Typography>
              </MenuItem>
            </Box>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;