import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import api from '../services/api';

export default function BookingDetailScreen({ route }) {
  const [booking, setBooking] = useState(null);
  const { id } = route.params;

  useEffect(() => {
    api.get(`/api/v1/bookings/${id}/`).then(res => setBooking(res.data)).catch(console.log);
  }, [id]);

  if (!booking) return <View style={styles.center}><Text style={styles.loading}>Loading...</Text></View>;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.reference}>{booking.reference}</Text>
        <Text style={styles.title}>{booking.title || booking.client_name}</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Date:</Text>
          <Text style={styles.value}>{booking.date}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Status:</Text>
          <Text style={styles.value}>{booking.status?.replace('_', ' ')}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Amount:</Text>
          <Text style={styles.value}>₦{booking.total_amount?.toLocaleString()}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Paid:</Text>
          <Text style={styles.value}>₦{booking.amount_paid?.toLocaleString()}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Balance:</Text>
          <Text style={[styles.value, { color: booking.balance > 0 ? '#ef4444' : '#22c55e' }]}>₦{booking.balance?.toLocaleString()}</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc', padding: 16 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 20, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  reference: { fontSize: 12, color: '#6366f1', fontWeight: '700', marginBottom: 4 },
  title: { fontSize: 22, fontWeight: '800', color: '#1e293b', marginBottom: 16 },
  row: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#f1f5f9' },
  label: { fontSize: 14, color: '#64748b' },
  value: { fontSize: 14, fontWeight: '600', color: '#1e293b', textTransform: 'capitalize' },
  loading: { color: '#94a3b8' },
});
