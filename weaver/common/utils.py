import random
import ua_generator


def create_ua() -> str:
    return ua_generator.generate().text

def generate_default_headers() -> dict[str, str]:
    ua = create_ua()
    lang = random.choice(['en-US,en;q=0.9', 'en-CA,en;q=0.8', 'en-GB,en;q=0.9'])
    encodings = random.choice([
        'gzip, deflate, br',
        'gzip, br, zstd',
        'gzip, deflate',
    ])
    base = {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': lang,
        'Accept-Encoding': encodings,
        'Connection': 'keep-alive',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-User': '?1',
    }
    if random.random() < 0.7:
        base['Upgrade-Insecure-Requests'] = '1'
    if random.random() < 0.5:
        base['Cache-Control'] = 'max-age=0'
    return base

    
def get_impersonation_profile(user_agent: str) -> str:
    # TODO check if this is better here or in http client
    ua_lower = user_agent.lower()
    
    if 'chrome' in ua_lower:
        return "chrome110"
    elif 'firefox' in ua_lower:
        return "firefox109"
    elif 'safari' in ua_lower:
        return "safari15_5"
    else:
        return "chrome110"