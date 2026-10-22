import React, { useEffect, useState } from "react";
import { Box, Card, CardContent, Typography, Table, TableBody, TableCell, TableHead, TableRow, Button, TextField, CircularProgress } from "@mui/material";
import api from "../services/apiClient";

export default function WebhookManager() {
  const [hooks, setHooks] = useState([]);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(true);

  const load = () => api.get("/api/v1/webhooks").then(({ data }) => setHooks(data)).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const register = async () => {
    if (!url) return;
    await api.post("/api/v1/webhooks", { url, events: [] });
    setUrl("");
    load();
  };

  if (loading) return <CircularProgress />;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Webhooks</Typography>
        <Box display="flex" gap={1} mb={2}>
          <TextField size="small" fullWidth label="URL" value={url} onChange={(e) => setUrl(e.target.value)} />
          <Button variant="contained" onClick={register}>Add</Button>
        </Box>
        <Table size="small">
          <TableHead><TableRow><TableCell>URL</TableCell><TableCell>Active</TableCell><TableCell>Failures</TableCell></TableRow></TableHead>
          <TableBody>
            {hooks.map((h) => (
              <TableRow key={h.id}>
                <TableCell>{h.url}</TableCell>
                <TableCell>{h.active ? "yes" : "no"}</TableCell>
                <TableCell>{h.failure_count}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
