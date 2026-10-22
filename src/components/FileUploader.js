import React, { useState } from "react";
import { Box, Card, CardContent, Typography, Button, LinearProgress, Alert } from "@mui/material";
import { CloudUpload } from "@mui/icons-material";
import api from "../services/apiClient";

export default function FileUploader() {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const upload = async () => {
    if (!file) return;
    setError(null);
    setResult(null);
    setProgress(0);
    try {
      const { data } = await api.post("/api/v1/files", { name: file.name });
      setResult(data);
      setProgress(100);
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>File Upload</Typography>
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <Box mt={2}>
          <Button variant="contained" startIcon={<CloudUpload />} onClick={upload} disabled={!file}>
            Upload
          </Button>
        </Box>
        {progress > 0 && <LinearProgress variant="determinate" value={progress} sx={{ mt: 2 }} />}
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {result && <Alert severity="success" sx={{ mt: 2 }}>Uploaded: {result.id}</Alert>}
      </CardContent>
    </Card>
  );
}
