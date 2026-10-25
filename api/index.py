"""Entry point untuk Vercel (serverless function). Variabel `app` dikenali Vercel."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402

app = create_app()
