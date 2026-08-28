"""Vercel handler that redirects to Streamlit Cloud"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Redirect to Streamlit Cloud"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "message": "DetectAI Frontend & Backend on Vercel",
            "frontend": "Deploy to Streamlit Cloud separately - see DEPLOYMENT.md",
            "backend_api": "This Vercel endpoint",
            "docs": "/api/docs",
            "health": "/api/health"
        }
        self.wfile.write(json.dumps(response).encode())
