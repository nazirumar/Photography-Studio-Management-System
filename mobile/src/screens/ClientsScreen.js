import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, RefreshControl } from 'react-native';
import api from '../services/api';

export default function ClientsScreen() {
  const [clients, setClients] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadClients = async () => {
    try {
      const res = await api.get('/api/v1/clients/');
      setClients(res.data.results || res.data || []);
    } catch (e) { console.log(e); }
  };

  useEffect(() => { loadClients(); }, []);

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <View style={styles.avatar}><Text style={styles.avatarText}>{(item.first_name || '?')[0]}</Text></View>
      <View style={styles.info}>
        <Text style={styles.name}>{item.display_name || `${item.first_name} ${item.last_name}`}</Text>
        <Text style={styles.email}>{item.email}</Text>
      </View>
    </View>
  );

  return (
    <FlatList style={styles.container} data={clients} keyExtractor={(item) => String(item.id || item.pk)} renderItem={renderItem}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={async () => { setRefreshing(true); await loadClients(); setRefreshing(false); }} />}
      ListEmptyComponent={<Text style={styles.empty}>No clients yet</Text>} />
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  card: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', marginHorizontal: 16, marginTop: 10, borderRadius: 12, padding: 14, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 3, elevation: 1 },
  avatar: { width: 44, height: 44, borderRadius: 22, backgroundColor: '#6366f1', justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  avatarText: { color: '#fff', fontSize: 18, fontWeight: '700' },
  info: { flex: 1 },
  name: { fontSize: 15, fontWeight: '700', color: '#1e293b' },
  email: { fontSize: 13, color: '#64748b', marginTop: 2 },
  empty: { textAlign: 'center', color: '#94a3b8', marginTop: 60 },
});
