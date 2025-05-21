import { useState } from 'react'
import axios from 'axios'
import './App.css'
import {
  Container,
  Typography,
  Button,
  Input,
  CircularProgress,
  Box,
  TextField,
} from '@mui/material'
import GeoMap from './GeoMap.jsx'

function App() {
  const [loading, setLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [message, setMessage] = useState('')
  const [configFileName, setConfigFileName] = useState('')
  const [uploadedFileName, setUploadedFileName] = useState('')
  const [columnValues, setColumnValues] = useState({})
  const [selectedValues, setSelectedValues] = useState({})

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    setSelectedFile(file)
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage('Please select a .zip file.')
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      setLoading(true)
      await axios.post('http://localhost:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setUploadedFileName(selectedFile.name)
      setMessage('✅ File uploaded successfully!')
    } catch (error) {
      console.error('Upload failed:', error)
      setMessage('❌ Upload failed.')
    } finally {
      setLoading(false)
    }
  }

  const callBackend = async (endpoint, payload, handleData) => {
    setLoading(true)
    setMessage('')
    try {
      const response = await axios.post(`http://localhost:5000/${endpoint}`, payload)
      setMessage(response.data.message || '✅ Success')
      if (handleData) {
        handleData(response.data)
      }

    } catch (err) {
      console.error(err)
      setMessage('❌ Error calling endpoint.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Upload & Run Pipeline
      </Typography>

      <Box className="section" sx={{ mb: 3 }}>
        <Typography variant="h6">1. Upload ZIP File</Typography>
        <Input type="file" accept=".zip" onChange={handleFileChange} />
        <Button variant="contained" sx={{ ml: 2 }} onClick={handleUpload}>
          Upload
        </Button>
        {uploadedFileName && (
          <Typography variant="body2" sx={{ mt: 1 }}>
            📁 Uploaded: <strong>{uploadedFileName}</strong>
          </Typography>
        )}
      </Box>

      <Box className="section" sx={{ mb: 3 }}>
        <Typography variant="h6">2. Enter Config File Name</Typography>
        <TextField
          label="e.g., depression_config.json"
          value={configFileName}
          onChange={(e) => setConfigFileName(e.target.value)}
          fullWidth
          size="small"
          sx={{ mt: 1 }}
        />
      </Box>

      <Box className="section" sx={{ mb: 3 }}>
        <Typography variant="h6">3. Run Pipeline</Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 1 }}>
          <Button
            variant="outlined"
            onClick={() =>
              callBackend('extract', {
                zip_file: uploadedFileName,
              })
            }
          >
            Extract zip
          </Button>
          <Button
            variant="outlined"
            onClick={() =>
              callBackend('prepare', {
                config_file: configFileName,
              })
            }
          >
            Process data
          </Button>
          <Button
            variant="outlined"
            onClick={() =>
              callBackend('train', {
                config_file: configFileName,
              })
            }
          >
            Train Models
          </Button>
          <Button
            variant="outlined"
            onClick={() =>
              callBackend(
                'options',
                {
                  config_file: configFileName,
                },
                (data) => {
                  setColumnValues(data)
                  const initialSelections = {}
                  for (const col in data) {
                    initialSelections[col] = ''
                  }
                  setSelectedValues(initialSelections)
                }
              )
            }
          >
            Get Column Values
          </Button>
          <Button
            variant="outlined"
            onClick={() =>
              callBackend('predict', {
                config_file: configFileName,
                values: selectedValues,
              })
            }
          >
            Predict
          </Button>
        </Box>
      </Box>

      {Object.keys(columnValues).length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="h6">Select Values</Typography>
          {Object.entries(columnValues).map(([col, options]) => (
            <Box key={col} sx={{ mb: 2 }}>
              <Typography variant="body1">{col}:</Typography>
              <select
                value={selectedValues[col]}
                onChange={(e) =>
                  setSelectedValues((prev) => ({ ...prev, [col]: e.target.value }))
                }
              >
                <option value="">-- Select --</option>
                {options.map((val) => (
                  <option key={val} value={val}>
                    {val}
                  </option>
                ))}
              </select>
            </Box>
          ))}
        </Box>
      )}

      {loading && (
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <CircularProgress />
        </Box>
      )}
      {!loading && message && (
        <Typography variant="body1" sx={{ mt: 2 }} color="primary">
          {message}
        </Typography>
      )}

      <Box sx={{ mt: 4 }}>
        <GeoMap />
      </Box>
    </Container>
  )
}

export default App
