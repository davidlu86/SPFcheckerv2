from flask import Flask, render_template, request, jsonify
import dns.resolver
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.config['MAX_WORKERS'] = 50  # Adjust based on your needs

def check_spf(domain):
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        spf_records = [r.to_text().strip('"') for r in answers if 'v=spf1' in r.to_text()]
        return {
            'domain': domain,
            'has_spf': bool(spf_records),
            'spf_record': spf_records[0] if spf_records else None,
            'error': None
        }
    except Exception as e:
        return {'domain': domain, 'has_spf': False, 'spf_record': None, 'error': str(e)}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_domains():
    domains = request.json.get('domains', [])
    
    with ThreadPoolExecutor(max_workers=app.config['MAX_WORKERS']) as executor:
        results = list(executor.map(check_spf, domains))
    
    return jsonify(results)

if __name__ == '__main__':
    app.run()
