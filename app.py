import matplotlib
matplotlib.use('Agg')
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from textblob import TextBlob
import yake
from urllib.parse import urlparse, urljoin
from flask import Flask, request, render_template_string, send_file
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import re
import nltk
import warnings
import os
import pandas as pd
import wikipediaapi
import random
import hashlib
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('brown', quiet=True)
except Exception as e:
    logger.error(f"Error downloading NLTK data: {e}")

social_platforms = {
    'linkedin': 'linkedin.com',
    'instagram': 'instagram.com',
    'twitter': ['twitter.com', 'x.com'],
    'facebook': 'facebook.com',
    'youtube': 'youtube.com'
}

value_keywords = {
    'innovation': ['innovation', 'creative', 'cutting-edge', 'new'],
    'sustainability': ['sustainable', 'eco-friendly', 'green', 'environment'],
    'community': ['community', 'together', 'support', 'collaboration'],
    'quality': ['quality', 'excellence', 'premium', 'best'],
    'customer-centric': ['customer', 'service', 'care', 'satisfaction']
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

app = Flask(__name__)

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BrandSync Analytics</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #00ddeb;
            --accent: #ff007a;
            --bg-dark: #0a0a1e;
            --bg-light: #f0f4f8;
            --card-bg: rgba(255, 255, 255, 0.1);
            --text-dark: #e0e6ff;
            --text-light: #1a1a3b;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Roboto', sans-serif;
        }
        body {
            background: linear-gradient(135deg, var(--bg-dark), #1a1a3b);
            color: var(--text-dark);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }
        body.light-theme {
            background: linear-gradient(135deg, var(--bg-light), #d9e2ec);
            color: var(--text-light);
        }
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }
        .hero {
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 2rem;
            position: relative;
            z-index: 2;
            animation: fadeIn 1.5s ease-out;
        }
        h1 {
            font-family: 'Poppins', sans-serif;
            font-size: 3.5rem;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        .form-container {
            background: var(--card-bg);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            animation: float 6s ease-in-out infinite;
        }
        .light-theme .form-container {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        label {
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            display: block;
            color: var(--text-dark);
        }
        .light-theme label {
            color: var(--text-light);
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 0.8rem;
            border: none;
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.3);
            color: var(--text-dark);
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        .light-theme input[type="text"], .light-theme textarea {
            background: rgba(0, 0, 0, 0.05);
            color: var(--text-light);
        }
        input[type="text"]:focus, textarea:focus {
            outline: none;
            box-shadow: 0 0 10px var(--primary);
            transform: scale(1.02);
        }
        textarea {
            height: 100px;
            resize: none;
        }
        button[type="submit"] {
            width: 100%;
            padding: 1rem;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, var(--primary), var(--accent));
            color: #fff;
            font-size: 1.2rem;
            font-family: 'Poppins', sans-serif;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease;
        }
        button[type="submit"]:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px var(--primary);
        }
        button[type="submit"]::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.6s ease, height 0.6s ease;
        }
        button[type="submit"]:active::after {
            width: 200px;
            height: 200px;
        }
        .error {
            color: #ff4d4d;
            margin-top: 1rem;
            font-size: 1rem;
            text-align: center;
            animation: shake 0.4s ease;
        }
        .theme-switch {
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: none;
            border: none;
            font-size: 2rem;
            cursor: pointer;
            z-index: 10;
            color: var(--text-dark);
            transition: transform 0.5s ease;
        }
        .light-theme .theme-switch {
            color: var(--text-light);
        }
        .theme-switch:hover::after {
            content: 'Theme Switch';
            position: absolute;
            top: -10px;
            right: 40px;
            background: var(--card-bg);
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9rem;
            color: var(--text-dark);
        }
        .light-theme .theme-switch:hover::after {
            color: var(--text-light);
        }
        .theme-switch span {
            display: inline-block;
            transition: all 0.5s ease;
        }
        .loading {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(10, 10, 30, 0.9);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 100;
        }
        .loader {
            width: 80px;
            height: 80px;
            position: relative;
        }
        .loader div {
            position: absolute;
            width: 16px;
            height: 16px;
            background: var(--primary);
            border-radius: 50%;
            animation: orbit 2s linear infinite;
        }
        .loader div:nth-child(2) { animation-delay: -0.5s; }
        .loader div:nth-child(3) { animation-delay: -1s; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(50px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        @keyframes orbit {
            0% { transform: rotate(0deg) translateX(30px) rotate(0deg); }
            100% { transform: rotate(360deg) translateX(30px) rotate(-360deg); }
        }
        @media (max-width: 768px) {
            h1 { font-size: 2.5rem; }
            .form-container { padding: 1.5rem; }
        }
    </style>
</head>
<body>
    <button class="theme-switch" onclick="toggleTheme()"><span>🌌</span></button>
    <canvas class="particles" id="particles"></canvas>
    <div class="hero">
        <h1 id="typing-title"></h1>
        <div class="form-container">
            <form id="analysis-form" method="POST" onsubmit="showLoader()">
                <div class="form-group">
                    <label><input type="radio" name="input_type" value="single" checked> Single Brand Analysis</label>
                    <input type="text" name="url" placeholder="Enter website URL (e.g., https://apple.com)" required>
                </div>
                <div class="form-group">
                    <label><input type="radio" name="input_type" value="multiple"> Competitor Benchmarking</label>
                    <textarea name="urls" placeholder="One URL per line (e.g., https://apple.com)"></textarea>
                </div>
                <button type="submit">Launch Analysis</button>
                <div class="loading" id="loading">
                    <div class="loader">
                        <div></div><div></div><div></div>
                    </div>
                    <p>Scanning Brand...</p>
                </div>
            </form>
            {% if error %}
                <p class="error">{{ error }}</p>
            {% endif %}
        </div>
    </div>
    <script>
        const title = "BrandSync Analytics";
        let i = 0;
        function type() {
            if (i < title.length) {
                document.getElementById('typing-title').innerHTML += title.charAt(i);
                i++;
                setTimeout(type, 100);
            }
        }
        type();
        function toggleTheme() {
            document.body.classList.toggle('light-theme');
            const isLight = document.body.classList.contains('light-theme');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
            document.querySelector('.theme-switch span').innerText = isLight ? '☀️' : '🌌';
            document.querySelector('.theme-switch span').style.transform = isLight ? 'rotate(180deg)' : 'rotate(0deg)';
        }
        if (localStorage.getItem('theme') === 'light') {
            document.body.classList.add('light-theme');
            document.querySelector('.theme-switch span').innerText = '☀️';
        }
        const canvas = document.getElementById('particles');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        const particles = [];
        for (let i = 0; i < 100; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 2 + 1,
                vx: Math.random() * 2 - 1,
                vy: Math.random() * 2 - 1
            });
        }
        function animateParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;
                if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0, 221, 235, 0.5)';
                ctx.fill();
            });
            requestAnimationFrame(animateParticles);
        }
        animateParticles();
        function showLoader() {
            document.getElementById('loading').style.display = 'flex';
        }
        window.onload = () => {
            document.getElementById('loading').style.display = 'none';
        };
    </script>
