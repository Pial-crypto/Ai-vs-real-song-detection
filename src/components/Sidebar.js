import { useState } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Box,
  Typography,
  useTheme,
  Divider,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from '@mui/material';
import {
  Home as HomeIcon,
  CloudUpload as UploadIcon,
  History as HistoryIcon,
  Logout as LogoutIcon,
  ChevronLeft as ChevronLeftIcon,
  MusicNote as MusicNoteIcon,
  People as UsersIcon,
  AdminPanelSettings as AdminIcon,
} from '@mui/icons-material';
const getMenuItems = (userRole) => {
  if (userRole === 'admin') {
    return [
      { id: 'dashboard', label: 'Dashboard', icon: HomeIcon },
      { id: 'users', label: 'User Management', icon: UsersIcon },
    ];
  }

  return [
    { id: 'dashboard', label: 'Dashboard', icon: HomeIcon },
    { id: 'upload', label: 'Upload Song', icon: UploadIcon },
    { id: 'history', label: 'My History', icon: HistoryIcon },
  ];
};

const Sidebar = ({ open, onClose, currentView, onViewChange, onToggleDarkMode, userRole, onLogout }) => {
  const theme = useTheme();
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false);

  return (
    <Drawer
      variant="permanent"
      anchor="left"
      open={open}
      sx={{
        width: 240,
        flexShrink: 0,
        position: 'fixed',
        height: '100%',
        '& .MuiDrawer-paper': {
          width: 240,
          height: '100%',
          position: 'fixed',
          border: 'none',
          backgroundColor: theme.palette.background.paper,
          boxShadow: '0px 2px 10px rgba(0, 0, 0, 0.05)',
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          '& .MuiListItem-root': {
            margin: '4px 8px',
            padding: '10px 16px',
            transition: 'all 0.2s ease-in-out',
          },
          '& .MuiListItemIcon-root': {
            minWidth: 40,
            color: theme.palette.text.secondary,
          },
        },
        '& .MuiDrawer-paperAnchorLeft': {
          left: open ? 0 : -240,
        },
      }}
    >
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <MusicNoteIcon sx={{ color: 'secondary.main' }} />
          <Typography variant="h6" color="primary" fontWeight="bold">
            AI Song Detector
          </Typography>
        </Box>
        <IconButton onClick={onClose}>
          <ChevronLeftIcon />
        </IconButton>
      </Box>

      <Divider sx={{ mx: 2 }} />

      <List sx={{ px: 2, flex: 1 }}>
        {getMenuItems(userRole).map(({ id, label, icon: Icon }) => (
          <ListItem
            button
            key={id}
            selected={currentView === id}
            onClick={() => onViewChange(id)}
            sx={{
              borderRadius: 2,
              mb: 1,
              position: 'relative',
              '&::before': {
                content: '""',
                position: 'absolute',
                left: -8,
                top: '50%',
                transform: 'translateY(-50%)',
                height: '60%',
                width: 4,
                borderRadius: '0 4px 4px 0',
                backgroundColor: 'secondary.main',
                opacity: currentView === id ? 1 : 0,
                transition: 'opacity 0.2s ease-in-out',
              },
              '&.Mui-selected': {
                backgroundColor: 'secondary.light',
                color: 'secondary.main',
                '&:hover': {
                  backgroundColor: 'secondary.lighter',
                },
                '& .MuiListItemIcon-root': {
                  color: 'secondary.main',
                },
              },
              '&:hover': {
                backgroundColor: 'rgba(0, 184, 148, 0.08)',
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <Icon />
            </ListItemIcon>
            <ListItemText primary={label} />
          </ListItem>
        ))}
      </List>

      <Divider sx={{ mx: 2 }} />
      
      <Box sx={{ p: 2 }}>
        <Box sx={{ 
          mb: 2,
          p: 1.5,
          backgroundColor: userRole === 'admin' ? 'error.lighter' : theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)',
          borderRadius: 2,
          border: userRole === 'admin' ? '1px dashed error.main' : 'none',
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Avatar
              sx={{
                bgcolor: userRole === 'admin' ? 'error.main' : 'secondary.main',
                width: 32,
                height: 32,
              }}
            >
              {userRole === 'admin' ? <AdminIcon fontSize="small" /> : 'U'}
            </Avatar>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: userRole === 'admin' ? 'error.main' : 'text.primary' }}>
                {userRole === 'admin' ? 'Administrator' : 'Regular User'}
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {userRole === 'admin' ? 'Full Access' : 'Limited Access'}
              </Typography>
            </Box>
          </Box>
        </Box>

        <ListItem
          button
          onClick={() => setLogoutDialogOpen(true)}
          sx={{
            borderRadius: 2,
            color: 'error.main',
            '&:hover': {
              backgroundColor: 'error.lighter',
            },
          }}
        >
          <ListItemIcon sx={{ minWidth: 40, color: 'error.main' }}>
            <LogoutIcon />
          </ListItemIcon>
          <ListItemText 
            primary="Logout" 
            primaryTypographyProps={{
              fontSize: '0.875rem',
              fontWeight: 500
            }}
          />
        </ListItem>
      </Box>

      <Dialog
        open={logoutDialogOpen}
        onClose={() => setLogoutDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle sx={{ pb: 1 }}>
          Confirm Logout
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to logout from your account?
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button 
            onClick={() => setLogoutDialogOpen(false)}
            variant="outlined"
            color="inherit"
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              onLogout();
              setLogoutDialogOpen(false);
            }}
            variant="contained"
            color="error"
            startIcon={<LogoutIcon />}
            sx={{ ml: 1 }}
          >
            Logout
          </Button>
        </DialogActions>
      </Dialog>
    </Drawer>
  );
};

export default Sidebar;