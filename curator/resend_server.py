from mcp.server.fastmcp import FastMCP
import os, requests, json
from dotenv import load_dotenv
load_dotenv(override=True)

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
mcp = FastMCP("Resend Email Server")

@mcp.tool()
def send_email(to_email: str, subject: str, html_content: str) -> str:
    """Send an email via Resend API"""
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "from": "Content Curator <onboarding@resend.dev>",
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    mcp.run(transport='stdio')
