import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LockOutlined as LockIcon,
  Email as EmailIcon,
  Lock as PasswordIcon,
  Visibility,
  VisibilityOff,
  Warning as WarningIcon,
  Person as PersonIcon,
  AccountBalanceWallet as WalletIcon
} from '@mui/icons-material';
import { isMetaMaskInstalled, connectMetaMask } from '../utils/metamask';
import { CircularProgress, TextField, InputAdornment, IconButton } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const Login = () => {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loginAttempts, setLoginAttempts] = useState(0);
  const [isBlocked, setIsBlocked] = useState(false);
  const [metamaskAvailable, setMetamaskAvailable] = useState(false);

  const BLOCK_DURATION_MS = 60 * 1000;

  useEffect(() => {
    setMetamaskAvailable(isMetaMaskInstalled());
    
    const isAuth = localStorage.getItem('isAuthenticated') === 'true';
    if (isAuth) {
      navigate('/dashboard');
    }
  }, [navigate]);

  useEffect(() => {
    let timer;
    if (isBlocked) {
      timer = setTimeout(() => {
        setIsBlocked(false);
        setLoginAttempts(0);
        setError(null);
      }, BLOCK_DURATION_MS);
    }
    return () => clearTimeout(timer);
  }, [isBlocked]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const validateForm = () => {
    setError(null);
    
    if (!isLogin && !formData.name) {
      setError('Name is required for registration');
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email || !emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }

    if (!formData.password || formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return false;
    }

    return true;
  };

  const handleLoginOrRegister = async (e) => {
    e.preventDefault();
    
    if (isBlocked || !validateForm()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      console.log(`--- SIMULATING ${isLogin ? 'LOGIN' : 'REGISTRATION'} ---`);
      console.log(`Email: ${formData.email}`);
      console.log(`Password: ${formData.password}`);

      const isCredentialsValid = () => {
          if (isLogin) {
              return formData.email === 'test@example.com' && formData.password === 'password';
          }
          return true;
      };

      await new Promise(resolve => setTimeout(resolve, 800));

      if (!isCredentialsValid()) {
        const attemptsLeft = 3 - (loginAttempts + 1);
        setLoginAttempts(prev => prev + 1);
        
        if (attemptsLeft <= 0) {
          setError('Incorrect credentials. Too many failed attempts. Please try again later.');
          setIsBlocked(true);
          console.warn(`--- SIMULATING SECURITY ALERT ---`);
          console.warn(`Would send security alert email to ${formData.email} due to multiple failed login attempts.`);
          console.warn(`(In a real app, this alert would be triggered by the backend)`);
          console.warn(`--- END SIMULATION ---`);
        } else {
          setError(`Incorrect email or password. ${attemptsLeft} attempts remaining.`);
        }
        throw new Error('Incorrect credentials');
      }
      
      setLoginAttempts(0);
      
      const userData = {
        name: isLogin ? (formData.email === 'test@example.com' ? 'Test User' : 'Logged In User') : formData.name,
        email: formData.email,
        role: 'User',
        lastLogin: new Date().toISOString()
      };
      
      localStorage.setItem('isAuthenticated', 'true');
      localStorage.setItem('user', JSON.stringify(userData));
      
      console.log(`${isLogin ? 'Login' : 'Registration'} successful for ${formData.email}, redirecting...`);
      navigate('/dashboard');
      
    } catch (error) {
      console.error(`${isLogin ? 'Login' : 'Registration'} error:`, error.message);
      if (!error.message.includes('Incorrect credentials')) {
        setError('An unexpected error occurred. Please try again.')
      }
    } finally {
      setLoading(false);
    }
  };

  const handleMetaMaskLogin = async () => {
    if (!metamaskAvailable) {
      setError('MetaMask is not installed. Please install the MetaMask browser extension first.');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const address = await connectMetaMask();
      if (!address) {
        throw new Error('Failed to connect to MetaMask wallet. Please try again.');
      }
      
      const userData = {
        name: `MetaMask User (${address.substring(0, 6)}...${address.substring(address.length - 4)})`,
        email: `metamask-${address}@local.user`,
        role: 'User',
        walletAddress: address,
        lastLogin: new Date().toISOString()
      };
      
      localStorage.setItem('isAuthenticated', 'true');
      localStorage.setItem('user', JSON.stringify(userData));
      console.log('MetaMask login successful, redirecting to dashboard');
      setTimeout(() => {
        navigate('/dashboard');
      }, 100);
      
    } catch (error) {
      console.error('MetaMask login error:', error);
      setError(error.message || 'Failed to connect with MetaMask. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError(null);
    setSuccess(null);
    setLoginAttempts(0);
    setIsBlocked(false);
    setFormData({ name: '', email: '', password: '' });
  };

  return (
    <div className='login-page1'>
      <div className="login-page">
        <div className="login-container-split">
          <div className="login-card-container">
            <div className="login-card">
              <div className="login-header">
                <div className="logo">
                  <LockIcon className="logo-icon" />
                  <h1>FraudGuard</h1>
                </div>
                <p className="subtitle">Secure Access</p>
              </div>

              {isBlocked && (
                <div className="error-message">
                  <WarningIcon className="icon" />
                  Too many failed attempts. Access temporarily blocked. Please try again shortly.
                </div>
              )}
              {error && !isBlocked && (
                <div className="error-message">
                  <WarningIcon className="icon" />
                  {error}
                </div>
              )}
              {success && (
                <div className="success-message">
                  <CheckCircleIcon className="icon" />
                  {success}
                </div>
              )}

              <div className="auth-tabs">
                <button 
                  className={`auth-tab ${isLogin ? 'active' : ''}`} 
                  onClick={() => !isLogin && toggleMode()}
                  disabled={isLogin || isBlocked}
                >
                  Login
                </button>
                <button 
                  className={`auth-tab ${!isLogin ? 'active' : ''}`} 
                  onClick={() => isLogin && toggleMode()}
                  disabled={!isLogin || isBlocked}
                >
                  Create Account
                </button>
              </div>

              <form onSubmit={handleLoginOrRegister} className="login-form">
                {!isLogin && (
                  <TextField
                    label="Full Name"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    disabled={loading || isBlocked}
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <PersonIcon />
                        </InputAdornment>
                      ),
                    }}
                    InputLabelProps={{
                      shrink: true,
                      style: { marginTop: '4px' }
                    }}
                    sx={{ 
                      marginBottom: '16px',
                      '& .MuiInputLabel-root': {
                        transform: 'translate(14px, -9px) scale(0.75)'
                      },
                      '& .MuiOutlinedInput-root': {
                        paddingTop: '8px'
                      }
                    }}
                  />
                )}
                
                <TextField
                  label="Email Address"
                  variant="outlined"
                  fullWidth
                  margin="normal"
                  type="email"
                  name="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleInputChange}
                  disabled={loading || isBlocked}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <EmailIcon />
                      </InputAdornment>
                    ),
                  }}
                  InputLabelProps={{
                    shrink: true,
                    style: { marginTop: '4px' }
                  }}
                  sx={{ 
                    marginBottom: '16px',
                    '& .MuiInputLabel-root': {
                      transform: 'translate(14px, -9px) scale(0.75)'
                    },
                    '& .MuiOutlinedInput-root': {
                      paddingTop: '8px'
                    }
                  }}
                />

                <TextField
                  label="Password"
                  variant="outlined"
                  fullWidth
                  margin="normal"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleInputChange}
                  disabled={loading || isBlocked}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <PasswordIcon />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={handleClickShowPassword}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                  InputLabelProps={{
                    shrink: true,
                    style: { marginTop: '4px' }
                  }}
                  sx={{ 
                    marginBottom: '16px',
                    '& .MuiInputLabel-root': {
                      transform: 'translate(14px, -9px) scale(0.75)'
                    },
                    '& .MuiOutlinedInput-root': {
                      paddingTop: '8px'
                    }
                  }}
                />
                
                <div style={{ marginTop: '1.5rem', marginBottom: '1.5rem' }}>
                  <button 
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading || isBlocked}
                    style={{ width: '100%', padding: '10px 0' }}
                  >
                    {loading ? (
                      <>
                        <CircularProgress size={20} sx={{ color: 'white', mr: 1}} /> Processing...
                      </>
                    ) : (isLogin ? 'Login' : 'Register')}
                  </button>
                </div>

                <div className="separator" style={{ margin: '1rem 0' }}>OR</div>

                <button 
                  type="button" 
                  className="btn btn-metamask" 
                  onClick={handleMetaMaskLogin}
                  disabled={loading || isBlocked}
                  style={{ width: '100%', marginBottom: '0.5rem', padding: '10px 0' }}
                >
                  <WalletIcon sx={{ mr: 1 }} />
                  Login with MetaMask
                </button>
                {!metamaskAvailable && (
                  <p className="metamask-warning" style={{ textAlign: 'center', marginTop: '0.5rem' }}>MetaMask extension not detected.</p>
                )}
              </form>

              <div className="toggle-mode" style={{ marginTop: '1.5rem' }}>
                {isLogin ? "Don't have an account?" : "Already have an account?"}
                <button onClick={toggleMode} disabled={isBlocked} className="text-btn">
                  {isLogin ? 'Register Now' : 'Login Here'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Right side container with white background for the GIF */}
      <div className="right-side-container">
        <img 
          src="/images/login-animation.gif" 
          alt="Secure transaction monitoring" 
        />
      </div>
    </div>
  );
};

export default Login; 