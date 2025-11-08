import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Divider,
  Alert,
  Snackbar,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';

const AdminSettings = () => {
  const [settings, setSettings] = useState({
    enableUserRegistration: true,
    maxUploadSize: 10,
    storageLimit: 1000,
    modelVersion: '1.0.0',
    confidenceThreshold: 85,
    enableEmailNotifications: true,
    autoDeleteInactiveDays: 30,
    maintenanceMode: false,
  });

  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success',
  });

  const handleChange = (field) => (event) => {
    setSettings({
      ...settings,
      [field]: event.target.type === 'checkbox' ? event.target.checked : event.target.value,
    });
  };

  const handleSave = () => {
    // Save settings to backend
    setSnackbar({
      open: true,
      message: 'Settings saved successfully',
      severity: 'success',
    });
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold' }}>
        System Settings
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper
            elevation={0}
            sx={{
              p: 3,
              boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)',
            }}
          >
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
              General Settings
            </Typography>

            <Box sx={{ mt: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableUserRegistration}
                    onChange={handleChange('enableUserRegistration')}
                    color="primary"
                  />
                }
                label="Enable User Registration"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.maintenanceMode}
                    onChange={handleChange('maintenanceMode')}
                    color="warning"
                  />
                }
                label="Maintenance Mode"
              />

              <TextField
                fullWidth
                label="Max Upload Size (MB)"
                type="number"
                value={settings.maxUploadSize}
                onChange={handleChange('maxUploadSize')}
                sx={{ mt: 2 }}
              />

              <TextField
                fullWidth
                label="Storage Limit (GB)"
                type="number"
                value={settings.storageLimit}
                onChange={handleChange('storageLimit')}
                sx={{ mt: 2 }}
              />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper
            elevation={0}
            sx={{
              p: 3,
              boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)',
            }}
          >
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
              Model Settings
            </Typography>

            <Box sx={{ mt: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Model Version</InputLabel>
                <Select
                  value={settings.modelVersion}
                  label="Model Version"
                  onChange={handleChange('modelVersion')}
                >
                  <MenuItem value="1.0.0">Version 1.0.0</MenuItem>
                  <MenuItem value="1.1.0">Version 1.1.0</MenuItem>
                  <MenuItem value="1.2.0">Version 1.2.0</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Confidence Threshold (%)"
                type="number"
                value={settings.confidenceThreshold}
                onChange={handleChange('confidenceThreshold')}
                sx={{ mt: 2 }}
              />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper
            elevation={0}
            sx={{
              p: 3,
              boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)',
            }}
          >
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
              User Management Settings
            </Typography>

            <Box sx={{ mt: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableEmailNotifications}
                    onChange={handleChange('enableEmailNotifications')}
                    color="primary"
                  />
                }
                label="Enable Email Notifications"
              />

              <TextField
                fullWidth
                label="Auto-delete Inactive Users (days)"
                type="number"
                value={settings.autoDeleteInactiveDays}
                onChange={handleChange('autoDeleteInactiveDays')}
                sx={{ mt: 2 }}
              />
            </Box>

            <Divider sx={{ my: 3 }} />

            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<SaveIcon />}
                onClick={handleSave}
              >
                Save Settings
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AdminSettings;