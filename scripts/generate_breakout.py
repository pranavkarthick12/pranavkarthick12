#!/usr/bin/env python3
"""
Generate GitHub Breakout SVG animation from contribution graph.
Ported from cyprieng/github-breakout with support for both GitHub GraphQL API
and fallback public contribution data.
"""

import json
import math
import os
import sys
import urllib.request
from datetime import datetime

PADDING = 15
PADDLE_WIDTH = 75
PADDLE_HEIGHT = 10
PADDLE_RADIUS = 5
PADDLE_BRICK_GAP = 100

BALL_RADIUS = 8
BRICK_SIZE = 12
BRICK_GAP = 3
BRICK_RADIUS = 3

ANIMATE_STEP = 1
SECONDS_PER_FRAME = 1.0 / 30.0
MAX_FRAMES = 30000
BALL_SPEED = 10.0

GITHUB_DARK = ["#151B23", "#033A16", "#196C2E", "#2EA043", "#56D364"]
GITHUB_LIGHT = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

def fetch_contributions(username, token=None):
    if token:
        try:
            query = """
            query($userName:String!) {
              user(login: $userName){
                contributionsCollection {
                  contributionCalendar {
                    weeks {
                      contributionDays {
                        contributionLevel
                        contributionCount
                        color
                      }
                    }
                  }
                }
              }
            }"""
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=json.dumps({"query": query, "variables": {"userName": username}}).encode("utf-8"),
                headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "Breakout-Generator"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                weeks_data = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
                weeks = []
                for w in weeks_data:
                    days = []
                    for d in w["contributionDays"]:
                        lvl_map = {
                            "FOURTH_QUARTILE": 4,
                            "THIRD_QUARTILE": 3,
                            "SECOND_QUARTILE": 2,
                            "FIRST_QUARTILE": 1
                        }
                        lvl = lvl_map.get(d["contributionLevel"], 0)
                        days.append({
                            "level": lvl,
                            "count": d["contributionCount"]
                        })
                    weeks.append(days)
                return weeks
        except Exception as e:
            print(f"GraphQL fetch failed ({e}), falling back to public contributions API...", file=sys.stderr)

    url = f"https://github-contributions-api.jogruber.de/v4/{username}?y=last"
    req = urllib.request.Request(url, headers={"User-Agent": "Breakout-Generator"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        contributions = data["contributions"]

        # GitHub calendars arrange days in columns of 7 (Sunday=0 to Saturday=6)
        weeks = []
        current_week = []
        for item in contributions:
            dt = datetime.strptime(item["date"], "%Y-%m-%d")
            # In Python, weekday() is Monday=0 ... Sunday=6.
            # GitHub calendar starts week on Sunday.
            gh_day = (dt.weekday() + 1) % 7
            
            # Start new week on Sunday if current_week has items
            if gh_day == 0 and len(current_week) > 0:
                weeks.append(current_week)
                current_week = []
            
            current_week.append({
                "level": item.get("level", 0),
                "count": item.get("count", 0)
            })
            
        if current_week:
            weeks.append(current_week)
        return weeks

def circle_rect_collision(circle_x, circle_y, radius, rect_x, rect_y, rect_w, rect_h):
    closest_x = max(rect_x, min(circle_x, rect_x + rect_w))
    closest_y = max(rect_y, min(circle_y, rect_y + rect_h))
    dx = circle_x - closest_x
    dy = circle_y - closest_y
    return (dx * dx + dy * dy) <= (radius * radius)

def simulate(bricks, canvas_w, canvas_h, paddle_y, enable_ghost_bricks):
    ball_x = canvas_w / 2.0
    ball_y = canvas_h - 30.0

    launch_angle = -math.pi / 4.0
    ball_vx = BALL_SPEED * math.cos(launch_angle)
    ball_vy = BALL_SPEED * math.sin(launch_angle)

    sim_bricks = [dict(b) for b in bricks]
    frame_history = []
    current_frame = 0

    while current_frame < MAX_FRAMES:
        has_targets = any(
            b["status"] == "visible" and (not enable_ghost_bricks or b["has_commit"])
            for b in sim_bricks
        )
        if not has_targets:
            break

        paddle_x = max(
            PADDING,
            min(canvas_w - PADDING - PADDLE_WIDTH, ball_x - PADDLE_WIDTH / 2.0)
        )

        ball_x += ball_vx
        ball_y += ball_vy

        if (ball_x + ball_vx > canvas_w - PADDING - BALL_RADIUS or
            ball_x + ball_vx < PADDING + BALL_RADIUS):
            ball_vx = -ball_vx

        if ball_y + ball_vy < PADDING + BALL_RADIUS:
            ball_vy = -ball_vy

        ball_next_bottom = ball_y + ball_vy + BALL_RADIUS
        if ball_vy > 0 and ball_next_bottom >= paddle_y and (ball_y + BALL_RADIUS <= paddle_y):
            ball_vy = -abs(ball_vy)
            ball_y = paddle_y - BALL_RADIUS

        for brick in sim_bricks:
            if brick["status"] == "visible" and (not enable_ghost_bricks or brick["has_commit"]):
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

def generate_breakout_svg(weeks, is_dark=True, enable_ghost_bricks=True, paddle_color="#1F6FEB", ball_color="#1F6FEB"):
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
                "has_commit": day["count"] > 0
            })

    states = simulate(bricks, canvas_w, canvas_h, paddle_y, enable_ghost_bricks)
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
    for i, b in enumerate(bricks):
        first_zero = -1
        for f, st in enumerate(states):
            if st["bricks"][i] != "visible":
                first_zero = f
                break

        if first_zero == -1:
            brick_uses.append(f'<use href="#brick" x="{b["x"]}" y="{b["y"]}" class="{b["color_class"]}" opacity="1"/>')
        else:
            t = first_zero / max(1, (total_frames - 1))
            if enable_ghost_bricks:
                orig_col = palette[b["level"]]
                c0_col = palette[0]
                brick_uses.append(
                    f'<use href="#brick" x="{b["x"]}" y="{b["y"]}" fill="{orig_col}">'
                    f'<animate attributeName="fill" values="{orig_col};{orig_col};{c0_col};{c0_col}" '
                    f'keyTimes="0;{t:.4f};{t:.4f};1" dur="{duration:.2f}s" fill="freeze" repeatCount="indefinite"/>'
                    f'</use>'
                )
            else:
                key_times = f"0;{t:.4f};{t:.4f};1"
                brick_uses.append(
                    f'<use href="#brick" x="{b["x"]}" y="{b["y"]}" class="{b["color_class"]}">'
                    f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="{key_times}" '
                    f'dur="{duration:.2f}s" fill="freeze" repeatCount="indefinite"/>'
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

    print(f"Fetching contribution calendar for {username}...")
    weeks = fetch_contributions(username, token)
    print(f"Loaded {len(weeks)} weeks of contribution data.")

    print("Generating breakout-dark.svg...")
    dark_svg = generate_breakout_svg(weeks, is_dark=True, enable_ghost_bricks=True, paddle_color="#2563EB", ball_color="#2563EB")
    dark_path = os.path.join(out_dir, "breakout-dark.svg")
    with open(dark_path, "w", encoding="utf-8") as f:
        f.write(dark_svg)

    print("Generating breakout-light.svg...")
    light_svg = generate_breakout_svg(weeks, is_dark=False, enable_ghost_bricks=True, paddle_color="#2563EB", ball_color="#2563EB")
    light_path = os.path.join(out_dir, "breakout-light.svg")
    with open(light_path, "w", encoding="utf-8") as f:
        f.write(light_svg)

    print("Successfully generated breakout SVGs!")

if __name__ == "__main__":
    main()
