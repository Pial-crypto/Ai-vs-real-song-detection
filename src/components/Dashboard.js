import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography, Box, LinearProgress } from '@mui/material';
import { MusicNote as MusicIcon, Autorenew as AIIcon, Person as HumanIcon } from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getDashboards } from '../functions/getDashboards';
import { extractDateParts } from '../functions/extractDateParts';



// Professional stat card component
const StatCard = ({ icon, title, subtitle, progress, color, gradient }) => (
  <Paper
    elevation={0}
    sx={{
      p: 3,
      display: 'flex',
      alignItems: 'center',
      borderRadius: 3,
      background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
      border: '1px solid #e2e8f0',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': { 
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        transform: 'translateY(-4px)',
        border: '1px solid #cbd5e1',
      },
      height: 130,
    }}
  >
    <Box
      sx={{
        width: 64,
        height: 64,
        borderRadius: 2.5,
        background: gradient,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        mr: 2.5,
        boxShadow: '0px 8px 16px rgba(0,0,0,0.15)',
        transition: 'transform 0.3s',
        '&:hover': {
          transform: 'scale(1.05)',
        }
      }}
    >
      {icon}
    </Box>
    <Box sx={{ flex: 1 }}>
      <Typography variant="h4" fontWeight="700" sx={{ mb: 0.5, color: '#1e293b' }}>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5, fontWeight: 500 }}>
        {subtitle}
      </Typography>
      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{
          height: 8,
          borderRadius: 4,
          backgroundColor: '#e2e8f0',
          '& .MuiLinearProgress-bar': { 
            borderRadius: 4, 
            backgroundColor: color,
            boxShadow: `0 0 10px ${color}40`,
          },
        }}
      />
    </Box>
  </Paper>
);

