import React, { useState } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Calendar, FileText } from 'lucide-react';

const Reports = () => {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchReport = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/reports/daily-summary?date=${date}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReport(response.data);
      toast.success('Report generated successfully');
    } catch (error) {
      toast.error('Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 md:p-8" data-testid="reports-page">
      <div className="mb-6">
        <h1 className="text-4xl font-bold text-[#0F172A] tracking-tight" style={{ fontFamily: 'Manrope' }}>Reports</h1>
        <p className="text-slate-600 mt-2">Generate daily attendance summary reports</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="border-slate-200 col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-[#2563EB]" />
              Select Date
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="report-date">Report Date</Label>
              <Input
                id="report-date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="h-12"
                data-testid="report-date-input"
              />
            </div>
            <Button
              onClick={fetchReport}
              disabled={loading}
              className="w-full bg-[#2563EB] hover:bg-[#1d4ed8] h-12"
              data-testid="generate-report-button"
            >
              {loading ? 'Generating...' : 'Generate Report'}
            </Button>
          </CardContent>
        </Card>

        {report && (
          <Card className="border-slate-200 col-span-1 lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-[#2563EB]" />
                Daily Summary - {report.date}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                  <p className="text-sm font-medium text-blue-600 uppercase tracking-wider mb-2">Total Records</p>
                  <p className="text-4xl font-bold text-[#0F172A]" style={{ fontFamily: 'Manrope' }}>{report.total_records}</p>
                </div>
                <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                  <p className="text-sm font-medium text-green-600 uppercase tracking-wider mb-2">Present</p>
                  <p className="text-4xl font-bold text-[#0F172A]" style={{ fontFamily: 'Manrope' }}>{report.present_count}</p>
                </div>
                <div className="bg-red-50 p-6 rounded-lg border border-red-200">
                  <p className="text-sm font-medium text-red-600 uppercase tracking-wider mb-2">Absent</p>
                  <p className="text-4xl font-bold text-[#0F172A]" style={{ fontFamily: 'Manrope' }}>{report.absent_count}</p>
                </div>
                <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                  <p className="text-sm font-medium text-purple-600 uppercase tracking-wider mb-2">Notifications</p>
                  <p className="text-4xl font-bold text-[#0F172A]" style={{ fontFamily: 'Manrope' }}>{report.notifications_sent}</p>
                </div>
              </div>

              <div className="mt-6 p-6 bg-gradient-to-br from-blue-50 to-slate-50 rounded-lg border border-slate-200">
                <p className="text-sm font-medium text-slate-600 mb-2">Attendance Percentage</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-5xl font-bold text-[#2563EB]" style={{ fontFamily: 'Manrope' }}>{report.attendance_percentage}%</p>
                  <p className="text-slate-600">of students were present</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Reports;
