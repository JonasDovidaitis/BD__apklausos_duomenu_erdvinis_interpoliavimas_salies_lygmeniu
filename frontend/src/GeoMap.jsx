import { MapContainer, GeoJSON  } from 'react-leaflet'
import { useEffect, useRef, useState } from 'react'
import 'leaflet/dist/leaflet.css'
import proj4 from 'proj4'
import { createLayerComponent } from '@react-leaflet/core'
import L from 'leaflet'
import { Box, Typography, Select, MenuItem, Input } from '@mui/material'
import { scaleLinear } from 'd3-scale'
import { interpolateRdYlGn } from 'd3-scale-chromatic'

// Define EPSG:3346 (Lithuania / LKS94)
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
  if (!Array.isArray(coords)) return coords
  if (typeof coords[0][0] === 'number') {
    return coords.map(([x, y]) => proj4(from, to, [x, y]))
  }
  return coords.map(reprojectCoords)
}

function getMinMaxFromGeoJSON(geojson, key) {
  const values = geojson.features
    .map(f => f.properties[key])
    .filter(v => v !== null && v !== undefined && v !== -1)

  const min = Math.min(...values)
  const max = Math.max(...values)
  return { min, max }
}

export default function GeoMap() {
  const [geoData, setGeoData] = useState(null)
  const [selectedPrediction, setSelectedPrediction] = useState('prediction_rf')
  const [colorScale, setColorScale] = useState(null)
  const [domain, setDomain] = useState([0, 1])
  const [boundaryData, setBoundaryData] = useState(null)
  const [boundaryKey, setBoundaryKey] = useState(Date.now())
  const [predictionsKey, setPredictionsKey] = useState(Date.now())
  const mapRef = useRef(null)

  const handleGeojsonUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      const json = JSON.parse(event.target.result)
      json.features = json.features.map((feature) => {
        const type = feature.geometry.type
        if (type === 'Polygon' || type === 'MultiPolygon') {
          feature.geometry.coordinates = reprojectCoords(feature.geometry.coordinates)
        }
        return feature
      })

      const { min, max } = getMinMaxFromGeoJSON(json, selectedPrediction)
      const newColorScale = scaleLinear()
        .domain([min, max])
        .range([interpolateRdYlGn(1), interpolateRdYlGn(0)])

      setDomain([min, max])
      setColorScale(() => newColorScale)
      setGeoData(json)
      setPredictionsKey(Date.now())
    }
    reader.readAsText(file)
  }

  const handleBoundaryUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      const json = JSON.parse(event.target.result)

      json.features = json.features.map((feature) => {
        const type = feature.geometry.type
        if (type === 'Polygon' || type === 'MultiPolygon') {
          feature.geometry.coordinates = reprojectCoords(feature.geometry.coordinates)
        }
        return feature
      })

      setBoundaryData(json)
      setBoundaryKey(Date.now())
    }
    reader.readAsText(file)
  }

  useEffect(() => {
    if (geoData && mapRef.current) {
      try {
        const bounds = L.geoJSON(geoData).getBounds()
        if (bounds.isValid()) {
          mapRef.current.fitBounds(bounds)
        }
      } catch (err) {
        console.error('Failed to fit bounds:', err)
      }
    }
  }, [geoData])

  useEffect(() => {
    if (!geoData) return
    const { min, max } = getMinMaxFromGeoJSON(geoData, selectedPrediction)
    const newColorScale = scaleLinear()
      .domain([min, max])
      .range([interpolateRdYlGn(1), interpolateRdYlGn(0)])
    setDomain([min, max])
    setColorScale(() => newColorScale)
  }, [selectedPrediction, geoData])

  const getColor = (value) => {
    if (!colorScale || value === null || value === undefined || value === -1) return '#ccc'
    return colorScale(value)
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
    <Box style={{ width: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '3em', paddingBottom: '2em' }}>
        <div>
          <Typography variant="h6">Upload Boundaries geojson file</Typography>
          <Input type="file" accept=".geojson" onChange={handleBoundaryUpload} />
        </div>
        <div>
          <Typography variant="h6">Upload GeoJSON and View Predictions</Typography>
          <Input type="file" accept=".geojson" onChange={handleGeojsonUpload} />
        </div>
        {geoData && (
          <div>
            <Typography>Select prediction type:</Typography>
            <Select
              value={selectedPrediction}
              onChange={(e) => {
                setSelectedPrediction(e.target.value); 
                setPredictionsKey((key) => key * -1)
              }}
              size="small"
              sx={{ mt: 1 }}
            >
              <MenuItem value="prediction_rf">Random Forest</MenuItem>
              <MenuItem value="prediction_svm">SVM</MenuItem>
              <MenuItem value="prediction_gnn">GNN</MenuItem>
            </Select>
          </div>
        )}
      </div>

      {geoData && (
        <Box sx={{ display: 'flex', gap: 4 }}>
          <Box sx={{ width: '60vw', height: '75vh' }}>
            <MapContainer
              whenCreated={(mapInstance) => {
                mapRef.current = mapInstance
              }}
              center={[55.2, 23.9]}
              zoom={6}
              style={{ height: '100%', width: '100%', background: '#fff' }}
              zoomControl={true}
            >
              {boundaryData && (
                <GeoJSON
                  key={boundaryKey}
                  data={boundaryData}
                  style={{
                    color: '#222',
                    weight: 0.5,
                    fillOpacity: 0,
                    interactive: false
                  }}
                />
              )}
              <CanvasGeoJSON
                key={predictionsKey}
                data={geoData}
                style={styleFeature}
                onEachFeature={onEachFeature}
              />
            </MapContainer>
          </Box>  
          {colorScale && (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                gap: 1,
                mt: 2,
              }}
            >
              <Box
                sx={{
                  width: '20px',
                  height: 200,
                  background: `linear-gradient(to top, ${interpolateRdYlGn(1)}, ${interpolateRdYlGn(0.75)}, ${interpolateRdYlGn(0.5)}, ${interpolateRdYlGn(0.25)}, ${interpolateRdYlGn(0)} )`,
                  border: '1px solid #ccc',
                  borderRadius: 1,
                }}
              />
              <Box
                sx={{
                  height: 200,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  fontSize: '0.8rem',
                  alignItems: 'flex-start',
                }}
              >
                <span>{domain[1].toFixed(2)}</span>
                <span>{domain[0].toFixed(2)}</span>
              </Box>
            </Box>
          )}
        </Box>
      )}
    </Box>
  )
}
