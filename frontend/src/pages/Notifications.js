import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from 'sonner';
import { Bell, RefreshCw, CheckCircle, XCircle, Phone, MessageSquare } from 'lucide-react';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

  const fetchNotifications = async () => {
    try {
      const token = localStorage.getItem('token');
      const url = filter === 'all' ? `${API}/notifications` : `${API}/notifications?status=${filter}`;
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(response.data);
    } catch (error) {
      toast.error('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async (notificationId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/notifications/${notificationId}/retry`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success(response.data.message);
      fetchNotifications();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Retry failed');
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      sent: 'bg-green-100 text-green-700 border-green-200',
      failed: 'bg-red-100 text-red-700 border-red-200',
      pending: 'bg-yellow-100 text-yellow-700 border-yellow-200'
    };
    return (
      <Badge className={styles[status] || styles.pending}>
        {status.toUpperCase()}
      </Badge>
    );
  };

  const getTypeIcon = (type) => {
    return type === 'sms' ? <MessageSquare className="w-4 h-4" /> : <Phone className="w-4 h-4" />;
  };

  if (loading) {
    return <div className="p-8">Loading notifications...</div>;
  }

  return (
    <div className="p-4 md:p-8" data-testid="notifications-page">
      <div className="mb-6">
        <h1 className="text-4xl font-bold text-[#0F172A] tracking-tight" style={{ fontFamily: 'Manrope' }}>Notifications</h1>
        <p className="text-slate-600 mt-2">View and manage notification history</p>
      </div>

      <div className="flex gap-3 mb-6">
        <Button
          variant={filter === 'all' ? 'default' : 'outline'}
          onClick={() => setFilter('all')}
          className={filter === 'all' ? 'bg-[#2563EB]' : ''}
          data-testid="filter-all-button"
        >
          All
        </Button>
        <Button
          variant={filter === 'sent' ? 'default' : 'outline'}
          onClick={() => setFilter('sent')}
          className={filter === 'sent' ? 'bg-green-600 hover:bg-green-700' : ''}
          data-testid="filter-sent-button"
        >
          <CheckCircle className="w-4 h-4 mr-2" />
          Sent
        </Button>
        <Button
          variant={filter === 'failed' ? 'default' : 'outline'}
          onClick={() => setFilter('failed')}
          className={filter === 'failed' ? 'bg-red-600 hover:bg-red-700' : ''}
          data-testid="filter-failed-button"
        >
          <XCircle className="w-4 h-4 mr-2" />
          Failed
        </Button>
      </div>

      <Card className="border-slate-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-[#2563EB]" />
            Notification History ({notifications.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Phone Number</TableHead>
                  <TableHead>Message</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Retry Count</TableHead>
                  <TableHead>Sent At</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {notifications.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-slate-500">
                      No notifications found.
                    </TableCell>
                  </TableRow>
                ) : (
                  notifications.map((notification) => (
                    <TableRow key={notification.id} data-testid={`notification-row-${notification.id}`}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getTypeIcon(notification.type)}
                          <span className="capitalize">{notification.type}</span>
                        </div>
                      </TableCell>
                      <TableCell>{notification.phone_number}</TableCell>
                      <TableCell className="max-w-xs truncate">{notification.message}</TableCell>
                      <TableCell>{getStatusBadge(notification.status)}</TableCell>
                      <TableCell>{notification.retry_count}</TableCell>
                      <TableCell>
                        {notification.sent_at
                          ? new Date(notification.sent_at).toLocaleString()
                          : 'N/A'}
                      </TableCell>
                      <TableCell className="text-right">
                        {notification.status === 'failed' && notification.retry_count < 3 && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRetry(notification.id)}
                            data-testid={`retry-notification-${notification.id}`}
                          >
                            <RefreshCw className="w-4 h-4 mr-1" />
                            Retry
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Notifications;
