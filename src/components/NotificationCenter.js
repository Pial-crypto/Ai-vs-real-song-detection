import React, { useEffect, useState } from "react";
import { Badge, IconButton, Menu, MenuItem, Typography, Box } from "@mui/material";
import { Notifications as NotificationsIcon } from "@mui/icons-material";
import api from "../services/apiClient";

export default function NotificationCenter() {
  const [anchor, setAnchor] = useState(null);
  const [items, setItems] = useState([]);

  const load = async () => {
    try {
      const { data } = await api.get("/api/v1/notifications");
      setItems(data);
    } catch (e) {}
  };

  useEffect(() => { load(); const t = setInterval(load, 30000); return () => clearInterval(t); }, []);

  const unread = items.filter((i) => !i.read).length;

  return (
    <>
      <IconButton color="inherit" onClick={(e) => setAnchor(e.currentTarget)}>
        <Badge badgeContent={unread} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>
      <Menu anchorEl={anchor} open={Boolean(anchor)} onClose={() => setAnchor(null)}>
        {items.length === 0 && <MenuItem disabled>No notifications</MenuItem>}
        {items.slice(0, 10).map((n) => (
          <MenuItem key={n.id} onClick={() => setAnchor(null)}>
            <Box>
              <Typography variant="subtitle2">{n.title}</Typography>
              <Typography variant="caption">{n.message}</Typography>
            </Box>
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}
