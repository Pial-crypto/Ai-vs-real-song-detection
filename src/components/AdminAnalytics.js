import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  LinearProgress,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

// Mock data - Replace with actual API data
const monthlyData = [
  { name: 'Jan', total: 65, ai: 40, human: 25 },
  { name: 'Feb', total: 85, ai: 55, human: 30 },
  { name: 'Mar', total: 75, ai: 45, human: 30 },
  { name: 'Apr', total: 95, ai: 60, human: 35 },
  { name: 'May', total: 115, ai: 70, human: 45 },
  { name: 'Jun', total: 95, ai: 60, human: 35 },
];

const accuracyData = [
  { name: 'Week 1', accuracy: 92 },
  { name: 'Week 2', accuracy: 94 },
  { name: 'Week 3', accuracy: 93 },
  { name: 'Week 4', accuracy: 95 },
  { name: 'Week 5', accuracy: 96 },
  { name: 'Week 6', accuracy: 94 },
];

const genreData = [
  { name: 'Pop', value: 35, color: '#00B894' },
  { name: 'Rock', value: 25, color: '#FF7675' },
  { name: 'Hip Hop', value: 20, color: '#74B9FF' },
  { name: 'Electronic', value: 15, color: '#A29BFE' },
  { name: 'Other', value: 5, color: '#636E72' },
];

const AdminAnalytics = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold' }}>
        System Analytics
      </Typography>

      <Grid container spacing={3}>
        {/* Monthly Predictions Chart */}
        <Grid item xs={12}>
          <Paper
            elevation={0}
            sx={{
              p: 3,
              boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)',
            }}
          >
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
              Monthly Predictions Overview
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.1)" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: 'none',
                    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                    borderRadius: 8,
                  }}
                />
                <Legend />
                <Bar dataKey="ai" name="AI Generated" fill="#00B894" stackId="a" />
                <Bar dataKey="human" name="Human Made" fill="#636E72" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* System Accuracy Chart */}
        <Grid item xs={12} md={8}>
          <Paper
            elevation={0}
            sx={{
              p: 3,
              boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)',
              height: '100%',
            }}
          >
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
              System Accuracy Trend
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={accuracyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.1)" />
                <XAxis dataKey="name" />
                <YAxis domain={[85, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: 'none',
                    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                    borderRadius: 8,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="accuracy"
                  stroke="#00B894"
                  strokeWidth={2}
                  dot={{ fill: '#00B894', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Genre Distribution */}
        <Grid item xs={12} md={4}>
          <Paper
            elevation={0}
            sx={{
              p: 3,
              boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)',
              height: '100%',
            }}
          >
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
              Genre Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={genreData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {genreData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: 'none',
                    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                    borderRadius: 8,
                  }}
                />
                <Legend 
                  verticalAlign="middle" 
                  align="right"
                  layout="vertical"
                />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* System Stats */}
        <Grid item xs={12}>
          <Paper
            elevation={0}
            sx={{
              p: 3,
              boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)',
            }}
          >
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
              System Performance
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    CPU Usage
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={65}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'rgba(0,0,0,0.09)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 4,
                      },
                    }}
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                    65% / 100%
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Memory Usage
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={45}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'rgba(0,0,0,0.09)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 4,
                      },
                    }}
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                    45% / 100%
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Storage Usage
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={28}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'rgba(0,0,0,0.09)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 4,
                      },
                    }}
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                    28% / 100%
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdminAnalytics;