import React, { useState } from "react";
import { Box, Card, CardContent, Typography, Button, Chip } from "@mui/material";
import api from "../services/apiClient";

export default function TaskQueueViewer() {
  const [stats, setStats] = useState(null);

  const refresh = async () => {
    try {
      const { data } = await api.get("/api/v1/tasks/stats");
      setStats(data);
    } catch (e) {
      setStats({ total: 0, pending: 0, completed: 0, failed: 0 });
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Task Queue</Typography>
        <Button variant="outlined" onClick={refresh} sx={{ mb: 2 }}>Refresh</Button>
        {stats && (
          <Box display="flex" gap={1} flexWrap="wrap">
            <Chip label={`Total: ${stats.total}`} />
            <Chip label={`Pending: ${stats.pending}`} color="warning" />
            <Chip label={`Completed: ${stats.completed}`} color="success" />
            <Chip label={`Failed: ${stats.failed}`} color="error" />
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
