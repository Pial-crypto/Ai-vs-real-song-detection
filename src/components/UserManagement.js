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
  Chip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Group as GroupIcon,
} from '@mui/icons-material';
import { getAllUsers } from '../functions/getAllusers';
import { getPredictionHistory } from '../functions/getPredictionHistory';
import axios from 'axios';

// Mock data - Replace with actual API data
const mockUsers = [
  { 
    id: 1, 
    username: 'john_doe', 
    email: 'john@example.com', 
    totalUploaded: 15,
    recentActivity: [
      { name: 'Song1.mp3', result: 'AI' },
      { name: 'Song2.mp3', result: 'Human' }
    ]
  },
  { 
    id: 2, 
    username: 'jane_smith', 
    email: 'jane@example.com', 
    totalUploaded: 8,
    recentActivity: [
      { name: 'MySong.mp3', result: 'AI' }
    ]
  },
  { 
    id: 3, 
    username: 'mike_wilson', 
    email: 'mike@example.com', 
    totalUploaded: 23,
    recentActivity: [
      { name: 'Track1.mp3', result: 'Human' },
      { name: 'Track2.mp3', result: 'AI' }
    ]
  },
  { 
    id: 4, 
    username: 'sarah_jones', 
    email: 'sarah@example.com', 
    totalUploaded: 12,
    recentActivity: [
      { name: 'Audio1.mp3', result: 'AI' }
    ]
  },
  { 
    id: 5, 
    username: 'alex_brown', 
    email: 'alex@example.com', 
    totalUploaded: 19,
    recentActivity: [
      { name: 'Music1.mp3', result: 'Human' },
      { name: 'Music2.mp3', result: 'AI' }
    ]
  },
];
const userBasedPrediciton=new Map();

const UserManagement = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [users, setUsers] = useState([]);
 // const [userBasedPrediciton,setUserBasedPrediction]=useState({});
 
useState(() => {

  getAllUsers().then(data => {
    console.log("Fetched users:", data);
   data.map(user=>{
    getPredictionHistory(user.id).then(predictionData => {
      userBasedPrediciton.set(user.id, predictionData);
    })
   })
    
    setUsers(data);
  }).catch(error => {
    console.error("Error fetching users:", error);
  });
}, []);

// users.forEach(user=>{
//     getPredictionHistory(user.id).then(predictionData => {
//         console.log("Fetching prediction for user:", user.id,predictionData);
//         userBasedPrediciton.set(user.id, predictionData);
//     });
// });

console.log("User Based Prediction Map:", userBasedPrediciton);




  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ 
      p: 4, 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
    }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="700" sx={{ color: '#1e293b', mb: 1 }}>
          User Management
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ fontWeight: 500 }}>
          Manage and monitor all registered users
        </Typography>
      </Box>

      {/* Total Users Card */}
      <Paper
        elevation={0}
        sx={{ 
          p: 3,
          mb: 3,
          borderRadius: 3,
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
          maxWidth: 280,
          boxShadow: '0 8px 16px rgba(99, 102, 241, 0.3)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box
            sx={{
              width: 60,
              height: 60,
              borderRadius: 2,
              background: 'rgba(255, 255, 255, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backdropFilter: 'blur(10px)',
            }}
          >
            <GroupIcon sx={{ fontSize: 32, color: 'white' }} />
          </Box>
          <Box>
            <Typography variant="h3" fontWeight="bold" sx={{ color: 'white' }}>
              {users.length}
            </Typography>
            <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 500 }}>
              Total Users
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* User List Table */}
      <Paper 
        elevation={0}
        sx={{ 
          borderRadius: 3,
          background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
          border: '1px solid #e2e8f0',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        }}
      >
        <Box sx={{ p: 3 }}>
          {/* Search Bar */}
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search users by username or email..."
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
              maxWidth: 500,
              '& .MuiOutlinedInput-root': {
                backgroundColor: '#f8fafc',
                borderRadius: 2,
                '&:hover': {
                  backgroundColor: '#f1f5f9',
                },
                '&.Mui-focused': {
                  backgroundColor: 'white',
                },
              },
            }}
          />

          {/* Users Table */}
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700, fontSize: '15px', color: '#475569' }}>
                    Username
                  </TableCell>
                  <TableCell sx={{ fontWeight: 700, fontSize: '15px', color: '#475569' }}>
                    Email
                  </TableCell>
                  <TableCell align="center" sx={{ fontWeight: 700, fontSize: '15px', color: '#475569' }}>
                    Total Uploaded
                  </TableCell>
                  <TableCell sx={{ fontWeight: 700, fontSize: '15px', color: '#475569' }}>
                    Recent Activity
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow 
                    key={user.id}
                    sx={{
                      '&:hover': {
                        backgroundColor: '#f8fafc',
                      },
                      transition: 'background-color 0.2s',
                    }}
                  >
                    <TableCell>
                      <Typography variant="body1" fontWeight="600" sx={{ color: '#1e293b' }}>
                        {user.username}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ color: '#64748b' }}>
                        {user.email}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip 
                        label={userBasedPrediciton.get(user.id)?.length || 0} 
                        size="small"
                        sx={{ 
                          fontWeight: 700,
                          backgroundColor: '#dbeafe',
                          color: '#1e40af',
                          minWidth: 50,
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        {userBasedPrediciton?.get(user.id)?.reverse().slice(0, 2).map((activity, index) => (
                          <Box 
                            key={index} 
                            sx={{ 
                              display: 'flex', 
                              alignItems: 'center', 
                              gap: 1 
                            }}
                          >
                            <Typography 
                              variant="caption" 
                              sx={{ 
                                color: '#64748b',
                                maxWidth: 150,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                              }}
                            >
                              {activity.fileName}
                            </Typography>
                            <Chip 
                              label={`${activity.finalPrediction.chunk_majority}-Chunk Majority`}
                              size="small"
                              sx={{
                                height: 20,
                                fontSize: '11px',
                                fontWeight: 600,
                                backgroundColor: activity.finalPrediction.chunk_majority.toLowerCase() === 'ai' ? '#ddd6fe' : '#fce7f3',
                                color: activity.finalPrediction.chunk_majority.toLowerCase() === 'ai' ? '#6b21a8' : '#be185d',
                              }}
                            />
                                <Chip 
                              label={`${activity.finalPrediction.model_majority}-Model Majority`}
                              size="small"
                              sx={{
                                height: 20,
                                fontSize: '11px',
                                fontWeight: 600,
                                backgroundColor: activity.finalPrediction.model_majority.toLowerCase() === 'ai' ? '#ddd6fe' : '#fce7f3',
                                color: activity.finalPrediction.model_majority.toLowerCase() === 'ai' ? '#6b21a8' : '#be185d',
                              }}
                            />
                          </Box>
                        ))}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* No Results Message */}
          {filteredUsers.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No users found matching your search
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default UserManagement;