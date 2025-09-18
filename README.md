# Weaver

A modern, async-first web scraping framework for Python that combines the speed of HTTP requests with the power of browser automation.

## Why Weaver?

- **Unified Interface**: One framework, two scraping modes - use HTTP requests for speed or browser automation for JavaScript-heavy sites
- **Fully Async**: Native asyncio support across HTTP requests and browser automation for maximum concurrency
- **Anti-Detection**: Stealth capabilities to help you blend in
- **Flexible**: Mix and match HTTP and browser scraping within the same spider
- **Proxy Integration**: Built-in support for static and rotating proxy configurations

## Quick Start

```python
from weaver import BaseSpider, BrowserConfig

class BlogSpider(BaseSpider):
    def run(self):
        # Your scraping logic here
        pass

# Browser-based scraping
browser_config = BrowserConfig()
with BlogSpider(browser_config=browser_config) as spider:
    spider.run()
```

## Features

- **HTTP Client**: Fast async requests using aiohttp
- **Browser Client**: Full browser automation with Playwright  
- **Proxy Support**: Rotate through proxies seamlessly
- **Stealth Mode**: Anti-detection capabilities
- **Context Management**: Proper cleanup of resources automatically

## Installation

```bash
# Install the package
pip install weaver  # Coming soon

# Install browser binaries (required for browser automation)
playwright install

# Or install only Chromium to save space (~100MB vs ~300MB)
playwright install chromium
```

## Basic Usage

### HTTP-Only Scraping
```python
from weaver import BaseSpider, HttpConfig

class FastSpider(BaseSpider):
    def run(self):
        # Use self.http_client for requests
        pass

http_config = HttpConfig()
with FastSpider(http_config=http_config) as spider:
    spider.run()
```

### Browser Automation
```python
from weaver import BaseSpider, BrowserConfig

class BrowserSpider(BaseSpider):
    def run(self):
        # Use self.browser_client for Playwright
        pass

browser_config = BrowserConfig()
with BrowserSpider(browser_config=browser_config) as spider:
    spider.run()
```

### Hybrid Scraping
```python
from weaver import BaseSpider, HttpConfig, BrowserConfig

class HybridSpider(BaseSpider):
    def run(self):
        # Use both self.http_client and self.browser_client
        pass

http_config = HttpConfig()
browser_config = BrowserConfig()
with HybridSpider(http_config=http_config, browser_config=browser_config) as spider:
    spider.run()
```

## Development Status

⚠️ **Early Development**: Weaver is in active development. APIs may change frequently. Not recommended for production use yet.

## Requirements

- Python 3.10+
- aiohttp
- playwright

## Contributing

This project is in early stages. Contributions, ideas, and feedback are welcome!

## License

MIT License