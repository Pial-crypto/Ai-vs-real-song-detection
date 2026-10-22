import React, { useState } from "react";
import { Box, Card, CardContent, Typography, Button, LinearProgress, Chip } from "@mui/material";
import api from "../services/apiClient";

export default function BatchUploader() {
  const [job, setJob] = useState(null);
  const [creating, setCreating] = useState(false);

  const createJob = async () => {
    setCreating(true);
    try {
      const { data } = await api.post("/api/v1/batch?total_files=5");
      setJob(data);
    } finally {
      setCreating(false);
    }
  };

  const progress = job ? (job.processed_files / job.total_files) * 100 : 0;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Batch Prediction</Typography>
        <Button variant="contained" onClick={createJob} disabled={creating}>
          {creating ? "Creating..." : "New Batch Job"}
        </Button>
        {job && (
          <Box mt={2}>
            <Chip label={`Status: ${job.status}`} sx={{ mb: 1 }} />
            <LinearProgress variant="determinate" value={progress} />
            <Typography variant="body2" sx={{ mt: 1 }}>
              {job.processed_files} / {job.total_files} processed
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
