import React, { useEffect, useState } from "react";
import { Box, Card, CardContent, Typography, Table, TableBody, TableCell, TableHead, TableRow, Chip } from "@mui/material";
import api from "../services/apiClient";

export default function ModelPerformance() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    api.get("/api/v1/models").then(({ data }) => setRows(data)).catch(() => setRows([]));
  }, []);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Model Performance</Typography>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Version</TableCell>
              <TableCell>Accuracy</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((m) => (
              <TableRow key={m.id}>
                <TableCell>{m.name}</TableCell>
                <TableCell>{m.version}</TableCell>
                <TableCell>{m.accuracy || "n/a"}</TableCell>
                <TableCell><Chip size="small" label={m.is_active ? "active" : "inactive"} color={m.is_active ? "success" : "default"} /></TableCell>
              </TableRow>
            ))}
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={4}>No models registered</TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
