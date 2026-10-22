import React, { useEffect, useState } from "react";
import { Box, Card, CardContent, TextField, Button, Typography, Avatar } from "@mui/material";
import api from "../services/apiClient";

export default function ProfileEditor() {
  const [profile, setProfile] = useState({ display_name: "", bio: "", avatar_url: "", preferences: {} });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get("/api/v1/profiles/me").then(({ data }) => setProfile(data)).catch(() => {});
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      const { data } = await api.put("/api/v1/profiles/me", profile);
      setProfile(data);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Avatar src={profile.avatar_url} />
          <Typography variant="h6">Edit Profile</Typography>
        </Box>
        <TextField fullWidth label="Display name" value={profile.display_name || ""} onChange={(e) => setProfile({ ...profile, display_name: e.target.value })} margin="normal" />
        <TextField fullWidth label="Avatar URL" value={profile.avatar_url || ""} onChange={(e) => setProfile({ ...profile, avatar_url: e.target.value })} margin="normal" />
        <TextField fullWidth multiline rows={3} label="Bio" value={profile.bio || ""} onChange={(e) => setProfile({ ...profile, bio: e.target.value })} margin="normal" />
        <Button variant="contained" onClick={save} disabled={saving} sx={{ mt: 2 }}>
          {saving ? "Saving..." : "Save"}
        </Button>
      </CardContent>
    </Card>
  );
}
