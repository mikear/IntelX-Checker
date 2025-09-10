"""Analysis helpers extracted from gui.py
"""
from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)


def extract_iocs(data, max_items=50):
    domains = set()
    emails = set()
    ips = set()
    urls = set()
    domain_re = re.compile(r"\b[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b")
    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    ip_re = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
    url_re = re.compile(r"https?://[^\s]+|www\.[^\s]+")

    for item in data:
        text = ' '.join(str(v) for v in item.values() if v)
        domains.update(domain_re.findall(text))
        emails.update(email_re.findall(text))
        ips.update(ip_re.findall(text))
        urls.update(url_re.findall(text))

    return {
        'domains': list(domains)[:max_items],
        'ips': list(ips)[:max_items],
        'emails': list(emails)[:max_items],
        'urls': list(urls)[:max_items]
    }
