import { MapContainer } from 'react-leaflet'
import { useState } from 'react'
import 'leaflet/dist/leaflet.css'
import proj4 from 'proj4'
import { createLayerComponent } from '@react-leaflet/core'
import L from 'leaflet'
import { Box, Typography, Select, MenuItem } from '@mui/material'

// EPSG:3346 - Lithuania (LKS94)
proj4.defs(
  "EPSG:3346",
  "+proj=tmerc +lat_0=0 +lon_0=24 +k=0.9998 +x_0=500000 +y_0=0 +ellps=GRS80 +units=m +no_defs"
)
const from = proj4("EPSG:3346")
const to = proj4("EPSG:4326")

const CanvasGeoJSON = createLayerComponent((props, context) => {
  const layer = L.geoJSON(props.data, {
    style: props.style,
    onEachFeature: props.onEachFeature,
    renderer: L.canvas()
  })
  return { instance: layer, context }
})

function reprojectCoords(coords) {
  if (typeof coords[0][0] === 'number') {
    return coords.map(coord => proj4(from, to, coord))
  } else {
    return coords.map(reprojectCoords)
  }
}

export default function GeoMap() {
  const [geoData, setGeoData] = useState(null)
  const [selectedPrediction, setSelectedPrediction] = useState('prediction_rf')

  const handleGeojsonUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      const json = JSON.parse(event.target.result)
      json.features = json.features.map((feature) => {
        if (['Polygon', 'MultiPolygon'].includes(feature.geometry.type)) {
          feature.geometry.coordinates = reprojectCoords(feature.geometry.coordinates)
        }
        return feature
      })
      setGeoData(json)
    }
    reader.readAsText(file)
  }

  const getColor = (value) => {
    if (value === undefined || value === null || value === -1) return '#ccc'
    const colors = ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850']
    return colors[value] || '#000'
  }

  const styleFeature = (feature) => {
    const value = feature.properties[selectedPrediction]
    return {
      fillColor: getColor(value),
      color: '#444',
      weight: 0.3,
      fillOpacity: 0.7,
    }
  }

  const onEachFeature = (feature, layer) => {
    const val = feature.properties[selectedPrediction]
    layer.bindTooltip(`${selectedPrediction}: ${val}`, { sticky: true })
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 1 }}>
        Upload GeoJSON and View Predictions
      </Typography>

      <input
        type="file"
        accept=".geojson"
        onChange={handleGeojsonUpload}
        style={{ marginBottom: '1rem' }}
      />

      {geoData && (
        <>
          <Box sx={{ mb: 2 }}>
            <Typography>Select prediction type:</Typography>
            <Select
              value={selectedPrediction}
              onChange={(e) => setSelectedPrediction(e.target.value)}
              size="small"
              sx={{ minWidth: 200, mt: 1 }}
            >
              <MenuItem value="prediction_rf">Random Forest</MenuItem>
              <MenuItem value="prediction_svm">SVM</MenuItem>
              <MenuItem value="prediction_gnn">GNN</MenuItem>
            </Select>
          </Box>

          <Box sx={{ width: '800px', height: '800px', background: '#fff', borderRadius: 1, overflow: 'hidden' }}>
            <MapContainer
              center={[55.2, 23.9]}
              zoom={7}
              style={{ height: '100%', width: '100%', background: '#fff' }}
              zoomControl={true}
            >
              <CanvasGeoJSON
                key={selectedPrediction}
                data={geoData}
                style={styleFeature}
                onEachFeature={onEachFeature}
              />
            </MapContainer>
          </Box>
        </>
      )}
    </Box>
  )
}
