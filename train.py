import os
import gymnasium as gym
from stable_baselines3 import PPO
import requests
import time

# GitHub repo details
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "nerddotdad"
REPO_NAME = "ai-gamer"
ISSUE_NUMBER = 1  # The issue number to monitor and update (change this if necessary)
ALLOWED_USER = "nerddotdad"  # Replace this with your GitHub username

# Define the polling interval (in seconds)
POLLING_INTERVAL = 60  # Poll every 60 seconds

# Function to create GitHub issue (only used once)
def create_github_issue(title, body):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"title": title, "body": body}
    response = requests.post(url, json=data, headers=headers)
    return response.status_code, response.json()

# Function to fetch the latest comments on the issue
def fetch_github_issue_comments():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{ISSUE_NUMBER}/comments"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    return response.json()

# Function to update the existing issue
def update_github_issue(issue_number, body):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"body": body}  # Update the issue body
    response = requests.patch(url, json=data, headers=headers)
    return response.status_code, response.json()

# Function to parse the tweaks from a comment
def parse_tweaks_from_comment(comment):
    tweaks = {}
    if "[tweaks]" in comment and "[/tweaks]" in comment:
        tweaks_block = comment.split("[tweaks]")[1].split("[/tweaks]")[0]
        for tweak in tweaks_block.split(" "):
            if "=" in tweak:
                key, value = tweak.split("=")
                tweaks[key.strip()] = value.strip()
    return tweaks

# Function to format the issue body
def format_github_issue(env_name, episode_count, avg_reward, max_reward, training_time, avg_length, loss, exploration_rate, checkpoint_name, behavior_notes, next_steps):
    return f"""
## 🎮 AI Training Session Summary

**Environment:** {env_name}
**Total Episodes:** {episode_count}
**Avg. Reward:** {avg_reward}
**Max Reward:** {max_reward}
**Training Time:** {training_time}

---

## 📈 Training Stats
- Avg. Episode Length: {avg_length} steps
- Loss (last 10 episodes): {loss}
- Exploration Rate: {exploration_rate}
- Model Checkpoint: `{checkpoint_name}`

---

## 🧠 Behavior Observations
{behavior_notes}

---

## 🚀 Next Steps
{next_steps}

---

## 🛠️ User Tweaks
Comment below with any changes you’d like to see for the next run. Example:


[tweaks] episodes = 50 learning_rate = 0.0005 notes = Try using a different gym environment: "MountainCar-v0" [/tweaks]
"""

# Start the loop to poll for updates
while True:
    # Fetch the latest comments from the issue
    comments = fetch_github_issue_comments()

    stop_training = False
    tweaks = {}

    # Loop through the comments to find any that contain tweaks or a stop signal
    for comment in comments:
        if comment['user']['login'] != ALLOWED_USER:
            continue  # Skip comments from other users

        if "Stop training" in comment['body']:
            stop_training = True
            print("Received stop signal, terminating training.")
            break
        else:
            # Parse for tweaks
            comment_tweaks = parse_tweaks_from_comment(comment['body'])
            if comment_tweaks:
                tweaks.update(comment_tweaks)

    if stop_training:
        break

    # Apply the tweaks to the model (if any)
    episodes = int(tweaks.get("episodes", 10))
    learning_rate = float(tweaks.get("learning_rate", 0.00025))
    
    # Select an environment
    env = gym.make("CartPole-v1")
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=learning_rate)

    # Train the model
    model.learn(total_timesteps=episodes * 1000)  # Adjust training steps based on the number of episodes

    # Save the model
    checkpoint_name = f"ppo_cartpole_{episodes}episodes"
    model.save(checkpoint_name)

    # Notify via GitHub Issues
    issue_title = f"Training Complete: CartPole-v1 - {episodes} Episodes"
    issue_body = format_github_issue(
        env_name="CartPole-v1",
        episode_count=episodes,
        avg_reward=165.2,  # This can be updated dynamically
        max_reward=200,  # This can be updated dynamically
        training_time="12m 43s",  # This can be updated dynamically
        avg_length=189,  # This can be updated dynamically
        loss=0.132,  # This can be updated dynamically
        exploration_rate=0.05,  # This can be updated dynamically
        checkpoint_name=checkpoint_name,
        behavior_notes="Stable balance achieved after 3 episodes. Occasional early failure around step 90.",
        next_steps="Increase training to 20 episodes and test reward penalty for jerky movement."
    )

    # Update the existing issue with the results
    status, response = update_github_issue(ISSUE_NUMBER, issue_body)

    if status == 200:
        print(f"Issue updated: {response.get('html_url')}")
    else:
        print("Failed to update issue.")
        print("GitHub API response:", response)

    # Sleep for a while before checking again
    time.sleep(POLLING_INTERVAL)
