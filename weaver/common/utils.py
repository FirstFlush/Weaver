import ua_generator


def create_ua() -> str:
    return ua_generator.generate().text

def generate_default_headers() -> dict[str, str]:
    return {
        'User-Agent': create_ua(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
