import React, { useEffect, useState } from "react";
import { Box, Card, CardContent, Typography, Switch, List, ListItem, ListItemText, CircularProgress } from "@mui/material";
import api from "../services/apiClient";

export default function FeatureFlagPanel() {
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/api/v1/feature-flags");
      setFlags(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const toggle = async (key, enabled) => {
    await api.post(`/api/v1/feature-flags/${key}`, { enabled });
    load();
  };

  if (loading) return <CircularProgress />;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Feature Flags</Typography>
        <List>
          {flags.map((f) => (
            <ListItem key={f.key} secondaryAction={
              <Switch checked={f.enabled} onChange={(e) => toggle(f.key, e.target.checked)} />
            }>
              <ListItemText primary={f.key} secondary={f.description} />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
}
