import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, RefreshControl } from 'react-native';
import api from '../services/api';

export default function DashboardScreen() {
  const [stats, setStats] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadStats = async () => {
    try {
      const res = await api.get('/api/v1/dashboard/');
      setStats(res.data);
    } catch (e) {
      console.log('Dashboard load error:', e);
    }
  };

  useEffect(() => { loadStats(); }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadStats();
    setRefreshing(false);
  };

  const StatCard = ({ title, value, color = '#1e293b' }) => (
    <View style={[styles.card, { borderLeftColor: color }]}>
      <Text style={styles.cardTitle}>{title}</Text>
      <Text style={[styles.cardValue, { color }]}>{value}</Text>
    </View>
  );

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.header}>Dashboard</Text>
      {stats ? (
        <>
          <StatCard title="Total Clients" value={stats.total_clients || 0} color="#6366f1" />
          <StatCard title="Active Bookings" value={stats.active_bookings || 0} color="#22c55e" />
          <StatCard title="Revenue This Month" value={`₦${(stats.revenue_this_month || 0).toLocaleString()}`} color="#f59e0b" />
          <StatCard title="Pending Invoices" value={stats.pending_invoices || 0} color="#ef4444" />
          <StatCard title="Completed Shoots" value={stats.completed_shoots || 0} color="#06b6d4" />
        </>
      ) : (
        <Text style={styles.loading}>Loading...</Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc', padding: 16 },
  header: { fontSize: 28, fontWeight: '800', color: '#1e293b', marginBottom: 20 },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 20, marginBottom: 12, borderLeftWidth: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  cardTitle: { fontSize: 13, color: '#64748b', fontWeight: '600', marginBottom: 4 },
  cardValue: { fontSize: 28, fontWeight: '800' },
  loading: { textAlign: 'center', color: '#94a3b8', marginTop: 40 },
});
