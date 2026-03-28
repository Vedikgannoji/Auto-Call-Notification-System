import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { useDropzone } from 'react-dropzone';
import { Upload, FileSpreadsheet, Send } from 'lucide-react';

const Attendance = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file && file.type === 'text/csv') {
      setUploadedFile(file);
      toast.success(`File "${file.name}" ready to upload`);
    } else {
      toast.error('Please upload a CSV file');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: false
  });

  const handleUpload = async () => {
    if (!uploadedFile) {
      toast.error('Please select a file first');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/attendance/upload-csv`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      toast.success(response.data.message);
      toast.info('Notifications are being sent in the background');
      setUploadedFile(null);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4 md:p-8" data-testid="attendance-page">
      <div className="mb-6">
        <h1 className="text-4xl font-bold text-[#0F172A] tracking-tight" style={{ fontFamily: 'Manrope' }}>Attendance</h1>
        <p className="text-slate-600 mt-2">Upload attendance records and trigger notifications</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-slate-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="w-5 h-5 text-[#2563EB]" />
              Upload CSV File
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all duration-200 ${
                isDragActive
                  ? 'border-[#2563EB] bg-blue-50'
                  : 'border-slate-300 hover:border-[#2563EB] hover:bg-slate-50'
              }`}
              data-testid="csv-dropzone"
            >
              <input {...getInputProps()} />
              <FileSpreadsheet className="w-16 h-16 mx-auto mb-4 text-slate-400" />
              {isDragActive ? (
                <p className="text-[#2563EB] font-medium">Drop the CSV file here...</p>
              ) : (
                <div>
                  <p className="text-slate-700 font-medium mb-2">Drag & drop CSV file here</p>
                  <p className="text-sm text-slate-500">or click to browse</p>
                </div>
              )}
            </div>

            {uploadedFile && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-700">
                  <strong>Selected:</strong> {uploadedFile.name}
                </p>
                <p className="text-xs text-green-600 mt-1">
                  Size: {(uploadedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
            )}

            <Button
              onClick={handleUpload}
              disabled={!uploadedFile || uploading}
              className="w-full mt-6 bg-[#2563EB] hover:bg-[#1d4ed8] h-12"
              data-testid="upload-csv-button"
            >
              <Send className="w-4 h-4 mr-2" />
              {uploading ? 'Uploading...' : 'Upload & Process'}
            </Button>
          </CardContent>
        </Card>

        <Card className="border-slate-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="text-[#0F172A]">CSV Format Guidelines</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold text-[#0F172A] mb-2">Required Columns:</h3>
              <ul className="list-disc list-inside space-y-1 text-sm text-slate-700">
                <li><code className="bg-white px-2 py-1 rounded">roll_number</code> - Student's roll number</li>
                <li><code className="bg-white px-2 py-1 rounded">date</code> - Date in YYYY-MM-DD format</li>
                <li><code className="bg-white px-2 py-1 rounded">status</code> - present or absent</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold text-[#0F172A] mb-2">Optional Columns:</h3>
              <ul className="list-disc list-inside space-y-1 text-sm text-slate-700">
                <li><code className="bg-white px-2 py-1 rounded">subject</code> - Subject name</li>
              </ul>
            </div>

            <div className="bg-white p-4 rounded-lg border border-slate-200">
              <h3 className="font-semibold text-[#0F172A] mb-2">Example:</h3>
              <pre className="text-xs overflow-x-auto">
{`roll_number,date,status,subject
2021001,2026-01-15,present,Mathematics
2021002,2026-01-15,absent,Mathematics
2021003,2026-01-15,present,Mathematics`}
              </pre>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> Notifications will be automatically sent to parents of absent students after upload.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Attendance;
