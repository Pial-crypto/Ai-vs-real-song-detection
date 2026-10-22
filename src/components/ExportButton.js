import React, { useState } from "react";
import { Button, CircularProgress } from "@mui/material";
import { Download } from "@mui/icons-material";
import api from "../services/apiClient";

export default function ExportButton() {
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      const { data } = await api.post("/api/v1/export?fmt=json");
      await api.post(`/api/v1/export/${data.id}/complete?file_path=/tmp/export_${data.id}.json`);
      alert("Export completed");
    } catch (e) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button variant="outlined" startIcon={loading ? <CircularProgress size={16} /> : <Download />} onClick={handleExport} disabled={loading}>
      Export Data
    </Button>
  );
}
