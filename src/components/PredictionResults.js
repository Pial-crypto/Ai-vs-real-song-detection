import React, { useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  LinearProgress,
  CircularProgress,
  Chip,
  Button,
  IconButton,
  Divider,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  PauseCircle as PauseIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
} from '@mui/icons-material';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const mockChunkData = [
  { chunk: 1, AI: 0.85, Real: 0.15 },
  { chunk: 2, AI: 0.92, Real: 0.08 },
  { chunk: 3, AI: 0.78, Real: 0.22 },
  { chunk: 4, AI: 0.88, Real: 0.12 },
];

const mockModelData = [
  { name: 'CNN', value: 90 },
  { name: 'MLP', value: 85 },
  { name: 'SVM', value: 88 },
];

const COLORS = ['#00B894', '#2D3436'];

const PredictionResults = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentChunk, setCurrentChunk] = useState(0);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <Grid container spacing={3}>
      {/* Main Result Card */}
      <Grid item xs={12}>
        <Paper 
          sx={{ 
            p: 3,
            background: 'linear-gradient(120deg, #00B894 0%, #2D3436 100%)',
            color: 'white',
            borderRadius: 2,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h5" fontWeight="bold">
              Current Prediction
            </Typography>
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.3)' },
              }}
            >
              Download Report
            </Button>
          </Box>
          <Box sx={{ mt: 3, display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <Box>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Final Verdict
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                AI Generated
              </Typography>
              <Chip 
                label="High Confidence" 
                sx={{ 
                  mt: 1,
                  bgcolor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                }} 
              />
            </Box>
            <Box>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Overall Confidence
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                89%
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <IconButton 
                  size="small" 
                  sx={{ color: 'white' }}
                  onClick={togglePlay}
                >
                  {isPlaying ? <PauseIcon /> : <PlayIcon />}
                </IconButton>
                <IconButton 
                  size="small" 
                  sx={{ color: 'white' }}
                >
                  <ShareIcon />
                </IconButton>
              </Box>
            </Box>
          </Box>
        </Paper>
      </Grid>

      {/* Model Predictions */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom fontWeight="bold">
            Model Predictions
          </Typography>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={mockModelData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, value }) => `${name} (${value}%)`}
                >
                  {mockModelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Box>
        </Paper>
      </Grid>

      {/* Chunk Analysis */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom fontWeight="bold">
            Chunk Analysis
          </Typography>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockChunkData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="chunk" label={{ value: 'Chunk Number', position: 'bottom' }} />
                <YAxis label={{ value: 'Confidence', angle: -90, position: 'left' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="AI" fill="#00B894" />
                <Bar dataKey="Real" fill="#2D3436" />
              </BarChart>
            </ResponsiveContainer>
          </Box>
        </Paper>
      </Grid>

      {/* Timeline Progress */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom fontWeight="bold">
            Chunk Timeline
          </Typography>
          <Box sx={{ mt: 2 }}>
            <LinearProgress
              variant="determinate"
              value={(currentChunk / mockChunkData.length) * 100}
              sx={{
                height: 10,
                borderRadius: 5,
                bgcolor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 5,
                  bgcolor: 'secondary.main',
                },
              }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                0:00
              </Typography>
              <Typography variant="caption" color="text.secondary">
                3:45
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default PredictionResults;