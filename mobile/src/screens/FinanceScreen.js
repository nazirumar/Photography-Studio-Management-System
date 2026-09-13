import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, RefreshControl } from 'react-native';
import api from '../services/api';

export default function FinanceScreen() {
  const [invoices, setInvoices] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadInvoices = async () => {
    try {
      const res = await api.get('/api/v1/invoices/');
      setInvoices(res.data.results || res.data || []);
    } catch (e) { console.log(e); }
  };

  useEffect(() => { loadInvoices(); }, []);

  const statusColor = (s) => ({ paid: '#22c55e', partial: '#f59e0b', issued: '#6366f1', overdue: '#ef4444', draft: '#94a3b8' }[s] || '#94a3b8');

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.number}>{item.invoice_number}</Text>
        <View style={[styles.badge, { backgroundColor: statusColor(item.status) + '20' }]}>
          <Text style={[styles.badgeText, { color: statusColor(item.status) }]}>{item.status}</Text>
        </View>
      </View>
      <Text style={styles.client}>{item.client_name || item.client}</Text>
      <View style={styles.amounts}>
        <Text style={styles.total}>₦{item.total?.toLocaleString()}</Text>
        <Text style={[styles.balance, { color: item.balance > 0 ? '#ef4444' : '#22c55e' }]}>Bal: ₦{item.balance?.toLocaleString()}</Text>
      </View>
    </View>
  );

  return (
    <FlatList style={styles.container} data={invoices} keyExtractor={(item) => String(item.id || item.pk)} renderItem={renderItem}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={async () => { setRefreshing(true); await loadInvoices(); setRefreshing(false); }} />}
      ListEmptyComponent={<Text style={styles.empty}>No invoices yet</Text>} />
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  card: { backgroundColor: '#fff', marginHorizontal: 16, marginTop: 10, borderRadius: 12, padding: 14, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 3, elevation: 1 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  number: { fontSize: 12, color: '#6366f1', fontWeight: '700' },
  badge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8 },
  badgeText: { fontSize: 11, fontWeight: '600', textTransform: 'capitalize' },
  client: { fontSize: 15, fontWeight: '600', color: '#1e293b', marginBottom: 6 },
  amounts: { flexDirection: 'row', justifyContent: 'space-between' },
  total: { fontSize: 16, fontWeight: '800', color: '#1e293b' },
  balance: { fontSize: 13, fontWeight: '600' },
  empty: { textAlign: 'center', color: '#94a3b8', marginTop: 60 },
});
