import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Grid,
  Card,
  Chip,
  Fade,
  Alert,
  IconButton,
  Zoom,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import axios from 'axios';
import {
  CloudUpload as UploadIcon,
  Audiotrack as AudioIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { savePrediction } from '../functions/savePrediction';
import axios from 'axios';
const UploadManager = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [predictions, setPredictions] = useState(null);
  const [error, setError] = useState(null);
const BASE_URL = "http://127.0.0.1:8000";
  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0]; // Only process the first file
    if (file) {
      console.log("ACCEPTED file:", file);
      if (file.type !== 'audio/mpeg') {
        setError('Please upload only MP3 files');
        return;
      }
      setError(null);
      setUploading(true);
      setUploadedFile(file);
      

  try {
    // Move to uploading/processing step
    setActiveStep(1);

    // Prepare form data
    const formData = new FormData();
    formData.append("file", file);
    console.log("FORM DATA:",formData);

    // === POST to FastAPI `/prediction` ===
    const response = await axios.post(`${BASE_URL}/prediction`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    // Extract prediction result
    const data = response.data;
    console.log("Prediction response:", data);
    
    // Structure the predictions data
    const prediction = {
      chunkPrediction: data.chunk_predictions || [],
      final_decision: {
        model_majority: data.final_decision?.model_majority,
        chunk_majority: data.final_decision?.chunk_majority,
        
      },
      fileName: file.name,
      model_predictions: data.model_predictions || {}
    };
    savePrediction(prediction);
    
    console.log("Structured predictions:", prediction);

    // Update state with predictions
    setPredictions(prediction);
    setActiveStep(2);
  } catch (err) {
    console.error(err);
    setError("An error occurred during prediction");
  } finally {
    setUploading(false);
  }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/mpeg': ['.mp3']
    },
    multiple: false
  });

  const handleReset = () => {
    setActiveStep(0);
    setUploadedFile(null);
    setPredictions(null);
    setError(null);
  };

  const tableStyles = {
    '& .MuiTableCell-root': {
      padding: '8px 16px',
      borderColor: '#e0e0e0',
      fontSize: '14px'
    },
    '& .MuiTableHead-root th': {
      backgroundColor: '#f5f5f5',
      fontWeight: 600,
      color: '#333'
    },
    '& .MuiTableRow-root:hover': {
      backgroundColor: '#fafafa'
    }
  };

  return (
    <Box sx={{ p: 4, minHeight: '80vh', bgcolor: '#ffffff' }}>
      <Box sx={{ maxWidth: 1400, mx: 'auto' }}>
        <Typography variant="h4" sx={{ mb: 4, color: '#333' }}>AI vs Real Song Detection</Typography>
        <Grid container spacing={4}>
          {/* Upload Area */}
        {activeStep === 0 && (
          <Zoom in timeout={800}>
            <Grid item xs={12}>
              <Card
                elevation={8}
                sx={{
                  background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
                  overflow: 'hidden',
                  position: 'relative',
                }}
              >
                <Box
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    opacity: 0.1,
                    backgroundImage: 'url("data:image/svg+xml,%3Csvg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"%3E%3Cpath d="M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z" fill="%23ffffff" fill-opacity="0.4" fill-rule="evenodd"/%3E%3C/svg%3E")',
                  }}
                />
                <Paper
                  sx={{
                    m: 3,
                    bgcolor: 'rgba(255, 255, 255, 0.9)',
                    borderRadius: 2,
                    backdropFilter: 'blur(10px)',
                    transition: 'all 0.3s ease',
                    transform: isDragActive ? 'scale(0.98)' : 'scale(1)',
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'rgba(255, 255, 255, 1)',
                      transform: 'scale(0.99)',
                    }
                  }}
                  {...getRootProps()}
                >
                  <input {...getInputProps()} />
                  <Box
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      py: 8,
                    }}
                  >
                    <IconButton
                      sx={{
                        p: 3,
                        bgcolor: 'primary.main',
                        color: 'white',
                        mb: 3,
                        '&:hover': {
                          bgcolor: 'primary.dark',
                        }
                      }}
                    >
                      <AudioIcon sx={{ fontSize: 40 }} />
                    </IconButton>
                    <Typography variant="h4" gutterBottom color="primary.dark" sx={{ fontWeight: 600 }}>
                      Upload Your Song
                    </Typography>
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      Drag & drop here or click to browse
                    </Typography>
                    <Chip
                      label="MP3 format only"
                      color="primary"
                      variant="outlined"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  </Box>
                </Paper>
              </Card>
            </Grid>
          </Zoom>
        )}

        {/* Processing State */}
        {activeStep === 1 && (
          <Fade in timeout={1000}>
            <Grid item xs={12}>
              <Card 
                elevation={8}
                sx={{
                  p: 6,
                  textAlign: 'center',
                  background: 'linear-gradient(135deg, #4a148c 0%, #311b92 100%)',
                  color: 'white',
                }}
              >
                <Box sx={{ position: 'relative', mb: 4 }}>
                  <CircularProgress
                    size={80}
                    thickness={2}
                    sx={{ color: 'rgba(255, 255, 255, 0.3)' }}
                  />
                  <CircularProgress
                    size={80}
                    thickness={2}
                    sx={{
                      position: 'absolute',
                      left: 'calc(50% - 40px)',
                      color: 'white',
                      animationDuration: '3s',
                    }}
                  />
                </Box>
                <Typography variant="h4" gutterBottom sx={{ fontWeight: 500 }}>
                  Analyzing Your Song
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.8 }}>
                  Please wait while our AI models process your audio
                </Typography>
                <LinearProgress 
                  sx={{ 
                    mt: 4, 
                    height: 6, 
                    borderRadius: 3,
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                  }} 
                />
              </Card>
            </Grid>
          </Fade>
        )}

        {/* Results Display */}
        {activeStep === 2 && predictions && (
          <>
            <Grid item xs={12}>
              <Box sx={{ mb: 4 }}>
                <Typography variant="h6" sx={{ mb: 2, color: '#1a237e', fontWeight: 500 }}>
                  Chunk-wise Predictions
                </Typography>
                <TableContainer component={Paper} sx={{ boxShadow: 1 }}>
                  <Table size="small" sx={tableStyles}>
                    <TableHead>
                      <TableRow>
                        <TableCell>Chunk</TableCell>
                        <TableCell>SVM</TableCell>
                        <TableCell>RF</TableCell>
                        <TableCell>XGBOOST</TableCell>
                        <TableCell>MLP</TableCell>
                        <TableCell>EARLY_STOPPING_MLP</TableCell>
                        <TableCell>CNN</TableCell>
                        <TableCell>EARLY_STOPPING_CNN</TableCell>
                        <TableCell>Chunk Majority</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                    {predictions.chunkPrediction.map((chunk, index) => (
  <TableRow key={index} hover>
    <TableCell sx={{ fontWeight: 500 }}>Chunk {index}</TableCell>

    <TableCell sx={{ 
      color: chunk.preds_per_model.svm === 'ai' ? '#d32f2f' : '#2e7d32',
      fontWeight: 500
    }}>
      {chunk.preds_per_model.svm.toUpperCase()}
    </TableCell>

    <TableCell sx={{ 
      color: chunk.preds_per_model.rf === 'ai' ? '#d32f2f' : '#2e7d32',
      fontWeight: 500
    }}>
      {chunk.preds_per_model.rf.toUpperCase()}
    </TableCell>

    <TableCell sx={{ 
      color: chunk.preds_per_model.xgboost === 'ai' ? '#d32f2f' : '#2e7d32',
      fontWeight: 500
    }}>
      {chunk.preds_per_model.xgboost.toUpperCase()}
    </TableCell>

    <TableCell sx={{ 
      color: chunk.preds_per_model.mlp === 'ai' ? '#d32f2f' : '#2e7d32',
      fontWeight: 500
    }}>
      {chunk.preds_per_model.mlp.toUpperCase()}
    </TableCell>

    <TableCell sx={{ 
      color: chunk.preds_per_model.early_stopping_mlp === 'ai' ? '#d32f2f' : '#2e7d32',
      fontWeight: 500
    }}>
      {chunk.preds_per_model.early_stopping_mlp.toUpperCase()}
    </TableCell>

    <TableCell sx={{ 
      color: chunk.preds_per_model.cnn === 'ai' ? '#d32f2f' : '#2e7d32',
      fontWeight: 500
    }}>
      {chunk.preds_per_model.cnn.toUpperCase()}
    </TableCell>

    <TableCell sx={{ 
      color: chunk.preds_per_model.early_stopping_cnn === 'ai' ? '#d32f2f' : '#2e7d32',
      fontWeight: 500
    }}>
      {chunk.preds_per_model.early_stopping_cnn.toUpperCase()}
    </TableCell>

    <TableCell sx={{ 
      color: chunk.chunk_majority === 'ai' ? '#d32f2f' : '#2e7d32',
      fontWeight: 700
    }}>
      {chunk.chunk_majority.toUpperCase()}
    </TableCell>
  </TableRow>
))}

                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>

              <Box>
                <Typography variant="h6" sx={{ mb: 2, color: '#1a237e', fontWeight: 500 }}>
                  Model-wise Majority (Across Chunks)
                </Typography>
                <TableContainer component={Paper} sx={{ boxShadow: 1 }}>
                  <Table size="small" sx={tableStyles}>
                    <TableHead>
                      <TableRow>
                        <TableCell>SVM</TableCell>
                        <TableCell>RF</TableCell>
                        <TableCell>XGBOOST</TableCell>
                        <TableCell>MLP</TableCell>
                        <TableCell>EARLY_STOPPING_MLP</TableCell>
                        <TableCell>CNN</TableCell>
                        <TableCell>EARLY_STOPPING_CNN</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        {Object.entries(predictions.model_predictions).map(([model, prediction]) => (
                          <TableCell key={model} sx={{ 
                            color: prediction === 'ai' ? '#d32f2f' : '#2e7d32',
                            fontWeight: 700
                          }}>
                            {prediction.toUpperCase()}
                          </TableCell>
                        ))}
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>

              <Box sx={{ mt: 4, textAlign: 'center' }}>
                <Typography variant="h6" sx={{ mb: 3, color: '#1a237e', fontWeight: 500 }}>
                  Final Decision
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4 }}>
                  <Paper sx={{ p: 2, minWidth: 200, textAlign: 'center', boxShadow: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Chunk-wise Final Decision
                    </Typography>
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        color: predictions.final_decision.chunk_majority === 'ai' ? '#d32f2f' : '#2e7d32',
                        fontWeight: 700
                      }}
                    >
                      {predictions.final_decision.chunk_majority.toUpperCase()}
                    </Typography>
                  </Paper>
                  <Paper sx={{ p: 2, minWidth: 200, textAlign: 'center', boxShadow: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Model-wise Final Decision
                    </Typography>
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        color: predictions.final_decision.model_majority === 'ai' ? '#d32f2f' : '#2e7d32',
                        fontWeight: 700
                      }}
                    >
                      {predictions.final_decision.model_majority.toUpperCase()}
                    </Typography>
                  </Paper>
                </Box>
              </Box>
            </Grid>

            {/* Reset Button */}
            <Grid item xs={12}>
              <Box sx={{ mt: 4, textAlign: 'center' }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleReset}
                  startIcon={<UploadIcon />}
                >
                  Analyze Another Song
                </Button>
              </Box>
            </Grid>
          </>
        )}

        {/* Error Display */}
        {error && (
          <Grid item xs={12}>
            <Alert 
              severity="error" 
              onClose={() => setError(null)}
            >
              {error}
            </Alert>
          </Grid>
        )}
      </Grid>
    </Box>
  </Box>
);
};

export default UploadManager;