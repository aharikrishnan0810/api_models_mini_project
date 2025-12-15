import google.generativeai as genai
import time
import os

# 🔑 Configure your Gemini API key
genai.configure(api_key="replace with your real API key")  # replace with your real API key
 # Replace with your real API key

# ✅ Fixed model (use the latest stable one)
MODEL_NAME = "models/gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# 🧾 Check remaining quota
def check_quota():
    try:
        quota = genai.get_quota_status()
        print("\n💡 Remaining Quota Status:")
        for metric, data in quota.items():
            print(f"- {metric}: {data['remaining']} remaining, limit {data['limit']}")
    except Exception as e:
        print(f"⚠️ Could not fetch quota: {e}")

# 🧠 Prompt generation logic
def generate_prompt(query, mode="zero-shot"):
    if mode == "zero-shot":
        return query
    elif mode == "one-shot":
        return f"""
        Example:
        Q: What is AI?
        A: AI is the simulation of human intelligence in machines.

        Q: {query}
        A:
        """
    elif mode == "few-shot":
        return f"""
        Example 1:
        Input: What is supervised learning?
        Output: Learning using labeled data.

        Example 2:
        Input: What is unsupervised learning?
        Output: Learning without labels.

        Now explain: {query}
        """
    elif mode == "chain-of-thought":
        return f"Explain step-by-step reasoning for this: {query}"
    else:
        return query

# ⚙️ Get response + token tracking
def get_response(prompt):
    start = time.time()
    response = model.generate_content(prompt)
    end = time.time()

    prompt_tokens = 0
    response_tokens = 0
    total_tokens = 0

    try:
        usage = response.usage_metadata
        prompt_tokens = usage.prompt_token_count
        response_tokens = usage.candidates_token_count
        total_tokens = usage.total_token_count
    except Exception:
        print("⚠️ Token usage info not available for this model version.\n")

    with open("token_usage_log.txt", "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | Prompt: {prompt_tokens} | Response: {response_tokens} | Total: {total_tokens}\n")

    return response.text, round(end - start, 2), prompt_tokens, response_tokens, total_tokens

# 🎯 Main function
def main():
    print("🤖 Gemini Agent with Prompting Logic + Token Tracker")
    print("----------------------------------------------------")

    # ⚡ Check quota before anything
    check_quota()

    print("\n1. Zero-shot prompting")
    print("2. One-shot prompting")
    print("3. Few-shot prompting")
    print("4. Chain-of-thought prompting")

    choice = input("Enter your choice (1-4): ").strip()
    modes = {"1": "zero-shot", "2": "one-shot", "3": "few-shot", "4": "chain-of-thought"}
    
    if choice not in modes:
        print("❌ Invalid choice.")
        return

    query = input("\nEnter your question: ").strip()
    prompt = generate_prompt(query, modes[choice])

    print("\nGenerating response...\n")
    response, duration, prompt_tokens, response_tokens, total_tokens = get_response(prompt)

    print(f"🧩 Prompt Mode: {modes[choice]}")
    print(f"⏱️ Response Time: {duration}s")
    print(f"🔢 Tokens → Prompt: {prompt_tokens}, Response: {response_tokens}, Total: {total_tokens}\n")
    print("💬 Model Response:\n")
    print(response)

    if os.path.exists("token_usage_log.txt"):
        with open("token_usage_log.txt", "r") as f:
            total_used = sum(int(line.strip().split("|")[-1].split(":")[-1]) for line in f if "Total" in line)
        print(f"\n📈 Total Tokens Used So Far (All Runs): {total_used}")

if __name__ == "__main__":
    main()
