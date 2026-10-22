import React, { useEffect, useState } from "react";
import { Box, Card, CardContent, Typography, CircularProgress } from "@mui/material";
import api from "../services/apiClient";

export default function MetricsDashboard() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/metrics")
      .then((r) => r.text())
      .then(setText)
      .catch(() => setText("unavailable"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Metrics</Typography>
        <Box component="pre" sx={{ fontSize: 12, overflow: "auto", maxHeight: 300, bgcolor: "#f5f5f5", p: 1 }}>
          {text}
        </Box>
      </CardContent>
    </Card>
  );
}
