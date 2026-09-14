import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Plus, X } from 'lucide-react';
import toast from 'react-hot-toast';

const Budgets = () => {
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    category: '',
    amount: '',
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear()
  });

  useEffect(() => {
    loadBudgets();
  }, []);

  const loadBudgets = async () => {
    try {
      setLoading(true);
      const response = await api.get('/budgets', {
        params: {
          month: new Date().getMonth() + 1,
          year: new Date().getFullYear()
        }
      });
      setBudgets(response.data);
    } catch (error) {
      toast.error('Failed to load budgets');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/budgets', {
        category: formData.category,
        amount: parseFloat(formData.amount),
        month: formData.month,
        year: formData.year
      });
      toast.success('Budget created');
      setShowModal(false);
      setFormData({
        category: '',
        amount: '',
        month: new Date().getMonth() + 1,
        year: new Date().getFullYear()
      });
      loadBudgets();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create budget');
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
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="font-serif text-2xl font-bold text-primary-green">Budgets</h1>
        <button
          onClick={() => setShowModal(true)}
          className="bg-primary-green text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-primary-greenLight transition-colors"
        >
          <Plus size={20} />
          Create Budget
        </button>
      </div>

      {budgets.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <p className="text-gray-500">No budgets yet</p>
          <p className="text-sm text-gray-400 mt-1">Create a budget to track your spending</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {budgets.map((budget) => (
            <div key={budget.id} className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-semibold text-lg">{budget.category}</h3>
                  <p className="text-sm text-gray-500">
                    Budget: {formatCurrency(budget.amount)}
                  </p>
                </div>
                <span className={`text-sm font-semibold ${
                  budget.percentage >= 100 ? 'text-red-500' :
                  budget.percentage >= 80 ? 'text-yellow-500' :
                  'text-green-500'
                }`}>
                  {Math.round(budget.percentage)}% used
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`rounded-full h-2 transition-all duration-500 ${
                    budget.percentage >= 100 ? 'bg-red-500' :
                    budget.percentage >= 80 ? 'bg-yellow-500' :
                    'bg-primary-green'
                  }`}
                  style={{ width: `${Math.min(budget.percentage, 100)}%` }}
                ></div>
              </div>
              <div className="flex justify-between mt-2 text-sm">
                <span className="text-gray-500">Spent: {formatCurrency(budget.spent)}</span>
                <span className="text-gray-500">Remaining: {formatCurrency(budget.remaining)}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-serif text-xl font-bold text-primary-green">Create Budget</h2>
              <button onClick={() => setShowModal(false)} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Amount</label>
                <input
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({...formData, amount: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent"
                  required
                  step="0.01"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Month</label>
                  <select
                    value={formData.month}
                    onChange={(e) => setFormData({...formData, month: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent"
                  >
                    {Array.from({length: 12}, (_, i) => (
                      <option key={i + 1} value={i + 1}>
                        {new Date(2024, i).toLocaleString('default', { month: 'long' })}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
                  <input
                    type="number"
                    value={formData.year}
                    onChange={(e) => setFormData({...formData, year: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent"
                    required
                  />
                </div>
              </div>
              <button
                type="submit"
                className="w-full bg-primary-green text-white py-3 rounded-lg font-semibold hover:bg-primary-greenLight transition-colors"
              >
                Create Budget
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Budgets;