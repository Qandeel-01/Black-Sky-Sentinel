import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const GEO_ID_MAP = { rahim_yar_khan: "ry_khan" };

export default function Map({ results, onDistrictClick, selectedId }) {
  const mapRef = useRef(null);
  const leafletMap = useRef(null);
  const layerRef = useRef(null);
  const [geoJSON, setGeoJSON] = useState(null);
  const [geoStatus, setGeoStatus] = useState("loading");
  const [geoError, setGeoError] = useState(null);

  useEffect(() => {
    setGeoStatus("loading");
    setGeoError(null);
    fetch("/api/geojson")
      .then((r) => {
        if (!r.ok) throw new Error(`GeoJSON request failed (${r.status})`);
        return r.json();
      })
      .then((data) => {
        data.features.forEach((f) => {
          const raw = f.properties.district_id;
          f.properties.district_id = GEO_ID_MAP[raw] || raw;
        });
        setGeoJSON(data);
        setGeoStatus("ready");
      })
      .catch((e) => {
        console.error("Failed to load GeoJSON:", e);
        setGeoError(e.message);
        setGeoStatus("error");
      });
  }, []);

  useEffect(() => {
    if (leafletMap.current) return;
    leafletMap.current = L.map(mapRef.current, {
      center: [29.8, 71.5],
      zoom: 7,
      zoomControl: true,
    });

    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      {
        attribution: "© OpenStreetMap © CARTO",
        subdomains: "abcd",
        maxZoom: 19,
      }
    ).addTo(leafletMap.current);
  }, []);

  useEffect(() => {
    if (!leafletMap.current || !geoJSON) return;
    if (layerRef.current) layerRef.current.removeFrom(leafletMap.current);

    const scoreMap = {};
    if (results?.length) results.forEach((d) => { scoreMap[d.id] = d; });

    layerRef.current = L.geoJSON(geoJSON, {
      style: (feature) => {
        const d = scoreMap[feature.properties.district_id];
        const color = d ? d.tier_color : "#374151";
        const isSelected = selectedId === feature.properties.district_id;
        return {
          fillColor: color,
          fillOpacity: isSelected ? 0.92 : 0.62,
          color: isSelected ? "#ffffff" : "#111827",
          weight: isSelected ? 2.5 : 1,
        };
      },
      onEachFeature: (feature, layer) => {
        const d = scoreMap[feature.properties.district_id];
        const name = feature.properties.name || feature.properties.district_id;
        const score = d ? `${d.composite.toFixed(1)} — ${d.tier}` : "Run calculation first";
        const rank = d ? `#${d.rank} ` : "";

        layer.bindTooltip(
          `<div class="map-tooltip">
            <strong>${name}</strong>
            <span>${rank}Risk Score: ${score}</span>
            ${d ? `<span>Population: ${d.population_m.toFixed(2)}M</span>` : ""}
          </div>`,
          { sticky: true, className: "leaflet-tooltip-custom" }
        );

        layer.on("click", () => { if (d) onDistrictClick(d); });
        layer.on("mouseover", function () { this.setStyle({ fillOpacity: 0.95, weight: 2 }); });
        layer.on("mouseout", function () {
          this.setStyle({
            fillOpacity: selectedId === feature.properties.district_id ? 0.92 : 0.62,
            weight: selectedId === feature.properties.district_id ? 2.5 : 1,
          });
        });
      },
    }).addTo(leafletMap.current);

    if (!results) {
      try {
        leafletMap.current.fitBounds(layerRef.current.getBounds(), { padding: [20, 20] });
      } catch (_) {}
    }
  }, [geoJSON, results, selectedId, onDistrictClick]);

  return (
    <div className="map-shell" role="region" aria-label="Risk analysis map of Southern Punjab districts">
      <div ref={mapRef} className="map-container" role="img" aria-label="Interactive map showing district risk levels by color" />
      {geoStatus !== "ready" && (
        <div className="map-status-overlay" role="status" aria-live="polite" aria-label={geoStatus === "loading" ? "Loading map data" : "Error loading map"}>
          {geoStatus === "loading" ? (
            <>
              <div className="map-status-title">Loading district map…</div>
              <div className="map-status-sub">Fetching GeoJSON from the backend</div>
            </>
          ) : (
            <>
              <div className="map-status-title">Map unavailable</div>
              <div className="map-status-sub">{geoError || "Unable to load GeoJSON"}</div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