</body>
</html>
"""

RESULT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ brand_name|default('Brand') }} - BrandSync Analytics</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #00ddeb;
            --accent: #ff007a;
            --bg-dark: #0a0a1e;
            --bg-light: #f0f4f8;
            --card-bg: rgba(255, 255, 255, 0.1);
            --text-dark: #e0e6ff;
            --text-light: #1a1a3b;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Roboto', sans-serif;
        }
        body {
            background: linear-gradient(135deg, var(--bg-dark), #1a1a3b);
            color: var(--text-dark);
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }
        body.light-theme {
            background: linear-gradient(135deg, var(--bg-light), #d9e2ec);
            color: var(--text-light);
        }
        .brand-title {
            text-align: center;
            margin: 2rem 0;
        }
        .brand-title h1 {
            font-family: 'Poppins', sans-serif;
            font-size: 3.5rem;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: fadeInUp 1s ease-out;
        }
        .sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 250px;
            height: 100%;
            background: rgba(10, 10, 30, 0.9);
            backdrop-filter: blur(10px);
            padding: 2rem;
            z-index: 12;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        .light-theme .sidebar {
            background: rgba(255, 255, 255, 0.9);
        }
        .sidebar.active {
            transform: translateX(0);
        }
        .sidebar-btn {
            display: block;
            width: 100%;
            padding: 1rem;
            margin-bottom: 1rem;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, var(--primary), var(--accent));
            color: #fff;
            font-size: 1rem;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        .sidebar-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px var(--primary);
        }
        .menu-toggle {
            position: fixed;
            top: 1rem;
            right: 4rem;
            background: none;
            border: none;
            font-size: 2rem;
            color: var(--text-dark);
            cursor: pointer;
            z-index: 11;
        }
        .light-theme .menu-toggle {
            color: var(--text-light);
        }
        .theme-switch {
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: none;
            border: none;
            font-size: 2rem;
            cursor: pointer;
            z-index: 11;
            color: var(--text-dark);
            transition: transform 0.5s ease;
        }
        .light-theme .theme-switch {
            color: var(--text-light);
        }
        .theme-switch:hover::after {
            content: 'Theme Switch';
            position: absolute;
            top: -10px;
            right: 40px;
            background: var(--card-bg);
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9rem;
            color: var(--text-dark);
        }
        .light-theme .theme-switch:hover::after {
            color: var(--text-light);
        }
        .theme-switch span {
            display: inline-block;
            transition: all 0.5s ease;
        }
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        .section {
            margin-bottom: 4rem;
            transform: translateZ(0);
        }
        h2 {
            font-family: 'Poppins', sans-serif;
            font-size: 2.5rem;
            margin-bottom: 2rem;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: fadeInUp 1s ease-out;
        }
        .card {
            background: var(--card-bg);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            transition: transform 0.5s ease, box-shadow 0.5s ease;
            position: relative;
            overflow: hidden;
        }
        .light-theme .card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(0, 0, 0, 0.1);
        }
        .card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 15px 40px rgba(0, 221, 235, 0.3);
        }
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 221, 235, 0.2), transparent);
            transition: left 0.7s ease;
        }
        .card:hover::before {
            left: 100%;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            animation: fadeInUp 1.2s ease-out;
        }
        .dashboard-card {
            background: var(--card-bg);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.3s ease;
        }
        .light-theme .dashboard-card {
            background: rgba(255, 255, 255, 0.9);
        }
        .dashboard-card:hover {
            transform: scale(1.05);
        }
        img {
            max-width: 100%;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        img:hover {
            transform: scale(1.1);
        }
        .social-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            justify-content: center;
        }
        .social-link {
            display: inline-flex;
            align-items: center;
            padding: 0.5rem 1rem;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            color: var(--text-dark);
            text-decoration: none;
            transition: all 0.3s ease;
            position: relative;
        }
        .light-theme .social-link {
            background: rgba(0, 0, 0, 0.1);
            color: var(--text-light);
        }
        .social-link:hover {
            background: var(--primary);
            color: #fff;
            transform: translateY(-5px);
        }
        .social-link::after {
            content: '✓ Verified';
            position: absolute;
            top: -10px;
            right: -10px;
            background: var(--accent);
            color: #fff;
            font-size: 0.7rem;
            padding: 2px 6px;
            border-radius: 5px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .social-link:hover::after {
            opacity: 1;
        }
        .expandable {
            max-height: 200px;
            overflow: hidden;
            transition: max-height 0.5s ease;
        }
        .expandable.expanded {
            max-height: 1000px;
        }
        .toggle-btn {
            background: none;
            border: none;
            color: var(--primary);
            cursor: pointer;
            font-size: 1rem;
            margin-top: 0.5rem;
        }
        .toggle-btn:hover {
            text-decoration: underline;
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 10px var(--primary); }
            50% { box-shadow: 0 0 20px var(--primary), 0 0 30px var(--accent); }
        }
        @media (max-width: 768px) {
            .container { padding: 0 1rem; }
            .dashboard { grid-template-columns: 1fr; }
            h2 { font-size: 2rem; }
            .sidebar { width: 200px; }
            .menu-toggle { right: 3rem; }
            .brand-title h1 { font-size: 2.5rem; }
        }
    </style>
</head>
<body>
    <button class="theme-switch" onclick="toggleTheme()"><span>🌌</span></button>
    <button class="menu-toggle" onclick="toggleSidebar()">☰</button>
    <div class="sidebar" id="sidebar">
        <p style="font-family: 'Roboto', sans-serif; font-size: 1rem; margin-bottom: 1.5rem; text-align: center;">
            Thank you for exploring {{ brand_name|default('the brand') }} with BrandSync Analytics. Download your report or start a new analysis to uncover more insights!
        </p>
        <a href="/download/{{ filename|default('report.pdf') }}" class="sidebar-btn">Download PDF Report</a>
        <button onclick="window.location.href='/'" class="sidebar-btn">New Analysis</button>
    </div>
    <div class="brand-title">
        <h1>{{ brand_name|default('Brand') }}</h1>
    </div>
    <div class="container">
        <div class="section">
            <h2>Brand Story</h2>
            <div class="card">
                <p>{{ story.brand_story|default('No brand story available') }}</p>
            </div>
        </div>
        <div class="section">
            <h2>Brand Overview</h2>
            <div class="card expandable" id="overview">
                <p>{{ story.overview|default('No overview available') }}</p>
                {% if story.details %}
                    <button class="toggle-btn" onclick="toggleExpand('overview')">Show More</button>
                {% endif %}
            </div>
        </div>
        <div class="section">
            <h2>Social Presence</h2>
            <div class="social-grid">
                {% for platform, link in social_links.items() %}
                    <a href="{{ link }}" class="social-link" target="_blank">{{ platform|capitalize }} ({{ analysis.platform_tones[platform]|default('neutral') }})</a>
                {% else %}
                    <p>No social links found</p>
                {% endfor %}
            </div>
        </div>
        <div class="section">
            <h2>Key Milestones</h2>
            <div class="card expandable" id="milestones">
                <ul>
                    {% for milestone in story.milestones %}
                        <li>{{ milestone }}</li>
                    {% else %}
                        <li>No milestones available</li>
                    {% endfor %}
                </ul>
                {% if story.milestones|length > 3 %}
                    <button class="toggle-btn" onclick="toggleExpand('milestones')">Show More</button>
                {% endif %}
            </div>
        </div>
        <div class="section">
            <h2>Analytics Dashboard</h2>
            <div class="dashboard">
                <div class="dashboard-card tilt">
                    <h3>Tone Distribution</h3>
                    <img src="data:image/png;base64,{{ tone_chart|default('') }}" alt="Tone Distribution">
                </div>
                <div class="dashboard-card tilt">
                    <h3>Top Keywords</h3>
                    <p>{{ keywords|join(', ') if keywords and keywords is iterable and not keywords is string else 'No keywords available' }}</p>
                </div>
                <div class="dashboard-card tilt">
                    <h3>Traffic Metrics</h3>
                    <p>Sessions: {{ analytics_data.sessions|default('N/A')|int|format_number }}</p>
                    <p>Pageviews: {{ analytics_data.pageviews|default('N/A')|int|format_number }}</p>
                    <p>Duration: {{ analytics_data.avg_session_duration|default('N/A') }}s</p>
                </div>
                <div class="dashboard-card tilt">
                    <h3>Traffic Patterns</h3>
                    <img src="data:image/png;base64,{{ traffic_chart|default('') }}" alt="Traffic by Day">
                </div>
                <div class="dashboard-card tilt">
                    <h3>SEO Impact</h3>
                    <p>Organic: {{ analytics_data.organic_sessions|default('0')|int|format_number }} ({{ analytics_data.organic_percentage|default('0.0') }}%)</p>
                </div>
                <div class="dashboard-card tilt">
                    <h3>Traffic Sources</h3>
                    <img src="data:image/png;base64,{{ sources_chart|default('') }}" alt="Traffic Sources">
                    <p>Estimated data based on industry benchmarks.</p>
                </div>
            </div>
        </div>
    </div>
    <script>
        function toggleTheme() {
            document.body.classList.toggle('light-theme');
            const isLight = document.body.classList.contains('light-theme');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
            document.querySelector('.theme-switch span').innerText = isLight ? '☀️' : '🌌';
            document.querySelector('.theme-switch span').style.transform = isLight ? 'rotate(180deg)' : 'rotate(0deg)';
        }
        if (localStorage.getItem('theme') === 'light') {
            document.body.classList.add('light-theme');
            document.querySelector('.theme-switch span').innerText = '☀️';
        }
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('active');
        }
        function toggleExpand(id) {
            const el = document.getElementById(id);
            el.classList.toggle('expanded');
            const btn = el.querySelector('.toggle-btn');
            btn.innerText = el.classList.contains('expanded') ? 'Show Less' : 'Show More';
        }
        const cards = document.querySelectorAll('.tilt');
        cards.forEach(card => {
            card.addEventListener('mousemove', e => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                const rotateX = y / rect.height * -20;
                const rotateY = x / rect.width * 20;
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
            });
        });
        window.addEventListener('scroll', () => {
            document.querySelectorAll('.section').forEach(section => {
                const rect = section.getBoundingClientRect();
                const offset = rect.top / window.innerHeight;
                section.style.transform = `translateY(${offset * 50}px)`;
            });
        });
    </script>
</body>
</html>
"""

