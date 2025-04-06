import { useState } from 'react';
import {
  Person as PersonIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Palette as PaletteIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import {
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Switch,
  Divider,
  Box
} from '@mui/material';
import Layout from '../components/Layout';

const Settings = () => {
  const [profileForm, setProfileForm] = useState({
    fullName: 'Admin User',
    email: 'admin@fraudguard.com',
    position: 'Administrator'
  });
  
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [securityAlerts, setSecurityAlerts] = useState(true);
  const [marketingEmails, setMarketingEmails] = useState(false);
  const [twoFactorAuth, setTwoFactorAuth] = useState(false);
  const [loginNotifications, setLoginNotifications] = useState(true);
  
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileForm(prevForm => ({
      ...prevForm,
      [name]: value
    }));
  };
  
  const handleSaveProfile = () => {
    // In a real application, this would save to a database
    alert('Profile information saved!');
  };

  return (
    <Layout title="Settings">
      <div className="page-container">
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
          Settings
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <PersonIcon sx={{ color: '#6147FF', mr: 1 }} />
                  <Typography variant="h6">Profile Information</Typography>
                </Box>
                
                <Divider sx={{ mb: 3 }} />
                
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <TextField 
                      fullWidth
                      label="Full Name"
                      name="fullName"
                      value={profileForm.fullName}
                      onChange={handleProfileChange}
                      variant="outlined"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField 
                      fullWidth
                      label="Email Address"
                      name="email"
                      type="email"
                      value={profileForm.email}
                      onChange={handleProfileChange}
                      variant="outlined"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField 
                      fullWidth
                      label="Position"
                      name="position"
                      value={profileForm.position}
                      onChange={handleProfileChange}
                      variant="outlined"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Button 
                      variant="contained" 
                      color="primary" 
                      startIcon={<SaveIcon />}
                      onClick={handleSaveProfile}
                      sx={{ mt: 2 }}
                    >
                      Save Changes
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <SecurityIcon sx={{ color: '#6147FF', mr: 1 }} />
                  <Typography variant="h6">Security Settings</Typography>
                </Box>
                
                <Divider sx={{ mb: 3 }} />
                
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={500}>Two-Factor Authentication</Typography>
                      <Typography variant="body2" color="text.secondary">Enable extra account security</Typography>
                    </Box>
                    <Switch 
                      checked={twoFactorAuth} 
                      onChange={() => setTwoFactorAuth(!twoFactorAuth)}
                      color="primary"
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={500}>Login Notifications</Typography>
                      <Typography variant="body2" color="text.secondary">Receive alerts for new login attempts</Typography>
                    </Box>
                    <Switch 
                      checked={loginNotifications} 
                      onChange={() => setLoginNotifications(!loginNotifications)}
                      color="primary"
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
            
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <NotificationsIcon sx={{ color: '#6147FF', mr: 1 }} />
                  <Typography variant="h6">Notification Preferences</Typography>
                </Box>
                
                <Divider sx={{ mb: 3 }} />
                
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={500}>Email Notifications</Typography>
                      <Typography variant="body2" color="text.secondary">Receive notifications via email</Typography>
                    </Box>
                    <Switch 
                      checked={emailNotifications} 
                      onChange={() => setEmailNotifications(!emailNotifications)}
                      color="primary"
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={500}>Security Alerts</Typography>
                      <Typography variant="body2" color="text.secondary">Get alerts about suspicious activities</Typography>
                    </Box>
                    <Switch 
                      checked={securityAlerts} 
                      onChange={() => setSecurityAlerts(!securityAlerts)}
                      color="primary"
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={500}>Marketing Emails</Typography>
                      <Typography variant="body2" color="text.secondary">Receive updates about new features</Typography>
                    </Box>
                    <Switch 
                      checked={marketingEmails} 
                      onChange={() => setMarketingEmails(!marketingEmails)}
                      color="primary"
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </div>
    </Layout>
  );
};

export default Settings; 