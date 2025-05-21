import { useState } from 'react'
import axios from 'axios'
import './App.css'
import { Container, Typography, Box, Button, Input, Stack, TextField, Select, MenuItem, CircularProgress, Grid } from '@mui/material'
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
    <Box sx={{ px: 4, py: 2 }}>
      <Typography variant="h4" gutterBottom style={{alignSelf: 'center'}}>
        Run Pipeline
      </Typography>
      <Grid container spacing={4} alignItems="flex-start">
        <Grid item xs={12} md={3}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6">1. Upload ZIP File</Typography>
            <Stack spacing={2}>
              <Input type="file" accept=".zip" onChange={handleFileChange} />
              <Button variant="contained" onClick={async (e) => {
                handleUpload(e)}
                }>Upload</Button>
              {uploadedFileName && (
                <Typography variant="body2">
                  📁 Uploaded: <strong>{uploadedFileName}</strong>
                </Typography>
              )}
            </Stack>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6">2. Config File Name</Typography>
            <TextField
              fullWidth
              placeholder="e.g., depression_config.json"
              value={configFileName}
              onChange={(e) => setConfigFileName(e.target.value)}
              size="small"
            />
          </Box>

          {loading && (
            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <CircularProgress />
            </Box>
          )}
          {!loading && message && (
            <Typography variant="body1" sx={{ mt: 2 }} color="info">
              {message}
            </Typography>
          )}

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6">3. Run Pipeline</Typography>
            <Stack spacing={1}>
              <Button variant="outlined" onClick={() => callBackend('extract', { zip_file: uploadedFileName })}>
                Extract ZIP
              </Button>
              <Button variant="outlined" onClick={() => callBackend('prepare', { config_file: configFileName })}>
                Process Data
              </Button>
              <Button variant="outlined" onClick={() => callBackend('train', { config_file: configFileName })}>
                Train Models
              </Button>
              <Button
                variant="outlined"
                onClick={() =>
                  callBackend('options', { config_file: configFileName }, (data) => {
                    setColumnValues(data)
                    const initialSelections = {}
                    for (const col in data) initialSelections[col] = ''
                    setSelectedValues(initialSelections)
                  })
                }
              >
                Get Column Values
              </Button>
              {Object.keys(columnValues).length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6">Select Values</Typography>
                  <Stack spacing={2}>
                    {Object.entries(columnValues).map(([col, options]) => (
                      <Box key={col}>
                        <Typography variant="body2">{col}:</Typography>
                        <Select
                          fullWidth
                          size="small"
                          value={selectedValues[col]}
                          onChange={(e) =>
                            setSelectedValues((prev) => ({ ...prev, [col]: e.target.value }))
                          }
                          sx={{
                            fontSize: '0.85rem',
                            '.MuiSelect-select': { padding: '6px 10px' },
                            mt: 0.5
                          }}
                        >
                          <MenuItem value="">-- Select --</MenuItem>
                          {options.map((val) => (
                            <MenuItem key={val} value={val}>
                              {val}
                            </MenuItem>
                          ))}</Select>
                      </Box>
                    ))}
                  </Stack>
                </Box>
              )}
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
            </Stack>
          </Box>
        </Grid>
        <Grid item xs={12} md={9} style={{width: '70%', height: '60%'}}>
          <GeoMap />
        </Grid>
      </Grid>
    </Box>
  )


}

export default App
