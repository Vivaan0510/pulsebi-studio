from google import genai


def generate_executive_memo(api_key: str, summary_metrics: dict) -> str:
    """Generates a concise CFO-level narrative memo from calculated PulseBI KPIs."""
    if not api_key:
        return ""

    client = genai.Client(api_key=api_key)

    prompt = f'''
You are a fractional CFO and senior BI consultant reviewing clean sales data for an executive leadership team.
Analyze the following business metrics calculated by PulseBI Studio and produce a structured, high-impact executive memo.

### Business Metrics Summary:
{summary_metrics.get('raw_summary', '')}

### Required Memo Format:
1. **Executive Headline:** A 2-sentence bottom-line assessment of company revenue health.
2. **Key Strategic Risks:** Plain-English breakdown of customer concentration and churn vulnerability.
3. **Immediate Action Plan (Next 14 Days):** 3 concrete tactical recommendations for the sales and finance teams.

Keep the tone professional, direct, and free of fluff.
'''

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ Unable to generate AI memo: {str(e)}"
