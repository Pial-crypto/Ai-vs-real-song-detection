import React, { useEffect, useState } from "react";
import { Box, Card, CardContent, Typography, List, ListItem, ListItemText, Chip, CircularProgress } from "@mui/material";
import api from "../services/apiClient";

export default function ModelRegistry() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Admin-only endpoint; ignore errors for non-admins
    api.get("/api/v1/models").then(({ data }) => setModels(data)).catch(() => setModels([])).finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Model Registry</Typography>
        <List>
          {models.map((m) => (
            <ListItem key={m.id}>
              <ListItemText primary={`${m.name} v${m.version}`} secondary={`accuracy: ${m.accuracy || "n/a"}`} />
              <Chip size="small" label={m.is_active ? "active" : "inactive"} color={m.is_active ? "success" : "default"} />
            </ListItem>
          ))}
          {models.length === 0 && <Typography color="text.secondary">No models registered</Typography>}
        </List>
      </CardContent>
    </Card>
  );
}