const AdminDashboard = () => {
  const [dashboards, setDashboards] = useState([])
  const [barData, setBarData] = useState([]);
  const today = new Date().toISOString();

 const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  useEffect(() => {
      getDashboards().then(data => {
    console.log("Dashboard data:", data);

    setDashboards(data);

         const preddictionObject={}
       data.forEach(element => {
          const dateParts = extractDateParts(element.createdAt);
          const month=dateParts.month;
          const day=dateParts.day;
          const year=dateParts.year;
          if (year === extractDateParts(today).year) {
            preddictionObject[month] = (preddictionObject[month] || 0) + 1;
    
          }
        
       });
       console.log("Prediction Object:",preddictionObject);
       const tempArray=[];
       for(let i=1;i<=extractDateParts(today).month;i++){
        if(!preddictionObject[i])
     tempArray.push({name:months[i-1], songs:0});
      }
      console.log("TEMporary Array before pushing",tempArray);
       for (const [key, value] of Object.entries(preddictionObject)) {
        tempArray.push({name:months[key-1], songs:value});
      console.log("the key and the value ",key, value);
      
    }
tempArray.sort((a,b) => {
      const monthA = months.indexOf(a.name) + 1;
      const monthB = months.indexOf(b.name) + 1;
      return monthA - monthB;
    });
    console.log("Temp Array:",tempArray);
        setBarData( tempArray);
  }
  ).catch(err => {
    console.error("Error fetching dashboard data:", err);
  })
},[])


  return (
    <Box sx={{ 
      p: 4, 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
    }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="700" sx={{ color: '#1e293b', mb: 1 }}>
          Music Analysis Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ fontWeight: 500 }}>
          AI-powered song detection analytics
        </Typography>
      </Box>

      {/* Row 1: প্রথম ৩টা স্ট্যাট কার্ড */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<MusicIcon sx={{ color: 'white', fontSize: 32 }} />}
            title={dashboards.length}
            subtitle="Total Songs Analyzed"
            progress={100}
            color="#10b981"
            gradient="linear-gradient(135deg, #10b981 0%, #34d399 100%)"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<AIIcon sx={{ color: 'white', fontSize: 32 }} />}
            title={`${dashboards.filter(d => d.chunkMajorityPrediction=='ai').length/dashboards.length * 100} %`}
            subtitle="AI Generated Songs through chunks"
            progress={dashboards.filter(d => d.chunkMajorityPrediction=='ai').length / dashboards.length * 100}
            color="#3b82f6"
            gradient="linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)"
          />
        </Grid>
            <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<AIIcon sx={{ color: 'white', fontSize: 32 }} />}
            title={`${dashboards.filter(d => d.modelWiseMajorityPrediction=='ai').length/dashboards.length *100} %`}
            subtitle="AI Generated Songs through models"
            progress={dashboards.filter(d => d.modelWiseMajorityPrediction=='ai').length / dashboards.length * 100}
            color="#3b82f6"
            gradient="linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<HumanIcon sx={{ color: 'white', fontSize: 32 }} />}
            title={`${dashboards.filter(d => d.chunkMajorityPrediction=='real').length/dashboards.length *100} %`}
            subtitle="Human Made Songs through chunks"
            progress={dashboards.filter(d => d.chunkMajorityPrediction=='real').length/dashboards.length*100}
            color="#ef4444"
            gradient="linear-gradient(135deg, #ef4444 0%, #f87171 100%)"
          />
        </Grid>
                <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<HumanIcon sx={{ color: 'white', fontSize: 32 }} />}
            title={`${dashboards.filter(d => d.modelWiseMajorityPrediction=='real').length/dashboards.length *100} %`}
            subtitle="Human Made Songs through models"
            progress={dashboards.filter(d => d.modelWiseMajorityPrediction=='real').length/dashboards.length *100}
            color="#ef4444"
            gradient="linear-gradient(135deg, #ef4444 0%, #f87171 100%)"
          />
        </Grid>
      </Grid>

      {/* Row 2: নিচে বড় গ্রাফ - পুরো width এবং centered */}
      <Box sx={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
        <Paper
          elevation={0}
          sx={{
            p: 4,
            borderRadius: 3,
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            border: '1px solid #e2e8f0',
            height: 600,
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          }}
        >
          {/* Graph Header */}
          <Box sx={{ mb: 3, textAlign: 'center' }}>
            <Typography variant="h5" fontWeight="700" sx={{ color: '#1e293b', mb: 1 }}>
              Songs Analyzed Over Time
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
              Monthly analysis breakdown for the last 6 months
            </Typography>
          </Box>
          
          {/* Graph Container */}
          <Box sx={{ flex: 1, minHeight: 0, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart 
                data={barData} 
                margin={{ top: 10, right: 30, left: 0, bottom: 10 }}
              >
                <defs>
                  <linearGradient id="colorSongs" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" stopOpacity={1}/>
                    <stop offset="100%" stopColor="#34d399" stopOpacity={0.85}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeWidth={1.5} />
                <XAxis 
                  dataKey="name" 
                  stroke="#64748b"
                  style={{ fontSize: '16px', fontWeight: 600 }}
                  tickLine={false}
                  axisLine={{ stroke: '#e2e8f0' }}
                />
                <YAxis 
                  stroke="#64748b"
                  style={{ fontSize: '16px', fontWeight: 600 }}
                  tickLine={false}
                  axisLine={{ stroke: '#e2e8f0' }}
                  width={50}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                    fontWeight: 600,
                    padding: '12px 16px'
                  }}
                  cursor={{ fill: '#f1f5f9', radius: 8 }}
                />
                <Legend 
                  wrapperStyle={{ 
                    paddingTop: '20px',
                    fontSize: '16px',
                    fontWeight: 600,
                  }}
                />
                <Bar 
                  dataKey="songs" 
                  fill="url(#colorSongs)" 
                  radius={[10, 10, 0, 0]}
                  name="Songs Analyzed"
                  barSize={80}
                />
              </BarChart>
            </ResponsiveContainer>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

export default AdminDashboard;