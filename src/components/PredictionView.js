import { useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Box,
  Chip,
  CircularProgress,
  IconButton,
} from '@mui/material';
import {
  Download as DownloadIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
} from '@mui/icons-material';

// Mock data for predictions
const mockPredictions = {
  fileName: 'song1.mp3',
  duration: '3:45',
  chunks: [
    { id: 1, start: '0:00', end: '0:30', prediction: 'AI', confidence: 92 },
    { id: 2, start: '0:30', end: '1:00', prediction: 'AI', confidence: 88 },
    { id: 3, start: '1:00', end: '1:30', prediction: 'Human', confidence: 75 },
    { id: 4, start: '1:30', end: '2:00', prediction: 'AI', confidence: 95 },
  ],
  modelPredictions: {
    cnn: { prediction: 'AI', confidence: 90 },
    mlp: { prediction: 'AI', confidence: 85 },
    svm: { prediction: 'AI', confidence: 88 },
  },
  finalDecision: 'AI',
  overallConfidence: 89,
};

const PredictionView = () => {
  const [isPlaying, setIsPlaying] = useState(false);

  return (
    <Grid container spacing={3}>
      {/* Song Info & Controls */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Grid container alignItems="center" spacing={3}>
            <Grid item>
              <IconButton
                size="large"
                sx={{
                  bgcolor: 'secondary.main',
                  color: 'white',
                  '&:hover': {
                    bgcolor: 'secondary.dark',
                  },
                }}
                onClick={() => setIsPlaying(!isPlaying)}
              >
                {isPlaying ? <PauseIcon /> : <PlayIcon />}
              </IconButton>
            </Grid>
            <Grid item xs>
              <Typography variant="h6">{mockPredictions.fileName}</Typography>
              <Typography variant="body2" color="text.secondary">
                Duration: {mockPredictions.duration}
              </Typography>
            </Grid>
            <Grid item>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                color="secondary"
              >
                Download Report
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Grid>

      {/* Final Prediction */}
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom>
            Final Decision
          </Typography>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              mt: 3,
            }}
          >
            <CircularProgress
              variant="determinate"
              value={mockPredictions.overallConfidence}
              size={120}
              thickness={8}
              sx={{ color: 'secondary.main' }}
            />
            <Box
              sx={{
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                mt: -15,
              }}
            >
              <Typography variant="h4" color="secondary.main">
                {mockPredictions.overallConfidence}%
              </Typography>
              <Chip
                label={mockPredictions.finalDecision}
                color={mockPredictions.finalDecision === 'AI' ? 'secondary' : 'primary'}
                sx={{ mt: 1 }}
              />
            </Box>
          </Box>
        </Paper>
      </Grid>

      {/* Model Predictions */}
      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Model Predictions
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(mockPredictions.modelPredictions).map(([model, data]) => (
              <Grid item xs={12} sm={4} key={model}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    bgcolor: 'grey.50',
                    textAlign: 'center',
                  }}
                >
                  <Typography variant="subtitle2" gutterBottom>
                    {model.toUpperCase()}
                  </Typography>
                  <Typography variant="h4" color="secondary.main">
                    {data.confidence}%
                  </Typography>
                  <Chip
                    label={data.prediction}
                    size="small"
                    color={data.prediction === 'AI' ? 'secondary' : 'primary'}
                    sx={{ mt: 1 }}
                  />
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Grid>

      {/* Chunk Analysis */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Chunk Analysis
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Time Range</TableCell>
                  <TableCell>Prediction</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell align="right">Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {mockPredictions.chunks.map((chunk) => (
                  <TableRow key={chunk.id}>
                    <TableCell>
                      {chunk.start} - {chunk.end}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={chunk.prediction}
                        size="small"
                        color={chunk.prediction === 'AI' ? 'secondary' : 'primary'}
                      />
                    </TableCell>
                    <TableCell>{chunk.confidence}%</TableCell>
                    <TableCell align="right">
                      <IconButton size="small">
                        <PlayIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default PredictionView;