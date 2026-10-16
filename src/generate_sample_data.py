import csv
import random
import os

random.seed(42)

PLATFORMS = [
    "GitHub", "GitLab", "StackOverflow", "HackerRank", "Kaggle", "Replit",
    "Twitter", "Instagram", "Facebook", "TikTok", "Pinterest", "Snapchat",
    "Reddit", "Medium", "Quora", "Tumblr", "Flickr", "Vimeo",
    "YouTube", "Twitch", "SoundCloud", "Spotify", "Steam", "Roblox",
    "Chess", "Duolingo", "Goodreads", "Letterboxd", "Dribbble", "Behance",
    "LinkedIn", "Telegram", "Discord", "Patreon", "eBay", "Etsy",
    "Wattpad", "DeviantArt", "Slideshare", "Scribd",
]

USERS = {
    "demo_user_alpha": 0.65,
    "demo_user_beta": 0.30,
    "demo_user_gamma": 0.10,
}

os.makedirs("data", exist_ok=True)

for username, p in USERS.items():
    path = f"data/{username}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["username", "name", "url_main", "url_user",
                    "exists", "http_status", "response_time_s"])
        for name in PLATFORMS:
            found = random.random() < p
            slug = name.lower()
            w.writerow([
                username, name,
                f"https://{slug}.example.com/",
                f"https://{slug}.example.com/{username}",
                "Claimed" if found else "Available",
                200 if found else 404,
                round(random.uniform(0.2, 2.5), 3),
            ])
    print("oluştu:", path)