import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from 'sonner';
import { Settings as SettingsIcon, Plus, Edit } from 'lucide-react';

const Settings = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [formData, setFormData] = useState({
    language: 'english',
    message: ''
  });

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/voice-templates`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTemplates(response.data);
    } catch (error) {
      toast.error('Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');

    try {
      if (editingTemplate) {
        await axios.put(`${API}/voice-templates/${editingTemplate.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Template updated successfully');
      } else {
        await axios.post(`${API}/voice-templates`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Template created successfully');
      }
      setDialogOpen(false);
      resetForm();
      fetchTemplates();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    }
  };

  const handleEdit = (template) => {
    setEditingTemplate(template);
    setFormData({
      language: template.language,
      message: template.message
    });
    setDialogOpen(true);
  };

  const resetForm = () => {
    setFormData({
      language: 'english',
      message: ''
    });
    setEditingTemplate(null);
  };

  if (loading) {
    return <div className="p-8">Loading settings...</div>;
  }

  return (
    <div className="p-4 md:p-8" data-testid="settings-page">
      <div className="mb-6">
        <h1 className="text-4xl font-bold text-[#0F172A] tracking-tight" style={{ fontFamily: 'Manrope' }}>Settings</h1>
        <p className="text-slate-600 mt-2">Configure voice message templates and system preferences</p>
      </div>

      <Card className="border-slate-200">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <SettingsIcon className="w-5 h-5 text-[#2563EB]" />
            Voice Message Templates
          </CardTitle>
          <Dialog open={dialogOpen} onOpenChange={(open) => {
            setDialogOpen(open);
            if (!open) resetForm();
          }}>
            <DialogTrigger asChild>
              <Button className="bg-[#2563EB] hover:bg-[#1d4ed8]" data-testid="add-template-button">
                <Plus className="w-4 h-4 mr-2" />
                Add Template
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold" style={{ fontFamily: 'Manrope' }}>
                  {editingTemplate ? 'Edit Template' : 'Add New Template'}
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="language">Language *</Label>
                  <Select value={formData.language} onValueChange={(value) => setFormData({ ...formData, language: value })}>
                    <SelectTrigger data-testid="template-language-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="english">English</SelectItem>
                      <SelectItem value="hindi">Hindi</SelectItem>
                      <SelectItem value="telugu">Telugu</SelectItem>
                      <SelectItem value="tamil">Tamil</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="message">Voice Message *</Label>
                  <Textarea
                    id="message"
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    required
                    rows={6}
                    placeholder="Dear {parent_name}, your child {student_name} was absent on {date}. Please contact the college for details."
                    className="resize-none"
                    data-testid="template-message-input"
                  />
                  <p className="text-xs text-slate-500">
                    Use placeholders: {'{parent_name}'}, {'{student_name}'}, {'{date}'}
                  </p>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button type="submit" className="flex-1 bg-[#2563EB] hover:bg-[#1d4ed8]" data-testid="submit-template-button">
                    {editingTemplate ? 'Update' : 'Create'} Template
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)} className="flex-1">
                    Cancel
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Language</TableHead>
                  <TableHead>Message Template</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {templates.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center py-8 text-slate-500">
                      No templates found. Add your first template to get started.
                    </TableCell>
                  </TableRow>
                ) : (
                  templates.map((template) => (
                    <TableRow key={template.id} data-testid={`template-row-${template.id}`}>
                      <TableCell className="font-medium capitalize">{template.language}</TableCell>
                      <TableCell className="max-w-md">{template.message}</TableCell>
                      <TableCell className="text-right">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEdit(template)}
                          data-testid={`edit-template-${template.id}`}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Card className="border-slate-200 mt-6 bg-yellow-50">
        <CardHeader>
          <CardTitle>Twilio Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-700 mb-4">
            To enable SMS and voice call notifications, configure your Twilio credentials in the backend .env file:
          </p>
          <div className="bg-white p-4 rounded-lg border border-slate-200">
            <code className="text-sm text-slate-800">
              TWILIO_ACCOUNT_SID=your_account_sid<br />
              TWILIO_AUTH_TOKEN=your_auth_token<br />
              TWILIO_PHONE_NUMBER=your_twilio_number
            </code>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;
