from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import math
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# ── Load environment variables ───────────────────────────────────────────────
load_dotenv()
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
DATA_PATH = os.getenv('DATA_PATH', 'data')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_PATH = os.getenv('LOG_PATH', 'logs')

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

# ── Logging setup ─────────────────────────────────────────────────────────────
log_dir = os.path.join(os.path.dirname(__file__), LOG_PATH)
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')
handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
app.logger.addHandler(handler)
app.logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# ── Primary data source: real_scores.json (PBS/NEPRA/NDMA/OSM/Open-Meteo) ───
_real_path = os.path.join(os.path.dirname(__file__), DATA_PATH, 'real_scores.json')


def _iso_from_mtime(path):
    return datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def refresh_catalog():
    """Reload the score dataset from disk so JSON edits show up immediately."""
    global DISTRICT_LIST, DISTRICTS, DATA_SOURCES, DATA_META
    with open(_real_path, encoding='utf-8') as f:
        _real = json.load(f)
    DISTRICT_LIST = _real['districts']
    DISTRICTS = {d['id']: d for d in DISTRICT_LIST}
    DATA_SOURCES = _real.get('sources', {})
    DATA_META = {
        'updated_at': _iso_from_mtime(_real_path),
        'district_count': len(DISTRICT_LIST),
        'source_file': 'backend/data/real_scores.json',
    }
    return _real


refresh_catalog()

# ── Criteria ─────────────────────────────────────────────────────────────────
# id must match the keys in real_scores.json → scores{}
CRITERIA = [
    {"id": "blackout", "label": "Complete Blackout Vulnerability",
     "source": "NEPRA State of Industry Report 2023 / MEPCO press releases"},
    {"id": "flood",    "label": "Flood Vulnerability",
     "source": "NDMA Monsoon 2022 Situation Reports"},
    {"id": "heat",     "label": "Heat Stress Index",
     "source": "Open-Meteo Historical Archive May–Sep 2023"},
    {"id": "internet", "label": "4G Coverage Gap",
     "source": "PTA Annual Report 2023"},
    {"id": "health",   "label": "Healthcare Access Deficit",
     "source": "OpenStreetMap via Overpass API"},
    {"id": "infra",    "label": "Infrastructure Gap",
     "source": "OpenStreetMap via Overpass API"},
    {"id": "popexp",   "label": "Population Exposure",
     "source": "PBS Census 2023 × NDMA flood ratio 2022"},
]
CRITERIA_IDS = [c['id'] for c in CRITERIA]

# ── AHP Random Index (Saaty, n = 1..10) ──────────────────────────────────────
AHP_RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12,
          6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}

# ── Scenario presets ──────────────────────────────────────────────────────────
SCENARIOS = {
    "default": {
        "name": "Equal Weight Baseline",
        "description": "All criteria weighted equally — general-purpose baseline.",
        "icon": "⚖️",
        "weights": {c: 5 for c in CRITERIA_IDS},
    },
    "flood_season": {
        "name": "Monsoon / Flood Season",
        "description": "Emphasises flood exposure and population at risk. Suitable June–September.",
        "icon": "🌊",
        "weights": {"blackout": 4, "flood": 10, "heat": 5,
                    "internet": 3, "health": 6, "infra": 4, "popexp": 9},
    },
    "grid_crisis": {
        "name": "Grid Crisis / Blackout",
        "description": "Prioritises load-shedding severity and infrastructure collapse.",
        "icon": "⚡",
        "weights": {"blackout": 10, "flood": 3, "heat": 4,
                    "internet": 6, "health": 5, "infra": 9, "popexp": 5},
    },
    "heat_emergency": {
        "name": "Extreme Heat Emergency",
        "description": "Used during heat waves — weights temperature and healthcare access.",
        "icon": "🌡️",
        "weights": {"blackout": 6, "flood": 2, "heat": 10,
                    "internet": 3, "health": 9, "infra": 4, "popexp": 7},
    },
    "comms_blackout": {
        "name": "Communications Blackout",
        "description": "Prioritises internet gap and infrastructure for coordination.",
        "icon": "📡",
        "weights": {"blackout": 5, "flood": 4, "heat": 2,
                    "internet": 10, "health": 4, "infra": 8, "popexp": 5},
    },
}

