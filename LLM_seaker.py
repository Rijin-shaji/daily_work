import os
from groq import Groq
from resumer_uploader import retrieve_resume_matches


# CONFIG
LLM_MODEL_NAME = "llama-3.3-70b-versatile"

# Check for API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable not set")

client = Groq(api_key=api_key)


# LLM ANALYSIS FOR TOP MATCH
def analyze_top_match(top_match):

    md = top_match.get("metadata", {})
    job_desc = top_match.get("text", "")

    prompt = f"""Analyze this job posting and provide a concise summary:

Job Title: {md.get('job_title', 'Unknown')}
Company: {md.get('company', 'Unknown')}
Location: {md.get('location', 'Unknown')}

Job Description:
{job_desc}

Provide:
1. A brief 2-3 sentence description of the role
2. Required experience (years and type)
3. Key skills needed

Keep it concise and professional."""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a job analyst. Provide clear, concise summaries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=LLM_MODEL_NAME,
            temperature=0.5,
            max_tokens=300
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Error calling LLM: {str(e)}"


# MAIN PIPELINE
def main():
    print("=" * 60)
    print("AI-Powered Resume-Job Matcher")
    print("=" * 60)

    # Get resume matches
    matches = retrieve_resume_matches()

    if not matches:
        print("\nNo matches found.")
        return

    # Get top 3-4 matches
    top_matches = matches[:4]

    print("\n" + "=" * 60)
    print("TOP MATCHED JOBS")
    print("=" * 60)


    for i, match in enumerate(top_matches, 1):
        md = match.get("metadata", {})

        print(f"\n{'=' * 60}")
        print(f"MATCH #{i}")
        print(f"{'=' * 60}\n")

        print(f"Job Title: {md.get('job_title', 'Unknown')}")
        print(f"Company: {md.get('company', 'Unknown')}")
        print(f"Location: {md.get('location', 'Unknown')}")
        print(f"Match Score: {match['similarity_score']:.4f}")

        print("\nJOB ANALYSIS:")
        print("-" * 60)

        analysis = analyze_top_match(match)
        print(analysis)

    print("\n" + "=" * 60)


# RUN
if __name__ == "__main__":
    main()