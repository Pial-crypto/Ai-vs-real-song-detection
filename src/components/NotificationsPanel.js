import React, { useEffect, useState } from "react";
import {
  Box, Card, CardContent, Typography, List, ListItem, ListItemText,
  IconButton, Chip, Button, CircularProgress, Alert,
} from "@mui/material";
import { MarkEmailRead, Notifications as NotificationsIcon } from "@mui/icons-material";
import api from "../services/apiClient";

export default function NotificationsPanel() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get("/api/v1/notifications");
      setItems(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const markRead = async (id) => {
    try {
      await api.post(`/api/v1/notifications/${id}/read`);
      setItems((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
    } catch (e) {
      setError(e.message);
    }
  };

  const markAll = async () => {
    try {
      await api.post("/api/v1/notifications/read-all");
      setItems((prev) => prev.map((n) => ({ ...n, read: true })));
    } catch (e) {
      setError(e.message);
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            <NotificationsIcon sx={{ mr: 1, verticalAlign: "middle" }} />
            Notifications
          </Typography>
          <Button size="small" onClick={markAll}>Mark all read</Button>
        </Box>
        {items.length === 0 ? (
          <Typography color="text.secondary">No notifications</Typography>
        ) : (
          <List>
            {items.map((n) => (
              <ListItem
                key={n.id}
                secondaryAction={
                  !n.read && (
                    <IconButton edge="end" onClick={() => markRead(n.id)}>
                      <MarkEmailRead />
                    </IconButton>
                  )
                }
              >
                <ListItemText
                  primary={n.title}
                  secondary={n.message}
                />
                <Chip size="small" label={n.level} color={n.read ? "default" : "primary"} />
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
}
