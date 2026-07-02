// Simplified district polygons for Southern Punjab, Pakistan
// Approximate boundaries based on GADM/OCHA administrative data
// Replace with official GADM shapefiles for production accuracy

const southernPunjabGeoJSON = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: { district_id: "layyah", name: "Layyah", division: "D.G. Khan" },
      geometry: {
        type: "Polygon",
        coordinates: [[[70.3,32.2],[71.9,32.2],[71.9,30.8],[70.3,30.8],[70.3,32.2]]]
      }
    },
    {
      type: "Feature",
      properties: { district_id: "dg_khan", name: "Dera Ghazi Khan", division: "D.G. Khan" },
      geometry: {
        type: "Polygon",
        coordinates: [[[69.3,30.8],[71.0,30.8],[71.2,29.8],[70.8,29.0],[69.3,29.2],[69.3,30.8]]]
      }
    },
    {
      type: "Feature",
      properties: { district_id: "muzaffargarh", name: "Muzaffargarh", division: "D.G. Khan" },
      geometry: {
        type: "Polygon",
        coordinates: [[[71.0,30.8],[71.9,30.8],[71.9,29.6],[71.2,29.8],[71.0,30.8]]]
      }
    },
    {
      type: "Feature",
      properties: { district_id: "multan", name: "Multan", division: "Multan" },
      geometry: {
        type: "Polygon",
        coordinates: [[[71.9,30.8],[72.5,30.8],[72.5,29.6],[71.9,29.6],[71.9,30.8]]]
      }
    },
    {
      type: "Feature",
      properties: { district_id: "khanewal", name: "Khanewal", division: "Multan" },
      geometry: {
        type: "Polygon",
        coordinates: [[[72.5,31.2],[73.2,31.2],[73.2,30.0],[72.5,30.0],[72.5,31.2]]]
      }
    },
    {
      type: "Feature",
      properties: { district_id: "lodhran", name: "Lodhran", division: "Multan" },
      geometry: {
        type: "Polygon",
        coordinates: [[[71.2,29.8],[72.5,29.8],[72.5,29.0],[71.2,29.0],[71.2,29.8]]]
      }
    },
    {
      type: "Feature",
      properties: { district_id: "vehari", name: "Vehari", division: "Multan" },
      geometry: {
        type: "Polygon",
        coordinates: [[[72.5,30.0],[73.5,30.0],[73.5,29.2],[72.5,29.2],[72.5,30.0]]]
      }
    },
    {
      type: "Feature",
      properties: { district_id: "bahawalpur", name: "Bahawalpur", division: "Bahawalpur" },
      geometry: {
        type: "Polygon",
        coordinates: [[[70.5,29.0],[72.5,29.0],[73.0,28.2],[71.5,27.8],[70.0,28.0],[70.5,29.0]]]
      }
    },
    {
      type: "Feature",
      properties: { district_id: "bahawalnagar", name: "Bahawalnagar", division: "Bahawalpur" },
      geometry: {
        type: "Polygon",
        coordinates: [[[73.2,30.5],[74.5,30.5],[74.5,29.0],[73.2,29.0],[73.2,30.5]]]
      }
    },
    {
      type: "Feature",
      properties: { district_id: "rajanpur", name: "Rajanpur", division: "D.G. Khan" },
      geometry: {
        type: "Polygon",
        coordinates: [[[69.3,29.2],[70.8,29.0],[71.0,28.2],[70.0,27.5],[69.0,27.8],[69.3,29.2]]]
      }
    },
    {
      type: "Feature",
      properties: { district_id: "rahim_yar_khan", name: "Rahim Yar Khan", division: "Bahawalpur" },
      geometry: {
        type: "Polygon",
        coordinates: [[[70.0,28.0],[72.0,28.2],[73.0,28.0],[73.0,27.2],[70.5,27.0],[69.5,27.4],[70.0,28.0]]]
      }
    }
  ]
};

export default southernPunjabGeoJSON;
