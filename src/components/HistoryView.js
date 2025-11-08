import React, { useState } from 'react';
import {
  Typography,
  Box,
  Modal,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TextField,
  MenuItem,
  Button,
  Stack,
  Paper,
  Divider,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  useTheme,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Delete as DeleteIcon,
  Close as CloseIcon,
  X,
} from '@mui/icons-material';
import { getPredictionHistory } from '../functions/getPredictionHistory';
import { getFromLocal } from '../functions/localStorage';
import { delPrediction } from '../functions/deletePrediction';



const tableStyles = {
  '& .MuiTableCell-root': {
    padding: '12px 16px',
    fontSize: '14px',
    whiteSpace: 'nowrap',
    borderColor: '#e0e0e0'
  },
  '& .MuiTableHead-root th': {
    backgroundColor: '#f8f9fa',
    fontWeight: 600,
    color: '#1a237e',
    borderBottom: '2px solid #e0e0e0',
    position: 'sticky',
    top: 0,
    zIndex: 1
  },
  '& .MuiTableRow-root:hover': {
    backgroundColor: 'rgba(0, 0, 0, 0.04)'
  },
  '& .MuiChip-root': {
    fontWeight: 500
  },
  '& .MuiTableContainer-root': {
    borderRadius: 2,
    border: '1px solid #e0e0e0',
    '&::-webkit-scrollbar': {
      width: '8px',
      height: '8px'
    },
    '&::-webkit-scrollbar-track': {
      background: '#f1f1f1',
      borderRadius: '4px'
    },
    '&::-webkit-scrollbar-thumb': {
      background: '#888',
      borderRadius: '4px',
      '&:hover': {
        background: '#666'
      }
    }
  }
};

const modalStyle = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: '95%',
  maxWidth: 1400,
  maxHeight: '90vh',
  bgcolor: 'background.paper',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
  borderRadius: 2,
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column'
};

const modalContentStyle = {
  flexGrow: 1,
  overflowY: 'auto',
  backgroundColor: '#fff',
  padding: '0',
  '&::-webkit-scrollbar': {
    width: '8px',
    height: '8px'
  },
  '&::-webkit-scrollbar-track': {
    background: '#f1f1f1',
    borderRadius: '4px'
  },
  '&::-webkit-scrollbar-thumb': {
    background: '#888',
    borderRadius: '4px',
    '&:hover': {
      background: '#666'
    }
  }
};

