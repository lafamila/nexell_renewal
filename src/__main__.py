from app import app
from flask import send_from_directory
from dotenv import load_dotenv
load_dotenv()

@app.route('/.well-known/acme-challenge/<test>')
def acme_challenge(test):
    print(test)
    return send_from_directory('static/challenge/acme-challenge', test)

app.run(host='0.0.0.0', port=5001, debug=True)

#docker run --rm -d --network host -v /var/lib/letsencrypt/.well-known/acme-challenge:/erp-service/app/static/challenge/acme-challenge -v /volume1/넥셀시스템/ERP/:/erp-service/app/static/files -e 'DB_USER=root' -e 'DB_PASSWORD=P@ssw0rd0106' -e 'DB_HOST=localhost' -e 'DB_PORT=3307' -e 'DB_SCHEME=nexell_erp_new'  -p 5001:5001 new_erp