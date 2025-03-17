#!/usr/bin/env python3

import os
import re

from bitwarden_sdk import BitwardenClient

BWS_UUID_MATCH = re.compile(r'\$BWS\{([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})\}', re.IGNORECASE)
BWS_ACCESS_TOKEN = os.getenv('BWS_ACCESS_TOKEN')

if BWS_ACCESS_TOKEN is None:
    print('Failed to find BWS_ACCESS_TOKEN, make sure to set it in the environment variables!')
    exit(1)

client = BitwardenClient()
client.access_token_login(BWS_ACCESS_TOKEN)

def find_secret_value(uuid: str):
    resp = client.secrets().get(uuid)
    if not resp.success:
        print(f'Failed to fetch secret with id {uuid}, does it exist?')
        print('Error message: ' + resp.error_message)
        exit(1)

    return resp.data.value

os.makedirs('out/.env', exist_ok=True)

print('Loading secrets...')

templates = os.listdir('out/.env_templates')
print(f'Found {len(templates)} var templates!')
for template in templates:
    output = {}
    template_file = 'out/.env_templates/' + template
    # Read in template
    with open(template_file) as f:
        content = f.readlines()

        for line in content:
            line = line.rstrip()
            if '=' not in line or line.startswith('#'):
                continue

            split = line.split('=', 1)
            if len(split) < 2:
                print(f'Malformed secret template file {template_file}, line: {line}')
                exit(1)

            secret_name = split[0]
            secret_uuid = split[1]
            
            if '$BWS{' not in secret_uuid:
                print(f'Secret {secret_name} is already using a hardcoded value {secret_uuid}. Is this a UUID? If so, wrap it with "$BWS{{}}" !')
                output[secret_name] = secret_uuid
                continue
            
            uuid_match = BWS_UUID_MATCH.match(secret_uuid)
            if uuid_match:
                uuid_match = uuid_match.group(1)
                output[secret_name] = find_secret_value(uuid_match)
            else:
                print(f'Secret {secret_name} failed to match the BWS UUID! Is it a correct value?')
                exit(1)
    
    # Write output file
    if len(output) > 0:
        final_file = f"out/.env/{template.replace('.template', '')}"
        with open(final_file, 'w') as f:
            for key, val in output.items():
                f.write(f'{key}={val}\n')
        print('Wrote output env file: ' + final_file)