"""Analysis helpers extracted from gui.py
"""
from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)


def analyze_results_for_report(data):
    analysis = {
        'total_records': len(data),
        'risk_assessment': {'overall_risk': 'LOW'},
        'temporal_analysis': {},
        'source_distribution': {},
        'content_analysis': {},
        'recommendations': [],
        'iocs': {'domains': [], 'ips': [], 'emails': [], 'urls': []},
        'timeline': []
    }
    try:
        buckets = Counter()
        media = Counter()
        dates = []
        for item in data:
            buckets[item.get('bucket', 'N/A')] += 1
            media[item.get('media', 'N/A')] += 1
            if item.get('date'):
                dates.append(item.get('date'))

        analysis['source_distribution'] = dict(buckets)
        analysis['content_analysis'] = dict(media)
        analysis['iocs'] = extract_iocs(data)
        analysis['recommendations'] = ["Revisar hallazgos", "Monitorear IOCs"]
        return analysis
    except Exception:
        logger.exception('Error analizando resultados')
        return analysis


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


def clean_data_for_mandiant_report(data):
    clean = []
    for item in data:
        if item.get('name') and item.get('bucket') and item.get('name').lower() not in ['unknown', '', 'null']:
            clean.append(item)
    return clean


def prepare_mandiant_chart_data(clean_data, analysis):
    sources = {}
    media_types = {}
    for item in clean_data:
        b = item.get('bucket', '')
        m = item.get('media', '')
        if b:
            sources[b] = sources.get(b, 0) + 1
        if m:
            media_types[m] = media_types.get(m, 0) + 1
    timeline = {'dates': [], 'counts': []}
    return {
        'sources': sources,
        'media_types': media_types,
        'timeline': timeline,
        'total_records': len(clean_data)
    }
