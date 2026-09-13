import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, RefreshControl } from 'react-native';
import api from '../services/api';

export default function BookingsScreen({ navigation }) {
  const [bookings, setBookings] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadBookings = async () => {
    try {
      const res = await api.get('/api/v1/bookings/');
      setBookings(res.data.results || res.data || []);
    } catch (e) {
      console.log('Bookings load error:', e);
    }
  };

  useEffect(() => { loadBookings(); }, []);

  const statusColor = (status) => {
    const colors = { confirmed: '#22c55e', in_progress: '#6366f1', completed: '#06b6d4', cancelled: '#ef4444', tentative: '#f59e0b' };
    return colors[status] || '#94a3b8';
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.card} onPress={() => navigation.navigate('BookingDetail', { id: item.id })}>
      <View style={styles.cardHeader}>
        <Text style={styles.reference}>{item.reference || item.id?.slice(0,8)}</Text>
        <View style={[styles.badge, { backgroundColor: statusColor(item.status) + '20' }]}>
          <Text style={[styles.badgeText, { color: statusColor(item.status) }]}>{item.status?.replace('_', ' ')}</Text>
        </View>
      </View>
      <Text style={styles.title}>{item.title || item.client_name || 'Booking'}</Text>
      <Text style={styles.date}>{item.date} {item.start_time ? `at ${item.start_time}` : ''}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={bookings}
        keyExtractor={(item) => String(item.id || item.pk)}
        renderItem={renderItem}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={async () => { setRefreshing(true); await loadBookings(); setRefreshing(false); }} />}
        ListEmptyComponent={<Text style={styles.empty}>No bookings yet</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  card: { backgroundColor: '#fff', marginHorizontal: 16, marginTop: 12, borderRadius: 16, padding: 16, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  reference: { fontSize: 12, color: '#6366f1', fontWeight: '700' },
  badge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8 },
  badgeText: { fontSize: 11, fontWeight: '600', textTransform: 'capitalize' },
  title: { fontSize: 16, fontWeight: '700', color: '#1e293b', marginBottom: 4 },
  date: { fontSize: 13, color: '#64748b' },
  empty: { textAlign: 'center', color: '#94a3b8', marginTop: 60, fontSize: 15 },
});
