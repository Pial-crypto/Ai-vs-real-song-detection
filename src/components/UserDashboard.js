import React, { useEffect, useState } from 'react';
import {
  Paper,
  Typography,
  Box,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { getDashboards } from '../functions/getDashboards';
import { extractDateParts } from '../functions/extractDateParts';
import { getFromLocal } from '../functions/localStorage';



const UserDashboard = () => {
  const today=new Date().toISOString();
  console.log("Today:",extractDateParts(today) );
  const [predictionHistory,setPredictionHistory]=useState([]);
 const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  

useEffect(() => {
    getDashboards().then(data => {
    console.log("Dashboard data:", data);
    console.log("date",extractDateParts(data.createdAt) );
     const preddictionObject={}
   data.forEach(element => {
      const dateParts = extractDateParts(element.createdAt);
      const month=dateParts.month;
      const day=dateParts.day;
      const year=dateParts.year;
      if (year === extractDateParts(today).year && month === extractDateParts(today).month && element.user_id===getFromLocal('user').id) {
        preddictionObject[day] = (preddictionObject[day] || 0) + 1;

      }
    
   });
   console.log("Prediction Object:",preddictionObject);
   const tempArray=[];
   for(let i=1;i<=extractDateParts(today).day;i++){
    if(!preddictionObject[i])
 tempArray.push({date:`${months[extractDateParts(today).month-1]} ${i}`, songs:0});
  }
   for (const [key, value] of Object.entries(preddictionObject)) {
    tempArray.push({date:`${months[extractDateParts(today).month-1]} ${key}`, songs:value});
  console.log("the key and the value ",key, value);
  
}
    tempArray.sort((a,b) => {
      const dayA = parseInt(a.date.split(' ')[1], 10);
      const dayB = parseInt(b.date.split(' ')[1], 10);
      return dayA - dayB;
    });
console.log("Temp Array:",tempArray);
    setPredictionHistory( tempArray);
  } 
).catch(err => {
    console.error("Error fetching dashboard data:", err);

  })
}, []);


  return (
    <Box >
      <Paper
        sx={{
          p: { xs: 3, md: 4 },
          mb: 4,
          background: 'linear-gradient(120deg, #00B894 0%, #2D3436 100%)',
          color: 'white',
          borderRadius: 3,
          boxShadow: 3,
        }}
      >
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Welcome back to your dashboard
        </Typography>
        <Typography variant="subtitle1" sx={{ opacity: 0.92, maxWidth: 600 }}>
          Monitor your AI song predictions and activity. This dashboard is designed for professional, industrial-grade music analysis and reporting.
        </Typography>
      </Paper>

      <Paper sx={{ p: { xs: 3, md: 4 }, borderRadius: 3, boxShadow: 2 }}>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          My Prediction Activity
        </Typography>
        <Box sx={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={predictionHistory}>
              <defs>
                <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00B894" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#00B894" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="songs"
                stroke="#00B894"
                fillOpacity={1}
                fill="url(#colorUv)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Box>
      </Paper>
    </Box>
  );
};

export default UserDashboard;