# ── Error handling & validation ───────────────────────────────────────────────
def validate_weights(weights_dict):
    """
    Validate that weights dict contains valid numeric values for all criteria.
    Returns (is_valid, error_msg).
    """
    if not isinstance(weights_dict, dict):
        return False, "weights must be a JSON object"
    
    for cid in CRITERIA_IDS:
        if cid not in weights_dict:
            return False, f"missing criterion: {cid}"
        try:
            val = float(weights_dict[cid])
            if not (1 <= val <= 10):
                return False, f"criterion {cid} value {val} out of range [1, 10]"
        except (TypeError, ValueError):
            return False, f"criterion {cid} value is not numeric"
    
    return True, None

def error_response(message, status_code=400, context=None):
    """Return standardized JSON error response."""
    payload = {
        'error': message,
        'status': status_code,
        'timestamp': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
    }
    if context:
        payload['context'] = context
    app.logger.warning(f"API Error {status_code}: {message}")
    return jsonify(payload), status_code

# ── AHP helpers ───────────────────────────────────────────────────────────────
def ahp_weights_and_cr(slider_dict):
    """
    Convert slider values (1–10) to AHP priority weights via geometric-mean
    row method on an implied pairwise matrix a[i][j] = slider[i]/slider[j].
    Also returns Consistency Ratio (CR); CR < 0.10 is considered acceptable.
    """
    ids     = list(slider_dict.keys())
    n       = len(ids)
    vals    = [max(float(slider_dict[i]), 1e-9) for i in ids]

    # Pairwise matrix
    matrix  = [[vals[i] / vals[j] for j in range(n)] for i in range(n)]

    # Priority vector (geometric mean of rows, normalised)
    geo     = [math.prod(row) ** (1 / n) for row in matrix]
    total   = sum(geo)
    w       = [g / total for g in geo]

    # λmax → CI → CR
    aw      = [sum(matrix[i][j] * w[j] for j in range(n)) for i in range(n)]
    lam_max = sum(aw[i] / w[i] for i in range(n)) / n
    ci      = (lam_max - n) / (n - 1) if n > 1 else 0.0
    ri      = AHP_RI.get(n, 1.49)
    cr      = ci / ri if ri > 0 else 0.0

    return {ids[i]: round(w[i], 6) for i in range(n)}, round(cr, 4)

def risk_tier(score):
    """score is 0–100."""
    if score >= 75: return "Critical"
    if score >= 50: return "High"
    if score >= 25: return "Moderate"
    return "Low"

def tier_color(tier):
    return {"Critical": "#dc2626", "High": "#ea580c",
            "Moderate": "#ca8a04", "Low": "#16a34a"}[tier]

def score_district(d, weights):
    """Return (composite_0_to_100, breakdown_dict)."""
    breakdown = {}
    composite = 0.0
    for c in CRITERIA:
        s = d['scores'][c['id']]          # already 0–100
        w = weights[c['id']]
        contrib = s * w
        composite += contrib
        breakdown[c['id']] = {
            "label":    c['label'],
            "source":   c['source'],
            "score":    round(s, 1),
            "weight":   round(w, 4),
            "weighted": round(contrib, 2),
        }
    return round(composite, 2), breakdown

def _parse_weights_from_qs(qs_string):
    """Parse 'blackout:8,flood:7,...' from query string into dict."""
    raw = {c: 5 for c in CRITERIA_IDS}
    if qs_string:
        for part in qs_string.split(','):
            if ':' in part:
                k, v = part.split(':', 1)
                k = k.strip()
                if k in raw:
                    try:
                        raw[k] = max(1, min(10, int(v)))
                    except ValueError:
                        pass
    return raw

# ── API routes ────────────────────────────────────────────────────────────────

@app.route('/api/real-scores', methods=['GET'])
def get_real_scores():
    refresh_catalog()
    with open(_real_path, encoding='utf-8') as f:
        payload = json.load(f)
    payload['meta'] = DATA_META
    return jsonify(payload)

@app.route('/api/settlements', methods=['GET'])
def get_settlements():
    path = os.path.join(os.path.dirname(__file__), DATA_PATH, 'settlements.json')
    if not os.path.exists(path):
        return jsonify({'error': 'Run fetch_settlements.py first'}), 404
    with open(path, encoding='utf-8') as f:
        return jsonify(json.load(f))

