import React, { useState, useEffect } from 'react';
import api from '../services/api';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, LineChart, Line
} from 'recharts';
import toast from 'react-hot-toast';

const Analytics = () => {
  const [loading, setLoading] = useState(true);
  const [categoryData, setCategoryData] = useState([]);
  const [monthlyData, setMonthlyData] = useState([]);
  const [stats, setStats] = useState({});

  const COLORS = ['#1a472a', '#2d5a3d', '#e8a87c', '#c38d6b', '#4a7c59', '#8fb996'];

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const [categoriesRes, monthlyRes] = await Promise.all([
        api.get('/analytics/categories'),
        api.get('/analytics/monthly')
      ]);
      setCategoryData(categoriesRes.data);
      setMonthlyData(monthlyRes.data);
      
      // Get stats
      const statsRes = await api.get('/analytics/stats');
      setStats(statsRes.data);
    } catch (error) {
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-green border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-2xl font-bold text-primary-green">Analytics</h1>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-4">
          <p className="text-sm text-gray-500">Total Spent</p>
          <p className="text-xl font-bold text-primary-green">{formatCurrency(stats.totalSpent || 0)}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4">
          <p className="text-sm text-gray-500">Average Daily</p>
          <p className="text-xl font-bold text-primary-green">{formatCurrency(stats.averageDaily || 0)}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4">
          <p className="text-sm text-gray-500">Highest Category</p>
          <p className="text-xl font-bold text-primary-green">{stats.topCategory || '-'}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4">
          <p className="text-sm text-gray-500">Monthly Change</p>
          <p className={`text-xl font-bold ${stats.monthlyChange >= 0 ? 'text-red-500' : 'text-green-500'}`}>
            {stats.monthlyChange !== undefined ? `${stats.monthlyChange > 0 ? '+' : ''}${Math.round(stats.monthlyChange)}%` : '-'}
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold mb-4">Spending by Category</h3>
          {categoryData.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-8">No data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(value)} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold mb-4">Monthly Spending</h3>
          {monthlyData.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-8">No data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Legend />
                <Bar dataKey="expenses" fill="#e8a87c" name="Expenses" />
                <Bar dataKey="income" fill="#1a472a" name="Income" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};

export default Analytics;