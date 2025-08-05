from flask import Flask, jsonify, request
from compass_engine import CompassEngine

app = Flask(__name__)
compass = CompassEngine()

@app.route('/api/agencies', methods=['GET'])
def get_agencies():
    service_type = request.args.get('service_type')
    agencies = compass.get_agencies(service_type)
    return jsonify(agencies)

@app.route('/api/market-insights', methods=['GET'])
def get_market_insights():
    region = request.args.get('region')
    insights = compass.get_market_insights(region)
    return jsonify(insights)

@app.route('/api/services', methods=['GET'])
def get_services():
    service_type = request.args.get('service_type')
    services = compass.get_services(service_type)
    return jsonify(services)

@app.route('/api/project-phases', methods=['GET'])
def get_project_phases():
    project_type = request.args.get('project_type', 'general')
    phases = compass.get_project_phases(project_type)
    return jsonify(phases)

@app.route('/api/competitors', methods=['GET'])
def get_competitors():
    industry = request.args.get('industry')
    competitors = compass.get_competitors(industry)
    return jsonify(competitors)

@app.route('/api/analyze-project', methods=['POST'])
def analyze_project():
    requirements = request.json
    analysis = compass.analyze_project(requirements)
    return jsonify(analysis)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)