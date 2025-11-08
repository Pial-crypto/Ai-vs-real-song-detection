import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Container,
  Link,
  useTheme,
  useMediaQuery,
  CircularProgress,
  Alert,
  Collapse,

} from '@mui/material';
import { motion } from 'framer-motion';
import { MusicNote as MusicIcon } from '@mui/icons-material';
import { handleSignUp, handleSignIn } from '../functions/handleAuth';
import { saveToLocal } from '../functions/localStorage';
const Login = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      if (isLogin) {
     
        // Handle Sign In
        const userData = await handleSignIn(formData);
        saveToLocal('user', userData);
        const roleText = userData.role === 'admin' ? 'Administrator' : 'User';
        setSuccess(`Sign in successful! Welcome back, ${roleText}!`);
        setTimeout(() => onLogin(userData.role), 1000); // Pass the role from response
      } else {

           if(formData.email === '' || formData.password === ''){
          setError('Please fill in all fields.');
          setLoading(false);
          return;
        }
        if(formData.password.length < 6){
          setError('Password must be at least 6 characters long.');
          setLoading(false);
          return;
        }

        if(formData.email === 'p03734027@gmail.com'){
          setError('This email is reserved for admin.');
          setLoading(false);
          return;
        }
        // Only allow user registration, not admin
        const userData = await handleSignUp(formData);

        setSuccess('Account created successfully! Welcome!');
        setTimeout(() => onLogin('user'), 1000);
      }
    } catch (err) {
      setError(err.message);
      console.error('Auth error:', err);
    } finally {
      setLoading(false);
    }
  };
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));


  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <Container maxWidth="sm">
      <Paper
        component={motion.div}
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        elevation={3}
        sx={{
          width: '100%',
          p: isMobile ? 2 : 4,
          borderRadius: 2,
        }}
      >
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <MusicIcon sx={{ fontSize: 48, color: 'secondary.main', mb: 2 }} />
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            AI Song Detector
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {isLogin ? 'Sign in to continue' : 'Create your account'}
          </Typography>
        </Box>

        <Collapse in={!!error}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        </Collapse>

        <Collapse in={!!success}>
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        </Collapse>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <TextField
              fullWidth
              name="username"
              label="Username"
              variant="outlined"
              value={formData.username}
              onChange={handleChange}
              required
              sx={{ mb: 2 }}
            />
          )}
          
          <TextField
            fullWidth
            name="email"
            label="Email"
            type="email"
            variant="outlined"
            value={formData.email}
            onChange={handleChange}
            required
            sx={{ mb: 2 }}
          />
          
          <TextField
            fullWidth
            name="password"
            label="Password"
            type="password"
            variant="outlined"
            value={formData.password}
            onChange={handleChange}
            required
            sx={{ mb: 3 }}
          />
          
          <Button
            fullWidth
            size="large"
            variant="contained"
            type="submit"
            disabled={loading}
            sx={{
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 600,
              background: 'linear-gradient(45deg, #00B894 30%, #2D3436 90%)',
              color: 'white',
              '&:hover': {
                background: 'linear-gradient(45deg, #00B894 10%, #2D3436 70%)',
              },
            }}
          >
            {loading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              isLogin ? 'Sign In' : 'Create Account'
            )}
          </Button>

          <Box sx={{ textAlign: 'center', mt: 3 }}>
            <Typography variant="body2" color="text.secondary">
              {isLogin ? "Don't have an account? " : 'Already have an account? '}
              <Link
                component="button"
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                sx={{ fontWeight: 600, textDecoration: 'none' }}
              >
                {isLogin ? 'Sign Up' : 'Sign In'}
              </Link>
            </Typography>
          </Box>
        </form>
      </Paper>
    </Container>
  );
};

export default Login;