@app.route('/api/criteria', methods=['GET'])
def get_criteria():
    refresh_catalog()
    return jsonify({"criteria": CRITERIA, "sources": DATA_SOURCES, "meta": DATA_META})

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    return jsonify(SCENARIOS)

@app.route('/api/districts', methods=['GET'])
def get_districts():
    refresh_catalog()
    return jsonify({"districts": DISTRICT_LIST, "sources": DATA_SOURCES, "meta": DATA_META})

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    POST body (JSON):
      { "weights": { "blackout": 8, "flood": 7, ... },  // 1–10 slider values
        "scenario": "flood_season"                        // optional preset override
      }
    Returns AHP-weighted composite scores for all 11 districts + CR diagnostic.
    Weights from real_scores.json (NEPRA/NDMA/OSM/Open-Meteo) — not districts.json.
    """
    try:
        refresh_catalog()
    except Exception as e:
        app.logger.error(f"Failed to refresh catalog: {e}")
        return error_response("Failed to load data", 500, str(e))
    
    try:
        body        = request.get_json()
        if body is None:
            body = {}
    except Exception:
        return error_response("Invalid JSON in request body", 400)
    
    scenario_id = body.get('scenario')

    if scenario_id and scenario_id in SCENARIOS:
        raw_weights = SCENARIOS[scenario_id]['weights'].copy()
    else:
        raw_weights = body.get('weights', {c: 5 for c in CRITERIA_IDS})
        
        # Validate weights
        is_valid, error_msg = validate_weights(raw_weights)
        if not is_valid:
            return error_response(error_msg, 400, 
                                 {'expected_criteria': CRITERIA_IDS})
        
        # Clamp to [1, 10]
        for c in CRITERIA_IDS:
            raw_weights[c] = max(1, min(10, float(raw_weights[c])))

    weights, cr = ahp_weights_and_cr(raw_weights)
    cr_ok       = cr < 0.10

    results = []
    for d in DISTRICT_LIST:
        composite, breakdown = score_district(d, weights)
        tier        = risk_tier(composite)
        top_drivers = sorted(breakdown.items(),
                             key=lambda x: x[1]['weighted'], reverse=True)[:2]
        results.append({
            "id":          d['id'],
            "name":        d['name'],
            "lat":         d['lat'],
            "lng":         d['lng'],
            "population_m": d['population_m'],
            "area_km2":    d['area_km2'],
            "composite":   composite,
            "tier":        tier,
            "tier_color":  tier_color(tier),
            "breakdown":   breakdown,
            "top_drivers": [{"id": k, "label": v['label'],
                             "contribution": v['weighted']}
                            for k, v in top_drivers],
            "raw":         d['raw'],
        })

    results.sort(key=lambda x: x['composite'], reverse=True)
    for i, r in enumerate(results):
        r['rank'] = i + 1

    return jsonify({
        "weights":        weights,
        "raw_weights":    raw_weights,
        "ahp_cr":         cr,
        "ahp_cr_ok":      cr_ok,
        "ahp_cr_note":    ("Consistent (CR < 0.10)" if cr_ok
                           else f"CR = {cr:.3f} > 0.10 — consider rebalancing"),
        "scenario":       scenario_id,
        "districts":      results,
        "top_district":   results[0]['name'] if results else None,
        "critical_count": sum(1 for r in results if r['tier'] == 'Critical'),
        "high_count":     sum(1 for r in results if r['tier'] == 'High'),
        "data_sources":   DATA_SOURCES,
        "meta":           DATA_META,
    })

@app.route('/api/report/<district_id>', methods=['GET'])
def district_report(district_id):
    """
    GET /api/report/rajanpur
    GET /api/report/rajanpur?weights=blackout:8,flood:9,heat:3,internet:5,health:6,infra:4,popexp:7
    Full diagnostic report for one district with regional comparison.
    """
    refresh_catalog()
    if district_id not in DISTRICTS:
        return jsonify({'error': f'Unknown district: {district_id}',
                        'valid_ids': list(DISTRICTS.keys())}), 404

    d           = DISTRICTS[district_id]
    raw_weights = _parse_weights_from_qs(request.args.get('weights', ''))
    weights, cr = ahp_weights_and_cr(raw_weights)
    composite, breakdown = score_district(d, weights)
    tier        = risk_tier(composite)

    # Regional rank and average under these weights
    all_scores = sorted(
        [(od['id'], score_district(od, weights)[0]) for od in DISTRICT_LIST],
        key=lambda x: x[1], reverse=True
    )
    rank        = next(i + 1 for i, (did, _) in enumerate(all_scores)
                       if did == district_id)
    regional_avg = sum(s for _, s in all_scores) / len(all_scores)

    return jsonify({
        "id":            district_id,
        "name":          d['name'],
        "lat":           d['lat'],
        "lng":           d['lng'],
        "population_m":  d['population_m'],
        "area_km2":      d['area_km2'],
        "composite":     composite,
        "tier":          tier,
        "tier_color":    tier_color(tier),
        "rank":          rank,
        "rank_of":       len(DISTRICT_LIST),
        "regional_avg":  round(regional_avg, 2),
        "vs_avg":        round(composite - regional_avg, 2),
        "breakdown":     breakdown,
        "raw":           d['raw'],
        "ahp_cr":        cr,
        "weights_used":  weights,
        "data_sources":  DATA_SOURCES,
        "meta":          DATA_META,
    })

@app.route('/api/compare', methods=['POST'])
def compare_scenarios():
    """
    POST { "scenarios": ["flood_season", "grid_crisis"] }
    Side-by-side district rankings for each named scenario.
    Omit body to compare all five presets.
    """
    try:
        refresh_catalog()
    except Exception as e:
        app.logger.error(f"Failed to refresh catalog: {e}")
        return error_response("Failed to load data", 500, str(e))
    
    try:
        body = request.get_json()
        if body is None:
            body = {}
    except Exception:
        return error_response("Invalid JSON in request body", 400)
    
    scenario_ids = body.get('scenarios', list(SCENARIOS.keys()))
    
    # Validate scenario IDs
    if not isinstance(scenario_ids, list):
        return error_response("scenarios must be a list", 400,
                             {'valid_scenarios': list(SCENARIOS.keys())})
    
    invalid = [s for s in scenario_ids if s not in SCENARIOS]
    if invalid:
        return error_response(f"Invalid scenarios: {invalid}", 400,
                             {'valid_scenarios': list(SCENARIOS.keys())})

    comparison = {}
    for sid in scenario_ids:
        weights, cr = ahp_weights_and_cr(SCENARIOS[sid]['weights'])
        ranked = []
        for d in DISTRICT_LIST:
            comp, _ = score_district(d, weights)
            ranked.append({"id": d['id'], "name": d['name'],
                           "composite": comp, "tier": risk_tier(comp)})
        ranked.sort(key=lambda x: x['composite'], reverse=True)
        for i, r in enumerate(ranked):
            r['rank'] = i + 1
        comparison[sid] = {
            "name":     SCENARIOS[sid]['name'],
            "icon":     SCENARIOS[sid]['icon'],
            "cr":       cr,
            "rankings": ranked,
        }

    return jsonify(comparison)

@app.route('/health', methods=['GET'])
def health():
    refresh_catalog()
    return jsonify({
        'status':    'online',
        'region':    'Southern Punjab, Pakistan',
        'districts': len(DISTRICT_LIST),
        'data':      'real_scores.json — NEPRA/NDMA/PBS/PTA/OSM/Open-Meteo',
        'meta':      DATA_META,
        'endpoints': [
            'GET  /api/real-scores',
            'GET  /api/criteria',
            'GET  /api/districts',
            'GET  /api/scenarios',
            'GET  /api/settlements',
            'POST /api/calculate',
            'GET  /api/report/<district_id>',
            'POST /api/compare',
        ],
    })

@app.route('/api/geojson', methods=['GET'])
def get_geojson():
    """Serve the Southern Punjab GeoJSON used by the frontend map."""
    path = os.path.join(os.path.dirname(__file__), DATA_PATH, 'southern_punjab.geojson')
    if not os.path.exists(path):
        return jsonify({'error': 'GeoJSON not found', 'path': path}), 404
    with open(path, encoding='utf-8') as f:
        return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
