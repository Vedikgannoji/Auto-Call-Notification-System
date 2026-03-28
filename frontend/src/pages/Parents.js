import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Plus, Edit, Trash2, Phone } from 'lucide-react';

const Parents = () => {
  const [parents, setParents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingParent, setEditingParent] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    phone_number: '',
    email: '',
    relationship: 'parent',
    preferred_language: 'english'
  });

  useEffect(() => {
    fetchParents();
  }, []);

  const fetchParents = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/parents`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setParents(response.data);
    } catch (error) {
      toast.error('Failed to load parents');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');

    try {
      if (editingParent) {
        await axios.put(`${API}/parents/${editingParent.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Parent updated successfully');
      } else {
        await axios.post(`${API}/parents`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Parent created successfully');
      }
      setDialogOpen(false);
      resetForm();
      fetchParents();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    }
  };

  const handleEdit = (parent) => {
    setEditingParent(parent);
    setFormData({
      name: parent.name,
      phone_number: parent.phone_number,
      email: parent.email || '',
      relationship: parent.relationship,
      preferred_language: parent.preferred_language
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this parent?')) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/parents/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Parent deleted successfully');
      fetchParents();
    } catch (error) {
      toast.error('Failed to delete parent');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      phone_number: '',
      email: '',
      relationship: 'parent',
      preferred_language: 'english'
    });
    setEditingParent(null);
  };

  if (loading) {
    return <div className="p-8">Loading parents...</div>;
  }

  return (
    <div className="p-4 md:p-8" data-testid="parents-page">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-4xl font-bold text-[#0F172A] tracking-tight" style={{ fontFamily: 'Manrope' }}>Parents</h1>
          <p className="text-slate-600 mt-2">Manage parent contact information</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) resetForm();
        }}>
          <DialogTrigger asChild>
            <Button className="bg-[#2563EB] hover:bg-[#1d4ed8]" data-testid="add-parent-button">
              <Plus className="w-4 h-4 mr-2" />
              Add Parent
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold" style={{ fontFamily: 'Manrope' }}>
                {editingParent ? 'Edit Parent' : 'Add New Parent'}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  data-testid="parent-name-input"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="phone_number">Phone Number *</Label>
                  <Input
                    id="phone_number"
                    type="tel"
                    value={formData.phone_number}
                    onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                    required
                    placeholder="+91XXXXXXXXXX"
                    data-testid="parent-phone-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    data-testid="parent-email-input"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="relationship">Relationship *</Label>
                  <Select value={formData.relationship} onValueChange={(value) => setFormData({ ...formData, relationship: value })}>
                    <SelectTrigger data-testid="parent-relationship-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="parent">Parent</SelectItem>
                      <SelectItem value="father">Father</SelectItem>
                      <SelectItem value="mother">Mother</SelectItem>
                      <SelectItem value="guardian">Guardian</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="preferred_language">Preferred Language *</Label>
                  <Select value={formData.preferred_language} onValueChange={(value) => setFormData({ ...formData, preferred_language: value })}>
                    <SelectTrigger data-testid="parent-language-select">
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
              </div>

              <div className="flex gap-3 pt-4">
                <Button type="submit" className="flex-1 bg-[#2563EB] hover:bg-[#1d4ed8]" data-testid="submit-parent-button">
                  {editingParent ? 'Update' : 'Create'} Parent
                </Button>
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)} className="flex-1">
                  Cancel
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="border-slate-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Phone className="w-5 h-5 text-[#2563EB]" />
            All Parents ({parents.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Phone Number</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Relationship</TableHead>
                  <TableHead>Language</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {parents.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-slate-500">
                      No parents found. Add your first parent to get started.
                    </TableCell>
                  </TableRow>
                ) : (
                  parents.map((parent) => (
                    <TableRow key={parent.id} data-testid={`parent-row-${parent.id}`}>
                      <TableCell className="font-medium">{parent.name}</TableCell>
                      <TableCell>{parent.phone_number}</TableCell>
                      <TableCell>{parent.email || 'N/A'}</TableCell>
                      <TableCell className="capitalize">{parent.relationship}</TableCell>
                      <TableCell className="capitalize">{parent.preferred_language}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex gap-2 justify-end">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleEdit(parent)}
                            data-testid={`edit-parent-${parent.id}`}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDelete(parent.id)}
                            data-testid={`delete-parent-${parent.id}`}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
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

export default Parents;
