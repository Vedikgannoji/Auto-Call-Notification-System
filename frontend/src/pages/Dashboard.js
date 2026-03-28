import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, UserCheck, Bell, AlertTriangle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { toast } from 'sonner';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/dashboard/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      toast.error('Failed to load dashboard stats');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading dashboard...</div>;
  }

  const statCards = [
    {
      title: 'Total Students',
      value: stats?.total_students || 0,
      icon: Users,
      color: 'bg-blue-500',
      testId: 'total-students-stat'
    },
    {
      title: 'Total Parents',
      value: stats?.total_parents || 0,
      icon: UserCheck,
      color: 'bg-green-500',
      testId: 'total-parents-stat'
    },
    {
      title: "Today's Absentees",
      value: stats?.today_absentees || 0,
      icon: AlertTriangle,
      color: 'bg-orange-500',
      testId: 'today-absentees-stat'
    },
    {
      title: 'Notifications Sent',
      value: stats?.notifications_sent_today || 0,
      icon: Bell,
      color: 'bg-purple-500',
      testId: 'notifications-sent-stat'
    }
  ];

  const chartData = [
    { name: 'Students', count: stats?.total_students || 0 },
    { name: 'Parents', count: stats?.total_parents || 0 },
    { name: 'Absentees', count: stats?.today_absentees || 0 },
    { name: 'Notifications', count: stats?.notifications_sent_today || 0 }
  ];

  return (
    <div className="p-4 md:p-8" data-testid="dashboard-page">
      <div className="mb-6">
        <h1 className="text-4xl font-bold text-[#0F172A] tracking-tight" style={{ fontFamily: 'Manrope' }}>Dashboard</h1>
        <p className="text-slate-600 mt-2">Overview of attendance and notifications</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="col-span-12 md:col-span-3 border-slate-200 hover:shadow-md transition-shadow duration-200" data-testid={stat.testId}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600 uppercase tracking-wider">{stat.title}</p>
                    <p className="text-3xl font-bold text-[#0F172A] mt-2" style={{ fontFamily: 'Manrope' }}>{stat.value}</p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}

        <Card className="col-span-12 md:col-span-8 border-slate-200">
          <CardHeader>
            <CardTitle className="text-xl font-bold" style={{ fontFamily: 'Manrope' }}>Statistics Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="name" stroke="#64748B" />
                <YAxis stroke="#64748B" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#FFFFFF', 
                    border: '1px solid #E2E8F0',
                    borderRadius: '8px'
                  }} 
                />
                <Legend />
                <Bar dataKey="count" fill="#2563EB" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="col-span-12 md:col-span-4 border-slate-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-red-700" style={{ fontFamily: 'Manrope' }}>Failed Notifications</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center h-48">
              <div className="text-center">
                <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                <p className="text-5xl font-bold text-red-700" style={{ fontFamily: 'Manrope' }}>{stats?.failed_notifications || 0}</p>
                <p className="text-red-600 mt-2">Notifications need retry</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
