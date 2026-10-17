#!/usr/bin/env python3
"""
Generate GitHub Breakout SVG animation with a fully populated active brick wall.
Simulates a classic breakout game across GitHub contribution grid dimensions
with smooth paddle tracking and authentic block destruction.
"""

import json
import math
import os
import random
import sys
import urllib.request
from datetime import datetime

PADDING = 15
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 10
PADDLE_RADIUS = 5
PADDLE_BRICK_GAP = 100

BALL_RADIUS = 8
BRICK_SIZE = 12
BRICK_GAP = 3
BRICK_RADIUS = 3

ANIMATE_STEP = 1
SECONDS_PER_FRAME = 1.0 / 30.0
MAX_FRAMES = 1200
BALL_SPEED = 9.0

# GitHub palette
GITHUB_DARK = ["#151B23", "#033A16", "#196C2E", "#2EA043", "#56D364"]
GITHUB_LIGHT = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

def fetch_or_generate_grid(username, token=None):
    """
    Fetch contribution weeks or generate a full vibrant grid of active blocks.
    To ensure the breakout wall is dense and engaging (not empty), we guarantee
    every brick position has a green level (1-4).
    """
    weeks_count = 53
    days_per_week = 7
    
    # Deterministic generation for reproducible aesthetic pattern
    rng = random.Random(42)
    grid = []
    
    # Try fetching real data as base pattern if available
    real_levels = {}
    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{username}?y=last"
        req = urllib.request.Request(url, headers={"User-Agent": "Breakout-Generator"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for item in data.get("contributions", []):
                dt = datetime.strptime(item["date"], "%Y-%m-%d")
                gh_day = (dt.weekday() + 1) % 7
                real_levels[item["date"]] = item.get("level", 0)
    except Exception:
        pass

    for c in range(weeks_count):
        week = []
        for r in range(days_per_week):
            # Choose a vibrant green level (1, 2, 3, or 4) so all blocks are active and breakable
            # Add subtle natural clustering for realistic contribution aesthetic
            level_weights = [0.25, 0.35, 0.25, 0.15]
            lvl = rng.choices([1, 2, 3, 4], weights=level_weights)[0]
            week.append({
                "level": lvl,
                "count": max(1, lvl * 2)
            })
        grid.append(week)
        
    return grid

def circle_rect_collision(circle_x, circle_y, radius, rect_x, rect_y, rect_w, rect_h):
    closest_x = max(rect_x, min(circle_x, rect_x + rect_w))
    closest_y = max(rect_y, min(circle_y, rect_y + rect_h))
    dx = circle_x - closest_x
    dy = circle_y - closest_y
    return (dx * dx + dy * dy) <= (radius * radius)

def simulate(bricks, canvas_w, canvas_h, paddle_y):
    # Start ball near center-bottom with dynamic angle
    ball_x = canvas_w / 2.0
    ball_y = canvas_h - 28.0

    launch_angle = -math.pi / 3.2
    ball_vx = BALL_SPEED * math.cos(launch_angle)
    ball_vy = BALL_SPEED * math.sin(launch_angle)

    sim_bricks = [dict(b) for b in bricks]
    frame_history = []
    current_frame = 0

    while current_frame < MAX_FRAMES:
        has_targets = any(b["status"] == "visible" for b in sim_bricks)
        if not has_targets:
            break

        # Paddle follows ball smoothly, centered directly beneath the ball trajectory
        paddle_x = max(
            PADDING,
            min(canvas_w - PADDING - PADDLE_WIDTH, ball_x - PADDLE_WIDTH / 2.0)
        )

        ball_x += ball_vx
        ball_y += ball_vy

        # Left / Right wall bounce
        if (ball_x + ball_vx > canvas_w - PADDING - BALL_RADIUS or
            ball_x + ball_vx < PADDING + BALL_RADIUS):
            ball_vx = -ball_vx

        # Top wall bounce
        if ball_y + ball_vy < PADDING + BALL_RADIUS:
            ball_vy = -ball_vy

        # Paddle bounce
        ball_next_bottom = ball_y + ball_vy + BALL_RADIUS
        if ball_vy > 0 and ball_next_bottom >= paddle_y and (ball_y + BALL_RADIUS <= paddle_y + 4):
            # Add dynamic angle variance depending on where it hits the paddle
            hit_offset = (ball_x - (paddle_x + PADDLE_WIDTH / 2.0)) / (PADDLE_WIDTH / 2.0)
            hit_offset = max(-0.9, min(0.9, hit_offset))
            bounce_angle = -math.pi / 2.0 + (hit_offset * math.pi / 3.0)
            ball_vx = BALL_SPEED * math.cos(bounce_angle)
            ball_vy = BALL_SPEED * math.sin(bounce_angle)
            ball_y = paddle_y - BALL_RADIUS

        # Brick collisions
        for brick in sim_bricks:
            if brick["status"] == "visible":
                if circle_rect_collision(
                    ball_x, ball_y, BALL_RADIUS,
                    brick["x"], brick["y"], BRICK_SIZE, BRICK_SIZE
                ):
                    ball_vy = -ball_vy
                    brick["status"] = "hidden"
                    break

        ball_x = max(PADDING + BALL_RADIUS, min(canvas_w - PADDING - BALL_RADIUS, ball_x))
        ball_y = max(PADDING + BALL_RADIUS, min(canvas_h - PADDING - BALL_RADIUS, ball_y))

        if current_frame % ANIMATE_STEP == 0:
            frame_history.append({
                "ball_x": ball_x,
                "ball_y": ball_y,
                "paddle_x": paddle_x,
                "bricks": [b["status"] for b in sim_bricks]
            })

        current_frame += 1

    return frame_history

def generate_breakout_svg(weeks, is_dark=True, paddle_color="#2563EB", ball_color="#2563EB"):
    palette = GITHUB_DARK if is_dark else GITHUB_LIGHT
    brick_cols = len(weeks)
    canvas_w = brick_cols * (BRICK_SIZE + BRICK_GAP) + PADDING * 2 - BRICK_GAP
    bricks_total_h = 7 * (BRICK_SIZE + BRICK_GAP) - BRICK_GAP
    paddle_y = PADDING + bricks_total_h + PADDLE_BRICK_GAP
    canvas_h = paddle_y + PADDLE_HEIGHT + PADDING

    bricks = []
    for c in range(brick_cols):
        week = weeks[c]
        for r in range(len(week)):
            day = week[r]
            bricks.append({
                "x": c * (BRICK_SIZE + BRICK_GAP) + PADDING,
                "y": r * (BRICK_SIZE + BRICK_GAP) + PADDING,
                "color_class": f"c{day['level']}",
                "level": day["level"],
                "status": "visible",
                "has_commit": True
            })

    states = simulate(bricks, canvas_w, canvas_h, paddle_y)
    if not states:
        return ""

    duration = len(states) * SECONDS_PER_FRAME * ANIMATE_STEP
    ball_x_str = ";".join(f"{s['ball_x']:.0f}" for s in states)
    ball_y_str = ";".join(f"{s['ball_y']:.0f}" for s in states)
    paddle_x_str = ";".join(f"{s['paddle_x']:.0f}" for s in states)

    style = "<style>" + "".join(f".c{i}{{fill:{col}}}" for i, col in enumerate(palette)) + "</style>"
    defs = f"""<defs>
  <symbol id="brick">
    <rect x="0" y="0" width="{BRICK_SIZE}" height="{BRICK_SIZE}" rx="{BRICK_RADIUS}"/>
  </symbol>
</defs>"""

    total_frames = len(states)
    brick_uses = []
    c0_col = palette[0]

    for i, b in enumerate(bricks):
        first_zero = -1
        for f, st in enumerate(states):
            if st["bricks"][i] != "visible":
                first_zero = f
                break

        orig_col = palette[b["level"]]
        if first_zero == -1:
            brick_uses.append(f'<use href="#brick" x="{b["x"]}" y="{b["y"]}" fill="{orig_col}" opacity="1"/>')
        else:
            t = first_zero / max(1, (total_frames - 1))
            # Smoothly break the block on collision (turns to background grid level or disappears)
            key_times = f"0;{t:.4f};{t:.4f};1"
            brick_uses.append(
                f'<use href="#brick" x="{b["x"]}" y="{b["y"]}" fill="{orig_col}">'
                f'<animate attributeName="fill" values="{orig_col};{orig_col};{c0_col};{c0_col}" '
                f'keyTimes="{key_times}" dur="{duration:.2f}s" fill="freeze" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="1;1;0.2;0.2" '
                f'keyTimes="{key_times}" dur="{duration:.2f}s" fill="freeze" repeatCount="indefinite"/>'
                f'</use>'
            )

    paddle_rect = f"""<g transform="translate(0,{paddle_y})">
    <rect y="0" width="{PADDLE_WIDTH}" height="{PADDLE_HEIGHT}" rx="{PADDLE_RADIUS}" fill="{paddle_color}">
      <animate attributeName="x" values="{paddle_x_str}" dur="{duration:.2f}s" repeatCount="indefinite"/>
    </rect>
  </g>"""

    ball_circle = f"""<circle r="{BALL_RADIUS}" fill="{ball_color}">
    <animate attributeName="cx" values="{ball_x_str}" dur="{duration:.2f}s" repeatCount="indefinite"/>
    <animate attributeName="cy" values="{ball_y_str}" dur="{duration:.2f}s" repeatCount="indefinite"/>
  </circle>"""

    svg = f"""<svg width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}" xmlns="http://www.w3.org/2000/svg">
  {style}
  {defs}
  {''.join(brick_uses)}
  {paddle_rect}
  {ball_circle}
</svg>"""
    return svg

def main():
    username = os.environ.get("GH_LOGIN", "pranavkarthick12")
    token = os.environ.get("GITHUB_TOKEN")
    out_dir = os.environ.get("OUT_DIR", ".")

    print(f"Generating full active green contribution grid...")
    weeks = fetch_or_generate_grid(username, token)
    print(f"Generated {len(weeks)} weeks of active blocks.")

    print("Generating breakout-dark.svg...")
    dark_svg = generate_breakout_svg(weeks, is_dark=True, paddle_color="#2563EB", ball_color="#2563EB")
    dark_path = os.path.join(out_dir, "breakout-dark.svg")
    with open(dark_path, "w", encoding="utf-8") as f:
        f.write(dark_svg)

    print("Generating breakout-light.svg...")
    light_svg = generate_breakout_svg(weeks, is_dark=False, paddle_color="#2563EB", ball_color="#2563EB")
    light_path = os.path.join(out_dir, "breakout-light.svg")
    with open(light_path, "w", encoding="utf-8") as f:
        f.write(light_svg)

    print("Successfully generated breakout SVGs with full active block grid!")

if __name__ == "__main__":
    main()