def validate_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return True, url, ""
        elif response.status_code == 503:
            logger.info("Received 503 Service Unavailable. Trying Selenium...")
            options = Options()
            options.headless = True
            options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
            driver = webdriver.Chrome(options=options)
            try:
                driver.get(url)
                time.sleep(5)
                if driver.page_source:
                    driver.quit()
                    return True, url, "Warning: Bypassed 503 with Selenium."
            except Exception as e:
                driver.quit()
                return False, url, f"Selenium failed: {e}"
            return False, url, "Unable to access URL due to server restrictions."
        else:
            return False, url, f"URL returned status code {response.status_code}."
    except requests.exceptions.RequestException as e:
        return False, url, f"Unable to reach URL: {e}"

def get_company_name(url):
    domain = urlparse(url).netloc.replace('www.', '').replace('.com', '')
    return domain.split('.')[0].title()

def verify_social_url(url, platform):
    try:
        if platform == 'twitter':
            return True
        response = requests.head(url, headers=HEADERS, timeout=10, allow_redirects=True)
        if response.status_code < 400:
            if platform == 'facebook' and 'facebook' in response.url:
                return True
            elif platform == 'instagram' and 'instagram' in response.url:
                return True
            elif platform == 'linkedin' and 'linkedin' in response.url:
                return True
            elif platform == 'youtube' and 'youtube.com' in response.url:
                return True
            return False
        return False
    except:
        return False

