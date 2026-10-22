import React, { useState } from "react";
import { Box, Card, CardContent, Typography, Button, Chip } from "@mui/material";
import api from "../services/apiClient";

export default function CacheInspector() {
  const [info, setInfo] = useState(null);

  const refresh = async () => {
    try {
      const { data } = await api.get("/api/v1/cache/stats");
      setInfo(data);
    } catch (e) {
      setInfo({ size: 0, max_size: 0, default_ttl: 0 });
    }
  };

  const clear = async () => {
    try { await api.post("/api/v1/cache/clear"); } catch (e) {}
    refresh();
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Cache</Typography>
        <Button variant="outlined" onClick={refresh} sx={{ mr: 1 }}>Refresh</Button>
        <Button variant="outlined" color="error" onClick={clear}>Clear</Button>
        {info && (
          <Box mt={2}>
            <Chip label={`Size: ${info.size}`} sx={{ mr: 1 }} />
            <Chip label={`Max: ${info.max_size}`} sx={{ mr: 1 }} />
            <Chip label={`TTL: ${info.default_ttl}s`} />
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
