import { useState, useEffect } from 'react';
import { 
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon
} from '@mui/icons-material';
import { 
  Card, 
  CardContent, 
  Grid, 
  TextField, 
  InputAdornment, 
  Button, 
  Select, 
  MenuItem, 
  IconButton, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper
} from '@mui/material';
import Layout from '../components/Layout';
import { getMockUsers } from '../api/api';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('All Roles');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getMockUsers();
        if (response.success) {
          setUsers(response.users);
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          user.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRole = selectedRole === 'All Roles' || user.role === selectedRole;
    
    return matchesSearch && matchesRole;
  });

  const handleRoleChange = (e) => {
    setSelectedRole(e.target.value);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleAddUser = () => {
    alert('Add user functionality would be implemented here');
    // In a real app, this would open a modal or navigate to a form
  };

  const handleEditUser = (userId) => {
    alert(`Edit user ${userId}`);
    // In a real app, this would open a modal with the user data
  };

  const handleDeleteUser = (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      setUsers(users.filter(user => user.id !== userId));
    }
  };

  const getInitial = (name) => {
    return name.charAt(0).toUpperCase();
  };

  return (
    <Layout title="User Management">
      <div className="page-container">
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      placeholder="Search users..."
                      value={searchTerm}
                      onChange={handleSearchChange}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <SearchIcon />
                          </InputAdornment>
                        ),
                      }}
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Select
                      value={selectedRole}
                      onChange={handleRoleChange}
                      fullWidth
                      displayEmpty
                      variant="outlined"
                      IconComponent={ExpandMoreIcon}
                    >
                      <MenuItem value="All Roles">All Roles</MenuItem>
                      <MenuItem value="Admin">Admin</MenuItem>
                      <MenuItem value="User">User</MenuItem>
                    </Select>
                  </Grid>
                  <Grid item xs={6} md={3} sx={{ textAlign: 'right' }}>
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<AddIcon />}
                      onClick={handleAddUser}
                    >
                      Add User
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <TableContainer component={Paper} sx={{ boxShadow: 'none' }}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 'bold' }}>USER</TableCell>
                        <TableCell sx={{ fontWeight: 'bold' }}>ROLE</TableCell>
                        <TableCell sx={{ fontWeight: 'bold' }}>STATUS</TableCell>
                        <TableCell sx={{ fontWeight: 'bold' }}>ACTIONS</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {loading ? (
                        <TableRow>
                          <TableCell colSpan={4} align="center">Loading user data...</TableCell>
                        </TableRow>
                      ) : filteredUsers.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={4} align="center">No users found</TableCell>
                        </TableRow>
                      ) : (
                        filteredUsers.map((user) => (
                          <TableRow key={user.id}>
                            <TableCell>
                              <div style={{ display: 'flex', alignItems: 'center' }}>
                                <div className="user-avatar" style={{ 
                                  backgroundColor: user.role === 'Admin' ? '#4a6cd8' : '#5c4ee5',
                                  width: '40px',
                                  height: '40px',
                                  borderRadius: '50%',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  color: 'white',
                                  fontWeight: 'bold',
                                  marginRight: '16px'
                                }}>
                                  {getInitial(user.name)}
                                </div>
                                <div>
                                  <div style={{ fontWeight: 'bold' }}>{user.name}</div>
                                  <div style={{ color: '#666' }}>{user.email}</div>
                                </div>
                              </div>
                            </TableCell>
                            <TableCell>{user.role}</TableCell>
                            <TableCell>
                              <span style={{ 
                                padding: '6px 12px',
                                borderRadius: '16px',
                                backgroundColor: user.status === 'Active' ? 'rgba(76, 175, 80, 0.1)' : 'rgba(158, 158, 158, 0.1)',
                                color: user.status === 'Active' ? '#4caf50' : '#9e9e9e'
                              }}>
                                {user.status}
                              </span>
                            </TableCell>
                            <TableCell>
                              <div style={{ display: 'flex' }}>
                                <IconButton
                                  onClick={() => handleEditUser(user.id)}
                                  size="small"
                                  sx={{ 
                                    backgroundColor: 'black',
                                    color: 'white',
                                    marginRight: '8px',
                                    '&:hover': {
                                      backgroundColor: '#333'
                                    }
                                  }}
                                >
                                  <EditIcon fontSize="small" />
                                </IconButton>
                                <IconButton
                                  onClick={() => handleDeleteUser(user.id)}
                                  size="small"
                                  sx={{ 
                                    backgroundColor: 'black',
                                    color: 'white',
                                    '&:hover': {
                                      backgroundColor: '#333'
                                    }
                                  }}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </div>
    </Layout>
  );
};

export default UserManagement; 