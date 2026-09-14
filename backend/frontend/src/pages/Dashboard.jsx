import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { 
  TrendingUp, 
  TrendingDown, 
  Wallet, 
  DollarSign,
  PieChart,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [balance, setBalance] = useState(0);
  const [income, setIncome] = useState(0);
  const [expenses, setExpenses] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [insights, setInsights] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [balanceRes, transactionsRes, insightsRes] = await Promise.all([
        api.get('/transactions/balance'),
        api.get('/transactions?limit=5'),
        api.get('/insights')
      ]);

      setBalance(balanceRes.data.balance);
      setIncome(balanceRes.data.income || 0);
      setExpenses(balanceRes.data.expenses || 0);
      setTransactions(transactionsRes.data);
      setInsights(insightsRes.data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
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

  const savingsRate = income > 0 ? ((income - expenses) / income * 100) : 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-green border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Available Balance</p>
              <p className="text-3xl font-bold text-primary-green mt-1">
                {formatCurrency(balance)}
              </p>
            </div>
            <div className="p-3 bg-primary-green/10 rounded-full">
              <Wallet className="text-primary-green" size={24} />
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500">Income</p>
              <p className="text-sm font-semibold text-green-600">{formatCurrency(income)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Expenses</p>
              <p className="text-sm font-semibold text-red-500">{formatCurrency(expenses)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Monthly Flow</p>
              <p className="text-3xl font-bold text-primary-green mt-1">
                {income > 0 ? `${Math.round((expenses / income) * 100)}%` : '0%'}
              </p>
            </div>
            <div className="p-3 bg-accent-orange/10 rounded-full">
              <PieChart className="text-accent-orange" size={24} />
            </div>
          </div>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-accent-orange rounded-full h-2 transition-all duration-500"
                style={{ width: `${Math.min((expenses / income) * 100, 100)}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {income === 0 ? 'Add income to calculate flow' : `${Math.round((expenses / income) * 100)}% used`}
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Savings Rate</p>
              <p className="text-3xl font-bold text-primary-green mt-1">
                {income > 0 ? `${Math.round(savingsRate)}%` : '0%'}
              </p>
            </div>
            <div className="p-3 bg-green-500/10 rounded-full">
              <TrendingUp className="text-green-500" size={24} />
            </div>
          </div>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-500 rounded-full h-2 transition-all duration-500"
                style={{ width: `${Math.max(Math.min(savingsRate, 100), 0)}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {income === 0 ? 'Add income to start saving' : `${Math.round(savingsRate)}% of income saved`}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="font-semibold text-lg mb-4">Recent Activity</h2>
          {transactions.length === 0 ? (
            <p className="text-gray-500 text-sm">No transactions yet. Add your first one!</p>
          ) : (
            <div className="space-y-3">
              {transactions.map((t) => (
                <div key={t.id} className="flex items-center justify-between py-2 border-b border-gray-100">
                  <div className="flex items-center gap-3">
                    {t.type === 'income' ? (
                      <ArrowUpRight className="text-green-500" size={18} />
                    ) : (
                      <ArrowDownRight className="text-red-500" size={18} />
                    )}
                    <div>
                      <p className="font-medium text-sm">{t.category || t.description || 'Transaction'}</p>
                      <p className="text-xs text-gray-500">{new Date(t.date).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <span className={`font-semibold ${t.type === 'income' ? 'text-green-600' : 'text-red-500'}`}>
                    {t.type === 'income' ? '+' : '-'}{formatCurrency(t.amount)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="font-semibold text-lg mb-4">Insights</h2>
          {insights.length === 0 ? (
            <p className="text-gray-500 text-sm">No insights yet. Add more transactions!</p>
          ) : (
            <div className="space-y-3">
              {insights.slice(0, 3).map((insight, index) => (
                <div 
                  key={index} 
                  className={`p-4 rounded-lg border-l-4 ${
                    insight.severity === 'success' ? 'border-green-500 bg-green-50' :
                    insight.severity === 'warning' ? 'border-yellow-500 bg-yellow-50' :
                    insight.severity === 'danger' ? 'border-red-500 bg-red-50' :
                    'border-blue-500 bg-blue-50'
                  }`}
                >
                  <p className="text-sm">{insight.message}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;