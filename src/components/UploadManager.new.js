import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Chip,
  Fade,
  Alert,
  IconButton,
  Zoom,
  Slide,
  LinearProgress,
} from '@mui/material';
import axios from 'axios';
import {
  CloudUpload as UploadIcon,
  MusicNote as MusicIcon,
  Analytics as AnalyticsIcon,
  Audiotrack as AudioIcon,
  BarChart as ChartIcon,
  TimelineOutlined as TimelineIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';

const UploadManager = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [predictions, setPredictions] = useState(null);
  const [error, setError] = useState(null);
  const BASE_URL = "http://127.0.0.1:8000";

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      if (file.type !== 'audio/mpeg') {
        setError('Please upload only MP3 files');
        return;
      }
      setError(null);
      setUploading(true);
      setUploadedFile(file);

      try {
        setActiveStep(1);
        const formData = new FormData();
        formData.append("file", file);
        const response = await axios.post(`${BASE_URL}/prediction`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        const data = response.data;
        console.log("Prediction response:", data);
        
        const prediction = {
          chunkPrediction: data.chunk_predictions || [],
          final_decision: {
            model_majority: data.final_decision?.model_majority,
            chunk_majority: data.final_decision?.chunk_majority,
            model_predictions: data.model_predictions || {}
          }
        };
        
        console.log("Structured predictions:", prediction);
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

  const renderUploadArea = () => (
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
  );

  const renderProcessing = () => (
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
  );

  const renderResults = () => (
    <Grid item xs={12}>
      <Grid container spacing={4}>
        {/* Chunk-wise Predictions */}
        <Grid item xs={12} md={6}>
          <Slide direction="right" in timeout={800}>
            <Card 
              elevation={8}
              sx={{
                background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
                height: '100%',
              }}
            >
              <CardContent sx={{ height: '100%', p: 3 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    mb: 4,
                    color: 'white',
                  }}
                >
                  <TimelineIcon sx={{ fontSize: 28, mr: 1 }} />
                  <Typography variant="h5" fontWeight={500}>
                    Chunk-wise Predictions
                  </Typography>
                </Box>
                
                <Paper 
                  elevation={4}
                  sx={{
                    background: 'rgba(255, 255, 255, 0.95)',
                    borderRadius: 2,
                    overflow: 'hidden'
                  }}
                >
                  {/* Table Header */}
                  <Box 
                    sx={{
                      display: 'grid',
                      gridTemplateColumns: '100px repeat(8, 1fr)',
                      borderBottom: '2px solid rgba(0, 0, 0, 0.1)',
                      bgcolor: 'rgba(0, 0, 0, 0.03)',
                    }}
                  >
                    {['Chunk', 'SVM', 'RF', 'XGBOOST', 'MLP', 'EARLY_MLP', 'CNN', 'EARLY_CNN', 'Majority'].map((header) => (
                      <Box
                        key={header}
                        sx={{
                          p: 1.5,
                          textAlign: 'center',
                          fontWeight: 600,
                          fontSize: '0.75rem',
                          borderRight: '1px solid rgba(0, 0, 0, 0.1)',
                          '&:last-child': {
                            borderRight: 'none'
                          }
                        }}
                      >
                        {header}
                      </Box>
                    ))}
                  </Box>

                  {/* Table Body */}
                  <Box sx={{ maxHeight: '500px', overflow: 'auto' }}>
                    {predictions.chunkPrediction.map((chunk, index) => (
                      <Fade in timeout={300} key={index}>
                        <Box 
                          sx={{
                            display: 'grid',
                            gridTemplateColumns: '100px repeat(8, 1fr)',
                            borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
                            '&:hover': {
                              bgcolor: 'rgba(0, 0, 0, 0.02)',
                            },
                            transition: 'background-color 0.2s ease'
                          }}
                        >
                          <Box
                            sx={{
                              p: 1.5,
                              textAlign: 'center',
                              fontWeight: 500,
                              borderRight: '1px solid rgba(0, 0, 0, 0.1)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center'
                            }}
                          >
                            {index + 1}
                          </Box>
                          {chunk.preds_per_model && [
                            chunk.preds_per_model.svm,
                            chunk.preds_per_model.rf,
                            chunk.preds_per_model.xgboost,
                            chunk.preds_per_model.mlp,
                            chunk.preds_per_model.early_stopping_mlp,
                            chunk.preds_per_model.cnn,
                            chunk.preds_per_model.early_stopping_cnn,
                            chunk.chunk_majority
                          ].map((prediction, idx) => (
                            <Box
                              key={idx}
                              sx={{
                                p: 1.5,
                                textAlign: 'center',
                                borderRight: '1px solid rgba(0, 0, 0, 0.1)',
                                '&:last-child': {
                                  borderRight: 'none'
                                },
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                              }}
                            >
                              <Chip
                                label={prediction || 'N/A'}
                                size="small"
                                color={prediction === 'AI' ? 'error' : 'success'}
                                variant={idx === 7 ? 'filled' : 'outlined'}
                                sx={{ 
                                  minWidth: 60,
                                  fontSize: '0.75rem',
                                  fontWeight: idx === 7 ? 600 : 400,
                                  textTransform: 'uppercase'
                                }}
                              />
                            </Box>
                          ))}
                        </Box>
                      </Fade>
                    ))}
                  </Box>
                </Paper>
              </CardContent>
            </Card>
          </Slide>
        </Grid>

        {/* Model-wise Predictions */}
        <Grid item xs={12} md={6}>
          <Slide direction="left" in timeout={800}>
            <Card 
              elevation={8}
              sx={{
                background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
                height: '100%',
                position: 'relative',
              }}
            >
              <CardContent sx={{ height: '100%' }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    mb: 3,
                    color: 'white',
                  }}
                >
                  <ChartIcon sx={{ fontSize: 28, mr: 1 }} />
                  <Typography variant="h5" fontWeight={500}>
                    Model Predictions
                  </Typography>
                </Box>
                <Box sx={{ mt: 3 }}>
                  <Fade in timeout={500}>
                    <Paper 
                      elevation={4}
                      sx={{ 
                        p: 3,
                        mb: 3,
                        background: 'rgba(255, 255, 255, 0.95)',
                        backdropFilter: 'blur(10px)',
                        borderRadius: 2,
                      }}
                    >
                      <Typography variant="h6" gutterBottom>
                        Final Decision
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Box sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Model Majority
                            </Typography>
                            <Chip
                              label={predictions?.final_decision?.model_majority || 'N/A'}
                              color={predictions?.final_decision?.model_majority === 'AI' ? 'error' : 'success'}
                              sx={{ 
                                fontWeight: 600,
                                px: 3,
                                py: 2,
                                fontSize: '1.1rem',
                                textTransform: 'uppercase'
                              }}
                            />
                          </Box>
                        </Grid>
                        <Grid item xs={6}>
                          <Box sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Chunk Majority
                            </Typography>
                            <Chip
                              label={predictions?.final_decision?.chunk_majority || 'N/A'}
                              color={predictions?.final_decision?.chunk_majority === 'AI' ? 'error' : 'success'}
                              sx={{ 
                                fontWeight: 600,
                                px: 3,
                                py: 2,
                                fontSize: '1.1rem',
                                textTransform: 'uppercase'
                              }}
                            />
                          </Box>
                        </Grid>
                      </Grid>
                    </Paper>
                  </Fade>

                  <Typography variant="h6" sx={{ mb: 2, color: 'white' }}>
                    Individual Model Predictions
                  </Typography>
                  
                  {predictions?.final_decision?.model_predictions && Object.entries(predictions.final_decision.model_predictions).map(([model, prediction], index) => (
                    <Fade in timeout={500 * (index + 1)} key={model}>
                      <Paper 
                        elevation={4}
                        sx={{ 
                          p: 2.5, 
                          mb: 2,
                          background: 'rgba(255, 255, 255, 0.95)',
                          backdropFilter: 'blur(10px)',
                          borderRadius: 2,
                          transition: 'transform 0.2s ease',
                          '&:hover': {
                            transform: 'translateX(-8px)',
                          }
                        }}
                      >
                        <Grid container alignItems="center" spacing={2}>
                          <Grid item xs={6}>
                            <Typography variant="subtitle1" fontWeight={600}>
                              {model.toUpperCase()}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Chip
                              label={prediction}
                              color={prediction === 'AI' ? 'error' : 'success'}
                              sx={{ 
                                fontWeight: 600,
                                px: 2,
                                textTransform: 'uppercase'
                              }}
                            />
                          </Grid>
                        </Grid>
                      </Paper>
                    </Fade>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Slide>
        </Grid>

        {/* Reset Button */}
        <Grid item xs={12}>
          <Box sx={{ mt: 6, mb: 2, textAlign: 'center' }}>
            <Fade in timeout={1500}>
              <Card
                elevation={4}
                sx={{
                  background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
                  p: 3,
                  maxWidth: 400,
                  mx: 'auto'
                }}
              >
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={handleReset}
                  startIcon={<UploadIcon />}
                  sx={{
                    py: 1.5,
                    bgcolor: 'rgba(255, 255, 255, 0.9)',
                    color: '#1a237e',
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    '&:hover': {
                      bgcolor: 'rgba(255, 255, 255, 1)',
                      transform: 'scale(1.02)',
                      transition: 'all 0.2s ease',
                    }
                  }}
                >
                  Analyze Another Song
                </Button>
              </Card>
            </Fade>
          </Box>
        </Grid>
      </Grid>
    </Grid>
  );

  return (
    <Box sx={{ p: 4, minHeight: '80vh' }}>
      <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
        <Grid container spacing={4}>
          {activeStep === 0 && renderUploadArea()}
          {activeStep === 1 && renderProcessing()}
          {activeStep === 2 && predictions && renderResults()}
          
          {/* Error Display */}
          {error && (
            <Grid item xs={12}>
              <Zoom in>
                <Alert 
                  severity="error" 
                  onClose={() => setError(null)}
                  sx={{
                    borderRadius: 2,
                    '& .MuiAlert-icon': {
                      fontSize: '2rem'
                    }
                  }}
                >
                  <Typography variant="subtitle1" fontWeight={500}>
                    {error}
                  </Typography>
                </Alert>
              </Zoom>
            </Grid>
          )}
        </Grid>
      </Box>
    </Box>
  );
};

export default UploadManager;