import React, { useState } from 'react';
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
  TextField,
  InputAdornment,
  Card,
  CardContent,
  Avatar,
} from '@mui/material';
import {
  Search as SearchIcon,
  Group as GroupIcon,
} from '@mui/icons-material';

// Mock data - Replace with actual API data
const mockUsers = [
  { 
    id: 1, 
    username: 'john_doe', 
    email: 'john@example.com', 
    totalSongs: 15,
    recentActivity: [
      { name: 'Song1.mp3', date: '2023-11-08', result: 'AI' },
      { name: 'Song2.mp3', date: '2023-11-07', result: 'Human' }
    ]
  },
  { 
    id: 2, 
    username: 'jane_smith', 
    email: 'jane@example.com', 
    totalSongs: 8,
    recentActivity: [
      { name: 'MySong.mp3', date: '2023-11-08', result: 'AI' }
    ]
  },
  { 
    id: 3, 
    username: 'mike_wilson', 
    email: 'mike@example.com', 
    totalSongs: 23,
    recentActivity: [
      { name: 'Track1.mp3', date: '2023-11-08', result: 'Human' },
      { name: 'Track2.mp3', date: '2023-11-07', result: 'AI' }
    ]
  },
];

const UserManagement = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredUsers = mockUsers.filter(user =>
    user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold' }}>
        User Management
      </Typography>

      {/* Total Users Card */}
      <Card 
        elevation={0}
        sx={{ 
          boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)',
          mb: 4,
          maxWidth: 300
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'secondary.main', width: 56, height: 56 }}>
              <GroupIcon sx={{ fontSize: 32 }} />
            </Avatar>
            <Box>
              <Typography variant="h3" fontWeight="bold">
                {mockUsers.length}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Total Users
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* User List */}
      <Paper 
        elevation={0}
        sx={{ 
          boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)',
        }}
      >
        <Box sx={{ p: 3 }}>
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
              mb: 3,
              maxWidth: 400,
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'background.paper',
              },
            }}
          />

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Username</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell align="center">Total Songs</TableCell>
                  <TableCell>Recent Activity</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow 
                    key={user.id}
                    sx={{
                      '&:hover': {
                        backgroundColor: 'rgba(0, 184, 148, 0.04)',
                      },
                    }}
                  >
                    <TableCell>
                      <Typography variant="subtitle2" fontWeight="medium">
                        {user.username}
                      </Typography>
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell align="center">
                      <Typography 
                        variant="subtitle2" 
                        sx={{ 
                          color: 'secondary.main',
                          fontWeight: 'medium'
                        }}
                      >
                        {user.totalSongs}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box>
                        {user.recentActivity.map((activity, index) => (
                          <Typography 
                            key={index} 
                            variant="caption" 
                            display="block"
                            color="text.secondary"
                            sx={{ mb: 0.5 }}
                          >
                            {activity.name} - {activity.result} ({activity.date})
                          </Typography>
                        ))}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </Paper>
    </Box>
  );
};

export default UserManagement;