import os
import gym
import minerl
from stable_baselines3 import PPO
import requests
import time

# GitHub repo details
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "nerddotdad"
REPO_NAME = "ai-gamer"
ISSUE_NUMBER = 1  # Use the issue number you want to update (e.g., issue #1)
GITHUB_USERNAME = "nerddotdad"  # Your GitHub username, only respond to your comments

# Configurations for the game and training
config = {
    "env_name": "MineRLNavigateDense-v0",  # A MineRL environment
    "total_timesteps": 100000,  # Adjust based on how long you want to train
    "checkpoint_name": "ppo_minerl",
    # other params...
}

# Function to get the existing issue
def get_github_issue():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{ISSUE_NUMBER}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    return response.status_code, response.json()

# Function to get the comments on the issue
def get_github_comments():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{ISSUE_NUMBER}/comments"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    return response.status_code, response.json()

# Function to update the existing issue
def update_github_issue(issue_number, title, body):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"title": title, "body": body}
    response = requests.patch(url, json=data, headers=headers)
    return response.status_code, response.json()

# Format the GitHub issue content
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

# Create the environment and model
env = gym.make(config["env_name"])
model = PPO("MlpPolicy", env, verbose=1)
model.policy.to("cuda")  # Moves the model to the GPU

# Train the model
print("Training started...")
start_time = time.time()
model.learn(total_timesteps=config["total_timesteps"])
training_time = time.time() - start_time

# Save the model
model.save(config["checkpoint_name"])
print(f"Model saved as {config['checkpoint_name']}")

# Notify via GitHub Issues
episode_count = 10  # Update this value as per your requirements
avg_reward = 50  # Example value, you can calculate it
max_reward = 100  # Example value, you can calculate it
avg_length = 200  # Example value, you can calculate it
loss = 0.1  # Example loss, you can calculate it
exploration_rate = 0.05  # Example value
behavior_notes = "The AI is learning to navigate the environment."
next_steps = "Train for more episodes to increase stability and maximize reward."

issue_title = f"Training Complete: {config['env_name']}"

issue_body = format_github_issue(
    env_name=config["env_name"],
    episode_count=episode_count,
    avg_reward=avg_reward,
    max_reward=max_reward,
    training_time=str(int(training_time)) + " seconds",
    avg_length=avg_length,
    loss=loss,
    exploration_rate=exploration_rate,
    checkpoint_name=config["checkpoint_name"],
    behavior_notes=behavior_notes,
    next_steps=next_steps
)

# Get the existing issue and update it
status, response = get_github_issue()

if status == 200:
    print("Found existing issue. Checking comments...")
    comment_status, comments = get_github_comments()
    
    if comment_status == 200:
        # Look through comments to check if it's your comment
        for comment in comments:
            if comment["user"]["login"] == GITHUB_USERNAME:
                print("Found your comment, updating issue...")
                update_status, update_response = update_github_issue(ISSUE_NUMBER, issue_title, issue_body)
                
                if update_status == 200:
                    print(f"Issue updated: {update_response.get('html_url')}")
                else:
                    print("Failed to update issue.")
                    print("GitHub API response:", update_response)
                break
        else:
            print("No comments from you found. Waiting for your comment to proceed.")
    else:
        print("Failed to fetch comments.")
        print("GitHub API response:", comments)
else:
    print("Issue not found. Please ensure the issue number is correct.")
    print("GitHub API response:", response)

# Test the trained model
obs = env.reset()
done = False
while not done:
    action, _states = model.predict(obs)
    obs, reward, done, info = env.step(action)
    env.render()  # Render the environment to see the game

env.close()  # Make sure to close the environment when done