const HistoryView = () => {

  const theme = useTheme();
  const [searchTerm, setSearchTerm] = useState('');
  const [resultFilter, setResultFilter] = useState('all');
  const [selectedSong, setSelectedSong] = useState(null);
  const [openModal, setOpenModal] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [songToDelete, setSongToDelete] = useState(null);
  const userId = getFromLocal('user')?.id;
  const [history, setHistory] = useState([]);
  const models = ['CNN','Early Stopping CNN', 'Early Stopping MLP', 'MLP','Random Forest', 'SVM','XGBoost'];

     
useState(() => {  
    getPredictionHistory(userId).then(data => {
    setHistory(data);
    console.log(data);
  }).catch(err => {
    console.error(err);
  });
},[])

  const handleOpenDetails = (song) => {
    setSelectedSong(song);
    setOpenModal(true);
  };

  console.log(selectedSong,"The selected song");

  const handleCloseDetails = () => {
    setOpenModal(false);
    setSelectedSong(null);
  };

  const handleOpenDeleteDialog = (song) => {
    setSongToDelete(song);
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setSongToDelete(null);
  };

  const handleDelete = () => {
    // TODO: Add actual delete API call here
    setHistory(prevHistory => prevHistory.filter(item => item !== songToDelete));
    delPrediction(songToDelete.id).then(() => {
      console.log("Deletion successful");
    }).catch(err => {
      console.error("Deletion failed:", err);
    });
    handleCloseDeleteDialog();
  };

  const filteredHistory = history.filter((item) => {
    const matchesSearch = item.fileName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.fileName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = resultFilter === 'all' || 
                         item.finalPrediction.chunk_majority.toLowerCase() === resultFilter.toLowerCase();
    return matchesSearch && matchesFilter;
  });

  return (
    <Box 
      sx={{
        maxWidth: 1400,
        margin: '0 auto',
        p: 3,
        minHeight: '100vh',
        backgroundColor: '#f8f9fa'
      }}
    >
      <Paper 
        elevation={0}
        sx={{ 
          p: 3, 
          mb: 3, 
          borderRadius: 2,
          backgroundColor: 'white',
          borderBottom: '1px solid #e0e0e0'
        }}
      >
        <Typography 
          variant="h4" 
          gutterBottom
          sx={{ 
            fontWeight: 600,
            color: '#1a237e',
            mb: 3
          }}
        >
          Analysis History
        </Typography>

        {/* Search and Filter Section */}
        <Box 
          sx={{
            display: 'flex',
            gap: 2,
            alignItems: 'center',
            flexWrap: 'wrap'
          }}
        >
          <TextField
            label="Search by name or file"
            variant="outlined"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            size="small"
            sx={{ 
              minWidth: { xs: '100%', sm: 250 },
              '& .MuiOutlinedInput-root': {
                backgroundColor: '#fff'
              }
            }}
          />

          <FormControl 
            variant="outlined" 
            size="small" 
            sx={{ 
              minWidth: { xs: '100%', sm: 200 }
            }}
          >
            <InputLabel>Filter by Result</InputLabel>
            <Select
              value={resultFilter}
              onChange={(e) => setResultFilter(e.target.value)}
              label="Filter by Result"
            >
              <MenuItem value="all">All Results</MenuItem>
              <MenuItem value="ai">AI Generated</MenuItem>
              <MenuItem value="real">Real Recording</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Paper>

      {/* Results Table */}
      <TableContainer component={Paper} sx={{ mb: 3 }}>
        <Table sx={tableStyles}>
          <TableHead>
            <TableRow>
              <TableCell>File Name</TableCell>
              
              <TableCell>Chunks Analyzed</TableCell>
              <TableCell>Models Used</TableCell>
              <TableCell>Final Result By Model</TableCell>
              <TableCell>Final Result By Chunk</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredHistory.map((item, index) => (
              <TableRow key={index}>
                <TableCell>{item.fileName}</TableCell>
                
                <TableCell>{item.chunkWisePrediction.length} chunks</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1}>
                    {models.map((model, idx) => (
                      <Chip
                        key={idx}
                        label={model}
                        size="small"
                        color="default"
                        variant="outlined"
                      />
                    ))}
                  </Stack>
                </TableCell>
                <TableCell>
                  <Chip
                    label={item.finalPrediction.model_majority}
                    color={item.finalPrediction.model_majority.toLowerCase() === 'ai' ? 'error' : 'success'}
                    size="small"
                  />
                </TableCell>

                      <TableCell>
                  <Chip
                    label={item.finalPrediction.chunk_majority}
                    color={item.finalPrediction.chunk_majority.toLowerCase() === 'ai' ? 'error' : 'success'}
                    size="small"
                  />
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="View Details">
                    <IconButton 
                      onClick={() => handleOpenDetails(item)}
                      color="primary"
                      size="small"
                    >
                      <VisibilityIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton 
                      onClick={() => handleOpenDeleteDialog(item)}
                      color="error"
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title" sx={{ color: '#d32f2f' }}>
          Confirm Deletion
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete the analysis for "{songToDelete?.fileName}"? 
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ p: 2, backgroundColor: '#f8f9fa' }}>
          <Button
            onClick={handleCloseDeleteDialog}
            variant="outlined"
            sx={{ 
              color: 'text.secondary',
              borderColor: 'text.secondary',
              '&:hover': {
                borderColor: 'text.primary',
              }
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDelete}
            variant="contained"
            color="error"
            startIcon={<DeleteIcon />}
            sx={{ ml: 2 }}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Detail View Modal */}
      <Modal
        open={openModal}
        onClose={handleCloseDetails}
        aria-labelledby="song-detail-modal"
        BackdropProps={{
          style: { backgroundColor: 'rgba(0, 0, 0, 0.8)' }
        }}
      >
        <Box sx={modalStyle}>
          {selectedSong && (
            <>
              <Box sx={{
                p: 3,
                borderBottom: '1px solid #e0e0e0',
                backgroundColor: '#f8f9fa',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <Typography
                  variant="h5"
                  component="h2"
                  sx={{
                    fontWeight: 600,
                    color: '#1a237e'
                  }}
                >
                  Analysis Details: {selectedSong.fileName}
                </Typography>
                <IconButton
                  onClick={handleCloseDetails}
                  size="small"
                  sx={{
                    color: '#666',
                    '&:hover': {
                      backgroundColor: 'rgba(0, 0, 0, 0.04)'
                    }
                  }}
                >
                  <CloseIcon />
                </IconButton>
              </Box>

              <Box sx={modalContentStyle}>
                <Box sx={{ p: 3 }}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      mb: 4,
                      backgroundColor: '#f8f9fa',
                      border: '1px solid #e0e0e0',
                      borderRadius: 2
                    }}
                  >
                    <Typography
                      variant="h6"
                      sx={{
                        mb: 3,
                        fontWeight: 600,
                        color: '#2c387e'
                      }}
                    >
                      Chunk Analysis Results
                    </Typography>
              
                    <TableContainer 
                      sx={{
                        maxHeight: 400,
                        overflowY: 'auto',
                        overflowX: 'auto',
                        border: '1px solid #e0e0e0',
                        borderRadius: 1,
                        '&::-webkit-scrollbar': {
                          width: '8px',
                          height: '8px'
                        },
                        '&::-webkit-scrollbar-track': {
                          background: '#f1f1f1',
                          borderRadius: '4px'
                        },
                        '&::-webkit-scrollbar-thumb': {
                          background: '#888',
                          borderRadius: '4px',
                          '&:hover': {
                            background: '#666'
                          }
                        }
                      }}
                    >
                      <Table size="small" stickyHeader>
                        <TableHead>
                          <TableRow>
                            <TableCell sx={{ backgroundColor: '#f5f5f5', fontWeight: 600 }}>Chunk</TableCell>
                            <TableCell sx={{ backgroundColor: '#f5f5f5', fontWeight: 600 }}>Chunk Majority</TableCell>
                            {models.map((model, idx) => (
                              <TableCell 
                                key={idx} 
                                sx={{ 
                                  backgroundColor: '#f5f5f5', 
                                  fontWeight: 600,
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                {model}
                              </TableCell>
                            ))}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {selectedSong.chunkWisePrediction.map((chunk, idx) => (
                            <TableRow key={idx} hover>
                              <TableCell>Chunk {idx + 1}</TableCell>
                              <TableCell>
                                <Chip
                                  label={chunk.chunk_majority}
                                  size="small"
                                  color={chunk.chunk_majority.toLowerCase() === 'ai' ? 'error' : 'success'}
                                  sx={{ fontWeight: 500 }}
                                />
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={chunk?.preds_per_model?.cnn || 'N/A'}
                                  size="small"
                                  variant="outlined"
                                  color={chunk?.preds_per_model?.cnn?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                />
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={chunk?.preds_per_model?.early_stopping_cnn || 'N/A'}
                                  size="small"
                                  variant="outlined"
                                  color={chunk?.preds_per_model?.early_stopping_cnn?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                />
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={chunk?.preds_per_model?.early_stopping_mlp || 'N/A'}
                                  size="small"
                                  variant="outlined"
                                  color={chunk?.preds_per_model?.early_stopping_mlp?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                />
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={chunk?.preds_per_model?.mlp || 'N/A'}
                                  size="small"
                                  variant="outlined"
                                  color={chunk?.preds_per_model?.mlp?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                />
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={chunk?.preds_per_model?.rf || 'N/A'}
                                  size="small"
                                  variant="outlined"
                                  color={chunk?.preds_per_model?.rf?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                />
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={chunk?.preds_per_model?.svm || 'N/A'}
                                  size="small"
                                  variant="outlined"
                                  color={chunk?.preds_per_model?.svm?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                />
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={chunk?.preds_per_model?.xgboost || 'N/A'}
                                  size="small"
                                  variant="outlined"
                                  color={chunk?.preds_per_model?.xgboost?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                />
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Paper>

                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      mb: 4,
                      backgroundColor: '#f8f9fa',
                      border: '1px solid #e0e0e0',
                      borderRadius: 2
                    }}
                  >
                    <Typography
                      variant="h6"
                      sx={{
                        mb: 3,
                        fontWeight: 600,
                        color: '#2c387e'
                      }}
                    >
                      Model Analysis Results
                    </Typography>

                    <TableContainer
                      sx={{
                        border: '1px solid #e0e0e0',
                        borderRadius: 1,
                        overflowX: 'auto',
                        '&::-webkit-scrollbar': {
                          height: '8px'
                        },
                        '&::-webkit-scrollbar-track': {
                          background: '#f1f1f1'
                        },
                        '&::-webkit-scrollbar-thumb': {
                          background: '#888',
                          borderRadius: '4px',
                          '&:hover': {
                            background: '#666'
                          }
                        }
                      }}
                    >
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            {models.map((model, idx) => (
                              <TableCell
                                key={idx}
                                sx={{
                                  backgroundColor: '#f5f5f5',
                                  fontWeight: 600,
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                {model}
                              </TableCell>
                            ))}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          <TableRow hover>
                            <TableCell>
                              <Chip
                                label={selectedSong.modelWiseMajorityPrediction?.cnn || 'N/A'}
                                size="small"
                                color={selectedSong.modelWiseMajorityPrediction?.cnn?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                sx={{ fontWeight: 500 }}
                              />
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={selectedSong.modelWiseMajorityPrediction?.early_stopping_cnn || 'N/A'}
                                size="small"
                                color={selectedSong.modelWiseMajorityPrediction?.early_stopping_cnn?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                sx={{ fontWeight: 500 }}
                              />
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={selectedSong.modelWiseMajorityPrediction?.early_stopping_mlp || 'N/A'}
                                size="small"
                                color={selectedSong.modelWiseMajorityPrediction?.early_stopping_mlp?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                sx={{ fontWeight: 500 }}
                              />
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={selectedSong.modelWiseMajorityPrediction?.mlp || 'N/A'}
                                size="small"
                                color={selectedSong.modelWiseMajorityPrediction?.mlp?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                sx={{ fontWeight: 500 }}
                              />
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={selectedSong.modelWiseMajorityPrediction?.rf || 'N/A'}
                                size="small"
                                color={selectedSong.modelWiseMajorityPrediction?.rf?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                sx={{ fontWeight: 500 }}
                              />
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={selectedSong.modelWiseMajorityPrediction?.svm || 'N/A'}
                                size="small"
                                color={selectedSong.modelWiseMajorityPrediction?.svm?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                sx={{ fontWeight: 500 }}
                              />
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={selectedSong.modelWiseMajorityPrediction?.xgboost || 'N/A'}
                                size="small"
                                color={selectedSong.modelWiseMajorityPrediction?.xgboost?.toLowerCase() === 'ai' ? 'error' : 'success'}
                                sx={{ fontWeight: 500 }}
                              />
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Paper>

                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      backgroundColor: '#f8f9fa',
                      border: '1px solid #e0e0e0',
                      borderRadius: 2
                    }}
                  >
                    <Stack direction="row" spacing={4} alignItems="flex-start">
                      <Box>
                        <Typography
                          variant="subtitle2"
                          sx={{
                            mb: 1,
                            color: '#666',
                            fontWeight: 600
                          }}
                        >
                          Model Majority Result
                        </Typography>
                        <Chip
                          label={selectedSong.finalPrediction.model_majority}
                          color={selectedSong.finalPrediction.model_majority.toLowerCase() === 'ai' ? 'error' : 'success'}
                          sx={{ fontWeight: 500 }}
                        />
                      </Box>
                      <Box>
                        <Typography
                          variant="subtitle2"
                          sx={{
                            mb: 1,
                            color: '#666',
                            fontWeight: 600
                          }}
                        >
                          Chunk Majority Result
                        </Typography>
                        <Chip
                          label={selectedSong.finalPrediction.chunk_majority}
                          color={selectedSong.finalPrediction.chunk_majority.toLowerCase() === 'ai' ? 'error' : 'success'}
                          sx={{ fontWeight: 500 }}
                        />
                      </Box>
                    </Stack>
                  </Paper>
                </Box>
              </Box>
            </>
          )}
        </Box>
      </Modal>
    </Box>
  );
};

export default HistoryView;