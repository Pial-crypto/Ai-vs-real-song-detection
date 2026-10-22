import React, { useState } from "react";
import { Box, TextField, Button, List, ListItem, ListItemText, Typography } from "@mui/material";
import { Search } from "@mui/icons-material";
import api from "../services/apiClient";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const search = async () => {
    try {
      const { data } = await api.get(`/api/v1/search/predictions?q=${encodeURIComponent(query)}`);
      setResults(data.results || []);
    } catch (e) {
      setResults([]);
    }
  };

  return (
    <Box>
      <Box display="flex" gap={1} mb={2}>
        <TextField fullWidth size="small" label="Search predictions" value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === "Enter" && search()} />
        <Button variant="contained" onClick={search}><Search /></Button>
      </Box>
      <List>
        {results.map((r) => (
          <ListItem key={r.id}>
            <ListItemText primary={r.file_name} secondary={`ID: ${r.id}`} />
          </ListItem>
        ))}
        {results.length === 0 && query && <Typography color="text.secondary">No results</Typography>}
      </List>
    </Box>
  );
}