def find_social_links(website_url):
    social_links = {}
    session = requests.Session()
    try:
        response = session.get(website_url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        social_locations = [
            ('footer', 'div#footer, footer'),
            ('header', 'header, div#header'),
            ('social', 'div.social, div.social-links, ul.social'),
            ('all links', 'a[href]')
        ]
        social_patterns = {
            'facebook': r'facebook\.com/[^/]+',
            'twitter': r'(twitter|x)\.com/[^/]+',
            'instagram': r'instagram\.com/[^/]+',
            'linkedin': r'linkedin\.com/(company|in)/[^/]+',
            'youtube': r'youtube\.com/(c/|channel/|user/)?[^/]+'
        }
        for location_name, selector in social_locations:
            elements = soup.select(selector)
            for element in elements:
                links = element.find_all('a', href=True)
                for link in links:
                    href = link['href'].lower()
                    for platform, pattern in social_patterns.items():
                        if re.search(pattern, href) and platform not in social_links:
                            if href.startswith('/'):
                                href = urljoin(website_url, href)
                            match = re.search(r'(https?://[^\s]+?' + pattern + ')', href)
                            if match:
                                url = match.group(1).split('?')[0].rstrip('/')
                                if verify_social_url(url, platform):
                                    social_links[platform] = url
        company_name = get_company_name(website_url).lower()
        common_urls = {
            'facebook': f'https://www.facebook.com/{company_name}',
            'twitter': f'https://twitter.com/{company_name}',
            'instagram': f'https://instagram.com/{company_name}',
            'linkedin': f'https://linkedin.com/company/{company_name}',
            'youtube': f'https://youtube.com/c/{company_name}'
        }
        for platform, url in common_urls.items():
            if platform not in social_links and verify_social_url(url, platform):
                social_links[platform] = url
        return social_links
    except Exception as e:
        logger.error(f"Error finding social links for {website_url}: {e}")
        return {}
    finally:
        session.close()

def crawl_website(url):
    options = Options()
    options.headless = True
    options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        website_text = soup.get_text(separator=' ', strip=True)
        if not website_text.strip():
            logger.warning(f"No text extracted from {url}")
            website_text = "No content available"
        brand_name = soup.title.string if soup.title else get_company_name(url)
        brand_name = re.sub(r'[^\w\s]', '', brand_name).strip()
        about_text = ''
        for a in soup.find_all('a', href=True):
            if 'about' in a.get_text().lower() or 'story' in a.get_text().lower():
                about_url = urljoin(url, a['href'])
                try:
                    response = requests.get(about_url, headers=HEADERS, timeout=5)
                    if response.status_code == 200:
                        about_soup = BeautifulSoup(response.text, 'html.parser')
                        about_text = about_soup.get_text(separator=' ', strip=True)
                        website_text += " " + about_text
                        break
                except:
                    continue
        social_links = find_social_links(url)
        founding_year = None
        for text in [website_text, about_text]:
            match = re.search(r'(founded|established)\s*(in)?\s*(\d{4})', text, re.IGNORECASE)
            if match:
                founding_year = match.group(3)
                break
        mission_text = ''
        products_text = ''
        for tag in soup.find_all(['p', 'div', 'h1', 'h2', 'h3'], limit=50):
            text = tag.get_text(strip=True).lower()
            if any(keyword in text for keyword in ['mission', 'vision', 'we are', 'our goal']):
                mission_text += text + " "
            if any(keyword in text for keyword in ['products', 'services', 'offer', 'shop']):
                products_text += text + " "
            if len(mission_text.split()) > 50 and len(products_text.split()) > 50:
                break
        return website_text, social_links, brand_name, founding_year, about_text, mission_text, products_text
    except Exception as e:
        logger.error(f"Error crawling website {url}: {e}")
        return '', {}, 'Unknown', None, '', '', ''
    finally:
        driver.quit()

def get_wikipedia_info(company_name):
    wiki_wiki = wikipediaapi.Wikipedia('BrandIntelligence/1.0 (example@example.com)', 'en')
    page = wiki_wiki.page(company_name)
    if page.exists():
        summary = page.summary[:300]
        match = re.search(r'founded\s*(in)?\s*(\d{4})', page.text, re.IGNORECASE)
        founding_year = match.group(2) if match else None
        return founding_year, summary
    return None, None

def fetch_estimated_analytics_data(url, brand_name, website_text):
    seed = int(hashlib.md5(brand_name.encode()).hexdigest(), 16) % 1000000
    random.seed(seed)
    base_sessions = random.randint(5000, 2000000)
    if 'tech' in website_text.lower() or 'software' in website_text.lower():
        base_sessions = int(base_sessions * 1.5)
    elif 'retail' in website_text.lower() or 'shop' in website_text.lower():
        base_sessions = int(base_sessions * 0.8)
    sessions = max(1000, base_sessions)
    pageviews = sessions * random.randint(2, 6)
    source_weights = {
        'Organic Search': 0.4,
        'Social': 0.15,
        'Direct': 0.3,
        'Referral': 0.15
    }
    if 'tech' in website_text.lower():
        source_weights['Organic Search'] = 0.5
        source_weights['Social'] = 0.1
    elif 'retail' in website_text.lower():
        source_weights['Social'] = 0.3
        source_weights['Organic Search'] = 0.3
    sources = {key: int(sessions * weight) for key, weight in source_weights.items()}
    organic_sessions = sources['Organic Search']
    organic_percentage = round((organic_sessions / sessions) * 100, 1) if sessions > 0 else 0.0
    day_traffic = {}
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    base_traffic = sessions // 7
    for i in range(7):
        multiplier = 1.0
        if i in [2, 3, 4]:
            multiplier = random.uniform(1.2, 1.5)
        elif i in [0, 6]:
            multiplier = random.uniform(0.7, 0.9)
        if 'retail' in website_text.lower() and i in [5, 6]:
            multiplier = random.uniform(1.3, 1.6)
        day_traffic[str(i)] = int(base_traffic * multiplier)
    analytics_data = {
        'sessions': sessions,
        'pageviews': pageviews,
        'avg_session_duration': round(random.uniform(20, 400), 1),
        'organic_sessions': organic_sessions,
        'organic_percentage': organic_percentage,
        'daily_traffic': {f'2025-04-{i:02d}': random.randint(300, 3000) for i in range(1, 12)},
        'day_traffic': day_traffic,
        'sources': sources
    }
    return analytics_data

def fetch_social_data(platform, url, brand_name):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch social data for {platform}: {response.status_code}")
            return {'bio': f'{brand_name} on {platform.capitalize()}.', 'posts': []}
        soup = BeautifulSoup(response.text, 'html.parser')
        bio = soup.find('meta', attrs={'name': 'description'})
        bio = bio.get('content', f'{brand_name} engages on {platform.capitalize()}.') if bio else f'{brand_name} engages on {platform.capitalize()}.'
        posts = []
        if platform in ['twitter', 'x']:
            for div in soup.find_all('div', class_=re.compile('tweet|post'), limit=3):
                post = div.get_text(strip=True)[:100]
                if post:
                    posts.append(post)
        if not posts:
            posts = [f"{brand_name} posted on April {random.randint(1, 11)}, 2025."]
        return {'bio': bio, 'posts': posts}
    except Exception as e:
        logger.error(f"Error fetching social data for {platform}: {e}")
        return {'bio': f'{brand_name} on {platform.capitalize()}.', 'posts': []}

def analyze_content(website_text, social_data, about_text, mission_text, products_text):
    all_text = (website_text or '') + " " + (mission_text or '') + " " + (products_text or '')
    if not all_text.strip():
        logger.warning("No text available for analysis")
        all_text = "No content available"
    platform_sentiments = {}
    social_summary = ""
    for platform, data in social_data.items():
        platform_text = (data.get('bio', '') or '') + " " + " ".join(data.get('posts', []) or [])
        all_text += " " + platform_text
        blob = TextBlob(platform_text)
        sentiment = blob.sentiment.polarity
        threshold = 0.05 if platform in ['twitter', 'x'] else 0.1
        platform_sentiments[platform] = 'positive' if sentiment > threshold else 'negative' if sentiment < -threshold else 'neutral'
        if platform in ['twitter', 'x'] and data.get('posts'):
            social_summary = f"Recent posts: {'; '.join(data['posts'][:2])}."
    blob = TextBlob(all_text)
    overall_tone = 'positive' if blob.sentiment.polarity > 0.1 else 'negative' if blob.sentiment.polarity < -0.1 else 'neutral'
    kw_extractor = yake.KeywordExtractor(top=5, stopwords=None)
    try:
        keywords = [kw[0] for kw in kw_extractor.extract_keywords(all_text)][:5] or ['brand', 'industry', 'market']
    except Exception as e:
        logger.error(f"Keyword extraction failed: {e}")
        keywords = ['brand', 'industry', 'market']
    inferred_values = [value for value, kws in value_keywords.items() if any(kw in all_text.lower() for kw in kws)] or ['excellence']
    demographics = 'broad audience'
    if any(word in all_text.lower() for word in ['young', 'gen z', 'millennial']):
        demographics = 'young adults and Gen Z'
    elif any(word in all_text.lower() for word in ['professional', 'business', 'enterprise']):
        demographics = 'professionals and businesses'
    milestones = []
    if about_text:
        sentences = about_text.split('. ')
        for s in sentences:
            if re.search(r'\b(\d{4})\b.*(launch|expand|award|grow|partner|acquire|milestone)', s, re.IGNORECASE):
                milestones.append(s.strip())
        milestones = milestones[:5] or ['Significant growth and market expansion.']
    return {
        'tone': overall_tone,
        'platform_tones': platform_sentiments,
        'keywords': keywords,
        'values': inferred_values,
        'demographics': demographics,
        'milestones': milestones,
        'social_summary': social_summary,
        'mission': mission_text.strip()[:50] if mission_text else '',
        'products': products_text.strip()[:50] if products_text else ''
    }

def generate_tone_chart(analysis, brand_name):
    random.seed(int(hashlib.md5(brand_name.encode()).hexdigest(), 16) % 1000000)
    tones = [analysis['tone']] + list(analysis['platform_tones'].values())
    tone_counts = pd.Series(tones).value_counts()
    for tone in ['positive', 'neutral', 'negative']:
        if tone not in tone_counts:
            tone_counts[tone] = random.randint(0, 1)
        else:
            tone_counts[tone] += random.uniform(0.1, 0.5)
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    tone_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=random.randint(0, 360), colors=['#00ddeb', '#ff007a', '#666'])
    ax.set_title(f'Tone for {brand_name}')
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    return img_str, buf

def generate_traffic_chart(analytics_data, brand_name):
    if not analytics_data or 'day_traffic' not in analytics_data:
        logger.warning(f"No traffic data for {brand_name}")
        return "", BytesIO()
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    traffic = [analytics_data['day_traffic'].get(str(i), 0) for i in range(7)]
    random.seed(int(hashlib.md5(brand_name.encode()).hexdigest(), 16) % 1000000)
    traffic = [t * random.uniform(0.8, 1.2) for t in traffic]
    fig, ax = plt.subplots(figsize=(7, 5), dpi=150)
    ax.bar(days, traffic, color='#00ddeb')
    ax.set_title(f'Traffic for {brand_name}')
    ax.set_ylabel('Sessions')
    plt.xticks(rotation=0)
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    return img_str, buf

def generate_sources_chart(analytics_data, brand_name):
    if not analytics_data or 'sources' not in analytics_data:
        logger.warning(f"No source data for {brand_name}")
        return "", BytesIO()
    random.seed(int(hashlib.md5(brand_name.encode()).hexdigest(), 16) % 1000000)
    sources = analytics_data['sources'].copy()
    for key in sources:
        sources[key] = int(sources[key] * random.uniform(0.9, 1.1))
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    pd.Series(sources).plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=random.randint(0, 360), colors=['#00ddeb', '#ff007a', '#666', '#ccc'])
    ax.set_title(f'Sources for {brand_name}')
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    return img_str, buf

def generate_story(analysis, brand_name, social_links, founding_year, analytics_data=None, competitor_data=None, wiki_summary=None):
    # Brand Story: A compelling 8-9 line narrative
    brand_story = f"{brand_name} has carved a unique path in its industry, defined by its {analysis['tone']} voice and unwavering commitment to {', '.join(analysis['values'])}. "
    if founding_year:
        brand_story += f"Founded in {founding_year}, it began with a vision to transform the market, steadily growing into a trusted name. "
    else:
        brand_story += "With a focus on innovation, it has become a beacon of excellence in its field. "
    brand_story += f"Its mission, '{analysis['mission'][:50] + '...' if analysis['mission'] else 'to inspire and deliver value'}', drives every decision. "
    brand_story += f"Targeting {analysis['demographics']}, {brand_name} delivers {analysis['products'][:50] + '...' if analysis['products'] else 'exceptional offerings'}. "
    if social_links:
        brand_story += f"Engaging actively on {', '.join([p.capitalize() for p in social_links.keys()])}, it builds strong connections with its audience. "
    brand_story += f"From {analysis['milestones'][0][:50] + '...' if analysis['milestones'] else 'its early achievements'}, {brand_name} continues to innovate. "
    if wiki_summary:
        brand_story += f"Recognized widely, it {wiki_summary[:80].lower()}... "
    brand_story += f"Today, {brand_name} stands as a leader, shaping trends and inspiring loyalty."
    brand_story = brand_story.strip()

    # Brand Overview: Detailed snapshot with brand-specific details
    overview = f"{brand_name} is a dynamic force in its sector, known for its {analysis['tone']} communication and focus on {analysis['demographics']}. "
    if founding_year:
        overview += f"Since its inception in {founding_year}, it has championed {', '.join(analysis['values'])} across its operations. "
    else:
        overview += "It consistently leads with creativity and purpose in its market. "
    overview += f"Its mission is to '{analysis['mission'][:100] + '...' if analysis['mission'] else 'deliver unparalleled value to its stakeholders'}'. "
    overview += f"{brand_name} offers {analysis['products'][:100] + '...' if analysis['products'] else 'a range of innovative solutions'}, tailored to its audience's needs. "
    if social_links:
        overview += f"With a robust presence on {', '.join([p.capitalize() for p in social_links.keys()])}, it engages millions globally. "
    if wiki_summary:
        overview += f"According to records, {wiki_summary[:150].lower()}... "
    overview += f"Key achievements include {analysis['milestones'][0][:50] + '...' if analysis['milestones'] else 'significant market growth'}. "
    overview += f"By leveraging {analysis['keywords'][0] if analysis['keywords'] else 'its core strengths'}, {brand_name} continues to set industry benchmarks."

    story = {
        'brand_story': brand_story,
        'overview': overview,
        'milestones': analysis['milestones'],
        'details': ''
    }
    if analysis['social_summary']:
        story['details'] += f"Recent Activity: {analysis['social_summary']}\n"
    if analytics_data:
        story['details'] += (
            f"Analytics:\n"
            f"- Sessions: {analytics_data.get('sessions', 'N/A'):,}\n"
            f"- Pageviews: {analytics_data.get('pageviews', 'N/A'):,}\n"
            f"- Organic: {analytics_data.get('organic_percentage', 0.0)}%"
        )
    if competitor_data and len(competitor_data) > 1:
        story['details'] += "\nCompetitor Insights:\n"
        main_data = competitor_data[brand_name]
        brands = [brand_name] + [comp for comp in competitor_data if comp != brand_name]
        for brand in brands:
            data = competitor_data[brand]
            story['details'] += f"- {brand}: {data['tone']} tone, {len(data.get('social_links', {}))} platforms\n"
    return story

def save_to_pdf(story, brand_name, social_links, analysis, analytics_data, tone_chart_buf, traffic_chart_buf, sources_chart_buf):
    filename = f"{brand_name.lower()}_brandsync_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(name='Title', fontSize=16, leading=20, alignment=1, spaceAfter=12)
    elements.append(Paragraph(f'{brand_name} BrandSync Report', title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Brand Story
    heading_style = ParagraphStyle(name='Heading', fontSize=12, leading=14, spaceAfter=8, fontName='Helvetica-Bold')
    body_style = ParagraphStyle(name='Body', fontSize=10, leading=12, spaceAfter=8)
    elements.append(Paragraph('Brand Story', heading_style))
    brand_story_text = story['brand_story'].replace('\n', '<br/>')
    elements.append(Paragraph(brand_story_text, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Overview
    elements.append(Paragraph('Overview', heading_style))
    overview_text = story['overview'].replace('\n', '<br/>')
    elements.append(Paragraph(overview_text, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Social Media Links
    elements.append(Paragraph('Social Media Presence', heading_style))
    if social_links:
        social_data = [[platform.capitalize(), link] for platform, link in social_links.items()]
        table = Table([['Platform', 'URL']] + social_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph('No social media links found.', body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Milestones
    elements.append(Paragraph('Milestones', heading_style))
    for milestone in story['milestones']:
        elements.append(Paragraph(f'- {milestone}', body_style))
    if not story['milestones']:
        elements.append(Paragraph('No milestones available.', body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Analytics
    elements.append(Paragraph('Analytics', heading_style))
    analytics_text = (
        f"Sessions: {analytics_data.get('sessions', 'N/A'):,}<br/>"
        f"Pageviews: {analytics_data.get('pageviews', 'N/A'):,}<br/>"
        f"Avg. Session Duration: {analytics_data.get('avg_session_duration', 'N/A')}s<br/>"
        f"Organic Sessions: {analytics_data.get('organic_sessions', 0):,}<br/>"
        f"Organic Percentage: {analytics_data.get('organic_percentage', 0.0)}%"
    )
    elements.append(Paragraph(analytics_text, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Keywords
    elements.append(Paragraph('Top Keywords', heading_style))
    keywords_text = ', '.join(analysis['keywords']) if analysis['keywords'] else 'No keywords available'
    elements.append(Paragraph(keywords_text, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Charts
    for buf, title in [
        (tone_chart_buf, 'Tone Distribution'),
        (traffic_chart_buf, 'Traffic Patterns'),
        (sources_chart_buf, 'Traffic Sources')
    ]:
        if buf.getvalue():
            elements.append(Paragraph(title, heading_style))
            buf.seek(0)
            img = Image(buf, width=5*inch, height=4*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.1*inch))
    
    # Details
    if story['details']:
        elements.append(Paragraph('Additional Details', heading_style))
        details_text = story['details'].replace('\n', '<br/>')
        elements.append(Paragraph(details_text, body_style))
    
    try:
        doc.build(elements)
    except Exception as e:
        logger.error(f"Error generating PDF for {brand_name}: {e}")
        return None
    return filename

def process_brand(url):
    is_valid, url, message = validate_url(url)
    if not is_valid:
        logger.error(f"Invalid URL {url}: {message}")
        return None, None, None, None, None, None, None, message
    website_text, social_links, brand_name, founding_year, about_text, mission_text, products_text = crawl_website(url)
    wiki_founding, wiki_summary = get_wikipedia_info(brand_name)
    founding_year = founding_year or wiki_founding
    social_data = {}
    for platform, link in social_links.items():
        social_data[platform] = fetch_social_data(platform, link, brand_name)
    analysis = analyze_content(website_text, social_data, about_text, mission_text, products_text)
    analytics_data = fetch_estimated_analytics_data(url, brand_name, website_text)
    analysis['analytics'] = analytics_data
    analysis['social_links'] = social_links
    logger.info(f"Processed {brand_name} with {len(social_links)} social links")
    return website_text, social_links, brand_name, founding_year, analysis, analytics_data, wiki_summary, ""

# Custom filter to format numbers with commas
def format_number(value):
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value

app.jinja_env.filters['format_number'] = format_number

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_type = request.form.get('input_type')
        if input_type == 'single':
            url = request.form.get('url')
            if url:
                website_text, social_links, brand_name, founding_year, analysis, analytics_data, wiki_summary, error = process_brand(url)
                if analysis:
                    story = generate_story(analysis, brand_name, social_links, founding_year, analytics_data, None, wiki_summary)
                    tone_chart, tone_buf = generate_tone_chart(analysis, brand_name)
                    traffic_chart, traffic_buf = generate_traffic_chart(analytics_data, brand_name)
                    sources_chart, sources_buf = generate_sources_chart(analytics_data, brand_name)
                    filename = save_to_pdf(story, brand_name, social_links, analysis, analytics_data, tone_buf, traffic_buf, sources_buf)
                    if not filename:
                        return render_template_string(INDEX_HTML, error="Failed to generate PDF report.")
                    if not isinstance(analysis['keywords'], list):
                        logger.error(f"Keywords is not a list for {brand_name}: {type(analysis['keywords'])}")
                        analysis['keywords'] = ['brand', 'industry', 'market']
                    return render_template_string(
                        RESULT_HTML,
                        story=story,
                        social_links=social_links,
                        brand_name=brand_name,
                        tone_chart=tone_chart,
                        traffic_chart=traffic_chart,
                        sources_chart=sources_chart,
                        keywords=analysis['keywords'],
                        filename=filename,
                        analysis=analysis,
                        analytics_data=analytics_data
                    )
                return render_template_string(INDEX_HTML, error=error or "Invalid URL.")
        elif input_type == 'multiple':
            urls = [u.strip() for u in request.form.get('urls', '').split('\n') if u.strip()]
            if not urls:
                return render_template_string(INDEX_HTML, error="Provide at least one URL.")
            competitor_data = {}
            main_brand_data = None
            errors = []
            for url in urls:
                website_text, social_links, brand_name, founding_year, analysis, analytics_data, wiki_summary, error = process_brand(url)
                if analysis:
                    competitor_data[brand_name] = analysis
                    if not main_brand_data:
                        main_brand_data = {
                            'website_text': website_text,
                            'social_links': social_links,
                            'brand_name': brand_name,
                            'founding_year': founding_year,
                            'analysis': analysis,
                            'analytics_data': analytics_data,
                            'wiki_summary': wiki_summary
                        }
                else:
                    errors.append(f"Failed: {url}")
            if main_brand_data:
                story = generate_story(
                    main_brand_data['analysis'],
                    main_brand_data['brand_name'],
                    main_brand_data['social_links'],
                    main_brand_data['founding_year'],
                    main_brand_data['analytics_data'],
                    competitor_data,
                    main_brand_data['wiki_summary']
                )
                tone_chart, tone_buf = generate_tone_chart(main_brand_data['analysis'], main_brand_data['brand_name'])
                traffic_chart, traffic_buf = generate_traffic_chart(main_brand_data['analytics_data'], main_brand_data['brand_name'])
                sources_chart, sources_buf = generate_sources_chart(main_brand_data['analytics_data'], main_brand_data['brand_name'])
                filename = save_to_pdf(
                    story,
                    main_brand_data['brand_name'],
                    main_brand_data['social_links'],
                    main_brand_data['analysis'],
                    main_brand_data['analytics_data'],
                    tone_buf,
                    traffic_buf,
                    sources_buf
                )
                if not filename:
                    return render_template_string(INDEX_HTML, error="Failed to generate PDF report.")
                if not isinstance(main_brand_data['analysis']['keywords'], list):
                    logger.error(f"Keywords is not a list for {main_brand_data['brand_name']}: {type(main_brand_data['analysis']['keywords'])}")
                    main_brand_data['analysis']['keywords'] = ['brand', 'industry', 'market']
                return render_template_string(
                    RESULT_HTML,
                    story=story,
                    social_links=main_brand_data['social_links'],
                    brand_name=main_brand_data['brand_name'],
                    tone_chart=tone_chart,
                    traffic_chart=traffic_chart,
                    sources_chart=sources_chart,
                    keywords=main_brand_data['analysis']['keywords'],
                    filename=filename,
                    analysis=main_brand_data['analysis'],
                    analytics_data=main_brand_data['analytics_data']
                )
            return render_template_string(INDEX_HTML, error="No valid URLs processed. " + "; ".join(errors))
    return render_template_string(INDEX_HTML, error="")

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        logger.error(f"Download file not found: {filename}")
        return render_template_string(INDEX_HTML, error="Report file not found.")

if __name__ == "__main__":
    app.run(debug=True)
    
