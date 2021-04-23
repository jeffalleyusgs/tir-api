secure_scheme_headers = {'X-FORWARDED-PROTOCOL': 'ssl', 'X-FORWARDED-PROTO': 'https', 'X-FORWARDED-SSL': 'on'}
bind= "0.0.0.0:8080"
workers=4
max_requests=50
max_requests_jitter=10