import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Block as BlockIcon,
  CheckCircle as VerifiedIcon,
  Search as SearchIcon,
} from '@mui/icons-material';

// Mock data - Replace with actual API calls
const mockUsers = [
  { id: 1, username: 'john_doe', email: 'john@example.com', status: 'active', predictions: 15, lastActive: '2023-11-08' },
  { id: 2, username: 'jane_smith', email: 'jane@example.com', status: 'blocked', predictions: 8, lastActive: '2023-11-07' },
  { id: 3, username: 'mike_wilson', email: 'mike@example.com', status: 'active', predictions: 23, lastActive: '2023-11-08' },
];

const AdminUsers = () => {
  const [users, setUsers] = useState(mockUsers);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleDeleteUser = (user) => {
    setSelectedUser(user);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    setUsers(users.filter(u => u.id !== selectedUser.id));
    setDeleteDialogOpen(false);
    setSelectedUser(null);
  };

  const handleToggleStatus = (userId) => {
    setUsers(users.map(user => {
      if (user.id === userId) {
        return {
          ...user,
          status: user.status === 'active' ? 'blocked' : 'active'
        };
      }
      return user;
    }));
  };

  const filteredUsers = users.filter(user => 
    user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold' }}>
        Manage Users
      </Typography>

      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search users by name or email..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
          sx={{
            maxWidth: 400,
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'background.paper',
            },
          }}
        />
      </Box>

      <TableContainer component={Paper} elevation={0} sx={{ 
        boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)',
      }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="center">Total Predictions</TableCell>
              <TableCell>Last Active</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredUsers.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Chip
                    label={user.status === 'active' ? 'Active' : 'Blocked'}
                    color={user.status === 'active' ? 'success' : 'error'}
                    size="small"
                    icon={user.status === 'active' ? <VerifiedIcon /> : <BlockIcon />}
                  />
                </TableCell>
                <TableCell align="center">{user.predictions}</TableCell>
                <TableCell>{user.lastActive}</TableCell>
                <TableCell align="right">
                  <IconButton
                    color={user.status === 'active' ? 'error' : 'success'}
                    onClick={() => handleToggleStatus(user.id)}
                    size="small"
                    sx={{ mr: 1 }}
                  >
                    {user.status === 'active' ? <BlockIcon /> : <VerifiedIcon />}
                  </IconButton>
                  <IconButton
                    color="error"
                    onClick={() => handleDeleteUser(user)}
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle sx={{ pb: 1 }}>
          Confirm User Deletion
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the user "{selectedUser?.username}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button 
            onClick={() => setDeleteDialogOpen(false)}
            variant="outlined"
            color="inherit"
          >
            Cancel
          </Button>
          <Button
            onClick={confirmDelete}
            variant="contained"
            color="error"
            startIcon={<DeleteIcon />}
            sx={{ ml: 1 }}
          >
            Delete User
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminUsers;