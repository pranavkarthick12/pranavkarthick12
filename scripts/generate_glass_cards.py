#!/usr/bin/env python3
"""
Generate high-fidelity glassmorphism SVGs with glowing white orbiting outline beams
for all sections in the GitHub profile README.
"""

import os
import sys

def make_glass_svg(width, height, content_xml, orbit_dur="6s"):
    rx = 16
    inset = 2
    w_box = width - inset * 2
    h_box = height - inset * 2
    
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">
  <defs>
    <!-- Dark Glass Background -->
    <linearGradient id="bgDark" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.06"/>
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.02"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.04"/>
    </linearGradient>

    <!-- Light Glass Background -->
    <linearGradient id="bgLight" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" stop-opacity="0.04"/>
      <stop offset="50%" stop-color="#0f172a" stop-opacity="0.015"/>
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0.03"/>
    </linearGradient>

    <!-- Subtle Static Glass Border -->
    <linearGradient id="borderGradDark" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.18"/>
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.12"/>
    </linearGradient>

    <linearGradient id="borderGradLight" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" stop-opacity="0.15"/>
      <stop offset="50%" stop-color="#0f172a" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0.12"/>
    </linearGradient>

    <!-- Outer Glow Filter -->
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3.5" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <style>
    .card-bg {{
      fill: url(#bgDark);
      stroke: url(#borderGradDark);
    }}
    .text-title {{
      fill: #f0f6fc;
      font-size: 20px;
      font-weight: 700;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }}
    .text-subtitle {{
      fill: #e6edf3;
      font-size: 15px;
      font-weight: 600;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }}
    .text-body {{
      fill: #8b949e;
      font-size: 13.5px;
      font-weight: 400;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }}
    .text-strong {{
      fill: #c9d1d9;
      font-weight: 600;
    }}
    .text-accent {{
      fill: #58a6ff;
      font-weight: 600;
    }}
    .bullet {{
      fill: #3b82f6;
    }}
    .row-line {{
      stroke: #30363d;
      stroke-width: 1;
    }}
    .orbit-beam {{
      stroke: #ffffff;
      stroke-width: 2.2;
      stroke-linecap: round;
      filter: url(#glow);
    }}

    @media (prefers-color-scheme: light) {{
      .card-bg {{
        fill: url(#bgLight);
        stroke: url(#borderGradLight);
      }}
      .text-title {{
        fill: #1f2328;
      }}
      .text-subtitle {{
        fill: #24292f;
      }}
      .text-body {{
        fill: #57606a;
      }}
      .text-strong {{
        fill: #24292f;
      }}
      .text-accent {{
        fill: #0969da;
      }}
      .bullet {{
        fill: #2563eb;
      }}
      .row-line {{
        stroke: #d0d7de;
      }}
      .orbit-beam {{
        stroke: #2563eb;
      }}
    }}
  </style>

  <!-- Ambient Backdrop -->
  <rect x="{inset}" y="{inset}" width="{w_box}" height="{h_box}" rx="{rx}" fill="none" opacity="0.4" />

  <!-- Glass Card Base -->
  <rect class="card-bg" x="{inset}" y="{inset}" width="{w_box}" height="{h_box}" rx="{rx}" stroke-width="1.2" />

  <!-- White Orbiting Beam -->
  <rect x="{inset}" y="{inset}" width="{w_box}" height="{h_box}" rx="{rx}" fill="none"
        class="orbit-beam" pathLength="1000"
        stroke-dasharray="140 860">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="{orbit_dur}" repeatCount="indefinite" />
  </rect>

  <!-- Content -->
  <g transform="translate(32, 28)">
    {content_xml}
  </g>
</svg>"""

def generate_what_i_do():
    content = """
    <text x="0" y="16" class="text-title">What I Do</text>

    <!-- 1. Full-Stack Development -->
    <text x="0" y="56" class="text-subtitle">Full-Stack Development</text>
    <text x="0" y="78" class="text-body">Build responsive web applications, integrate RESTful APIs, implement backend logic, and work with databases using modern development technologies.</text>

    <!-- 2. Software Quality & Accessibility -->
    <text x="0" y="120" class="text-subtitle">Software Quality &amp; Accessibility</text>
    <text x="0" y="142" class="text-body">Test applications, investigate accessibility issues, troubleshoot defects, document findings, and support quality validation workflows.</text>

    <!-- 3. AI-Assisted Development & Automation -->
    <text x="0" y="184" class="text-subtitle">AI-Assisted Development &amp; Automation</text>
    <text x="0" y="206" class="text-body">Explore AI-assisted software development using Claude, ChatGPT, and Antigravity to support implementation, debugging, testing, and repeatable quality checks.</text>

    <!-- 4. Frontend & UI/UX -->
    <text x="0" y="248" class="text-subtitle">Frontend &amp; UI/UX</text>
    <text x="0" y="270" class="text-body">Develop responsive interfaces with React and modern web technologies, with an interest in usability, interface consistency, and clean visual design.</text>
    """
    return make_glass_svg(850, 330, content, orbit_dur="6s")

def generate_skills():
    rows = [
        ("Programming Languages", "JavaScript, Python, Java, C++"),
        ("Frontend Development", "React.js, HTML5, CSS3, Redux Toolkit"),
        ("Backend Development", "Node.js, Express.js, Spring Boot, Flask, REST APIs"),
        ("Databases", "MongoDB, MySQL"),
        ("Core Concepts", "DBMS, OOP, Data Structures and Algorithms, Operating Systems"),
        ("AI-Assisted Development", "Claude, ChatGPT, Antigravity, AI-assisted development workflows"),
        ("Testing & Quality", "Playwright, Selenium, Accessibility Testing, Debugging"),
        ("Libraries", "Pandas, NumPy, Scikit-learn"),
        ("Cloud & Deployment", "AWS, Docker, Vercel"),
        ("Tools", "Git, GitHub, VS Code"),
    ]
    
    xml = ['<text x="0" y="16" class="text-title">Technical Skills</text>']
    y_start = 54
    row_height = 36
    
    # Table Header Line
    xml.append(f'<text x="0" y="{y_start}" class="text-strong" font-size="14">Category</text>')
    xml.append(f'<text x="240" y="{y_start}" class="text-strong" font-size="14">Technologies and Skills</text>')
    xml.append(f'<line x1="0" y1="{y_start + 10}" x2="786" y2="{y_start + 10}" class="row-line" />')
    
    cur_y = y_start + 36
    for cat, skills in rows:
        xml.append(f'<text x="0" y="{cur_y}" class="text-strong">{cat}</text>')
        xml.append(f'<text x="240" y="{cur_y}" class="text-body">{skills}</text>')
        xml.append(f'<line x1="0" y1="{cur_y + 10}" x2="786" y2="{cur_y + 10}" class="row-line" opacity="0.4" />')
        cur_y += row_height
        
    return make_glass_svg(850, 480, "".join(xml), orbit_dur="7s")

def generate_projects():
    content = """
    <text x="0" y="16" class="text-title">Selected Projects</text>

    <!-- Project 1 -->
    <text x="0" y="56" class="text-subtitle">1. AI-Powered Interview Assistant</text>
    <text x="0" y="78" class="text-body"><tspan class="text-strong">Technologies:</tspan> React, Redux Toolkit, Ant Design</text>
    <text x="0" y="98" class="text-body">Built an interview simulation platform designed to support structured technical interview practice.</text>
    <circle cx="4" cy="118" r="2.5" class="bullet" /><text x="16" y="122" class="text-body">Resume parsing for personalized interview experiences.</text>
    <circle cx="4" cy="138" r="2.5" class="bullet" /><text x="16" y="142" class="text-body">Timed interview sessions and automated interview scoring.</text>
    <circle cx="4" cy="158" r="2.5" class="bullet" /><text x="16" y="162" class="text-body">Separate interfaces for different user roles and responsive dashboard.</text>

    <line x1="0" y1="180" x2="786" y2="180" class="row-line" opacity="0.3" />

    <!-- Project 2 -->
    <text x="0" y="212" class="text-subtitle">2. PhishSiren — Phishing &amp; Spam Detection</text>
    <text x="0" y="234" class="text-body"><tspan class="text-strong">Technologies:</tspan> Flask, Scikit-learn, Gmail API, MongoDB</text>
    <text x="0" y="254" class="text-body">Developed a web application focused on detecting phishing and spam messages using a trained machine learning model.</text>
    <circle cx="4" cy="274" r="2.5" class="bullet" /><text x="16" y="278" class="text-body">Integrated Gmail using OAuth 2.0 with real-time message classification.</text>
    <circle cx="4" cy="294" r="2.5" class="bullet" /><text x="16" y="298" class="text-body">Maintained prediction history in MongoDB and web analysis interface.</text>

    <line x1="0" y1="316" x2="786" y2="316" class="row-line" opacity="0.3" />

    <!-- Project 3 -->
    <text x="0" y="348" class="text-subtitle">3. Pachyderm Partner — Elephant Safety System</text>
    <text x="0" y="370" class="text-body"><tspan class="text-strong">Technologies:</tspan> ESP32, HC-05 Bluetooth, Mobile App</text>
    <text x="0" y="390" class="text-body">Developed an elephant-safety solution using an ESP32-based wearable and Bluetooth-controlled vibration alerts to support mahout safety.</text>
    <circle cx="4" cy="410" r="2.5" class="bullet" /><text x="16" y="414" class="text-body">ESP32 hardware implementation with HC-05 Bluetooth communication.</text>
    <circle cx="4" cy="430" r="2.5" class="bullet" /><text x="16" y="434" class="text-body">Mobile application integration with safety-focused alert automation.</text>
    """
    return make_glass_svg(850, 490, content, orbit_dur="7.5s")

def generate_experience():
    content = """
    <text x="0" y="16" class="text-title">Professional Experience</text>

    <!-- Role 1 -->
    <text x="0" y="56" class="text-subtitle">Software Quality and Accessibility Engineer Intern</text>
    <text x="0" y="78" class="text-accent">Hudsmer Business Solutions | Present</text>
    <circle cx="4" cy="100" r="2.5" class="bullet" /><text x="16" y="104" class="text-body">Test and troubleshoot software quality and PDF/web accessibility issues.</text>
    <circle cx="4" cy="120" r="2.5" class="bullet" /><text x="16" y="124" class="text-body">Investigate defects, document findings, and support engineering follow-up.</text>
    <circle cx="4" cy="140" r="2.5" class="bullet" /><text x="16" y="144" class="text-body">Develop and improve technical tools using AI-assisted workflows and Antigravity.</text>
    <circle cx="4" cy="160" r="2.5" class="bullet" /><text x="16" y="164" class="text-body">Work on repeatable checks, debugging, and quality validation.</text>
    <text x="16" y="188" class="text-body"><tspan class="text-strong">Tools:</tspan> Claude, ChatGPT, Antigravity, Docker, Vercel, Playwright, Selenium.</text>

    <line x1="0" y1="206" x2="786" y2="206" class="row-line" opacity="0.3" />

    <!-- Role 2 -->
    <text x="0" y="238" class="text-subtitle">MERN Stack Intern</text>
    <text x="0" y="260" class="text-accent">RAMPeX Technologies | January 2024</text>
    <circle cx="4" cy="282" r="2.5" class="bullet" /><text x="16" y="286" class="text-body">Built and deployed two MERN-stack web applications.</text>
    <circle cx="4" cy="302" r="2.5" class="bullet" /><text x="16" y="306" class="text-body">Developed responsive UI components and REST APIs using MongoDB, Express.js, React, Node.js.</text>
    <circle cx="4" cy="322" r="2.5" class="bullet" /><text x="16" y="326" class="text-body">Supported debugging and application optimization.</text>

    <line x1="0" y1="344" x2="786" y2="344" class="row-line" opacity="0.3" />

    <!-- Role 3 -->
    <text x="0" y="376" class="text-subtitle">Spring Boot and React Intern</text>
    <text x="0" y="398" class="text-accent">July 2025</text>
    <circle cx="4" cy="420" r="2.5" class="bullet" /><text x="16" y="424" class="text-body">Developed and integrated RESTful APIs using Spring Boot and React.</text>
    <circle cx="4" cy="440" r="2.5" class="bullet" /><text x="16" y="444" class="text-body">Worked on backend logic, frontend implementation, and database operations.</text>
    """
    return make_glass_svg(850, 500, content, orbit_dur="7.5s")

def generate_certifications():
    certs = [
        ("Data Analytics Essentials", "Cisco Networking Academy | 8 June 2026"),
        ("Python Essentials", "Cisco Networking Academy | 10 July 2026"),
        ("Python (Basic)", "HackerRank | 2025"),
        ("Cloud Foundation", "AWS | 2025"),
        ("React.js", "Codecademy | 2025"),
        ("Data Structures and Algorithms (C++)", "Udemy | 2025"),
        ("MongoDB Fundamentals", "Infosys Springboard | 2025"),
    ]
    xml = ['<text x="0" y="16" class="text-title">Certifications</text>']
    cur_y = 56
    for name, issuer in certs:
        xml.append(f'<circle cx="4" cy="{cur_y - 4}" r="2.5" class="bullet" />')
        xml.append(f'<text x="16" y="{cur_y}" class="text-body"><tspan class="text-strong">{name}</tspan> — {issuer}</text>')
        cur_y += 28
    return make_glass_svg(850, cur_y + 24, "".join(xml), orbit_dur="6s")

def generate_achievements():
    achievements = [
        ("2nd Place — Thiran Hackathon / Project Expo", "Developed an application for an elephant-safety system."),
        ("Flipkart GRiD 7.0", "Participated and reached the semifinals."),
        ("Best Speaker — Toastmasters", "Recognized for public speaking and communication."),
        ("Vice President — Media & Branding, Student Leadership Council", "Led campus media, branding, and promotional initiatives."),
    ]
    xml = ['<text x="0" y="16" class="text-title">Achievements &amp; Leadership</text>']
    cur_y = 56
    for title, desc in achievements:
        xml.append(f'<circle cx="4" cy="{cur_y - 4}" r="2.5" class="bullet" />')
        xml.append(f'<text x="16" y="{cur_y}" class="text-body"><tspan class="text-strong">{title}:</tspan> {desc}</text>')
        cur_y += 28
    return make_glass_svg(850, cur_y + 24, "".join(xml), orbit_dur="6s")

def main():
    out_dir = "."
    files = {
        "what-i-do-card.svg": generate_what_i_do(),
        "skills-card.svg": generate_skills(),
        "projects-card.svg": generate_projects(),
        "experience-card.svg": generate_experience(),
        "certifications-card.svg": generate_certifications(),
        "achievements-card.svg": generate_achievements(),
    }
    
    for filename, content in files.items():
        filepath = os.path.join(out_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {filename}")

if __name__ == "__main__":
    main()
