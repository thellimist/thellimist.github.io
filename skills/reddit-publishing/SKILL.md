---
name: reddit-publishing
description: Research subreddits, verify rules, and draft a Reddit post for a blog article.
---

# Reddit Publishing Skill

Research relevant subreddits, verify their rules allow the content, and draft a Reddit post.

## Tools Required

- **browser** (OpenClaw browser tool) — for reading subreddit rules and drafting posts
- **web_fetch** — for reading subreddit rules and sidebar via JSON API

## Format Rules

### Post Type
- **Link post** if the subreddit allows it (title + blog URL)
- **Text post** if the subreddit requires it (write a summary, link at the bottom)
- Check subreddit rules — some require text posts only, some ban self-promotion entirely

### Title
- Match the subreddit's style. Read recent top posts to calibrate.
- No clickbait. Reddit punishes hype harder than HN.
- Add flair tag if required (check rules).

### Content
- If text post: write a genuine summary with key takeaways, not just "check out my blog"
- Add value first, link second
- Never use marketing language

### Tone
- Reddit-native. Casual, direct, not corporate.
- Write like you're sharing with peers, not promoting.

## Step 1: Research Subreddits

Find relevant subreddits and check if the post is allowed.

### 1a. Generate Search Keywords

Read the blog post and extract 4 different keyword angles that would map to different subreddit communities. Think about:
- The core topic (e.g. "ai agents")
- The technical angle (e.g. "LLM tool use")
- The industry/audience angle (e.g. "AI startups")
- A broader adjacent topic (e.g. "developer productivity AI")

### 1b. Search Subreddits

Run 4 searches with 10 results each to cast a wide net:

```bash
for QUERY in "ai+agents" "LLM+tool+use" "AI+startups" "developer+productivity+AI"; do
  echo "=== Query: $QUERY ==="
  curl -s "https://www.reddit.com/subreddits/search.json?q=$QUERY&limit=10" \
    -H "User-Agent: blog-research" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for sub in data['data']['children']:
    d = sub['data']
    print(f\"r/{d['display_name']} | {d['subscribers']} subs | {d['public_description'][:100]}\")
"
  echo ""
done
```

### 1c. Deduplicate and Rank

From the ~40 results, pick the top 5-8 unique subreddits based on:
- **Relevance:** Does the blog topic fit what the subreddit discusses?
- **Size:** Prefer 50k+ subscribers for reach, but niche subs (10k+) with high engagement are fine
- **Activity:** Check if recent posts get comments (dead subs aren't worth it)

### 1d. Check Rules for Each Candidate

For each candidate subreddit, check rules:

```bash
# Fetch subreddit rules
SUBREDDIT="MachineLearning"
curl -s "https://www.reddit.com/r/$SUBREDDIT/about/rules.json" \
  -H "User-Agent: blog-research" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for rule in data.get('rules', []):
    print(f\"- {rule['short_name']}: {rule.get('description', '')[:200]}\")
"

# Also check sidebar for additional rules
curl -s "https://www.reddit.com/r/$SUBREDDIT/about.json" \
  -H "User-Agent: blog-research" | python3 -c "
import json, sys
data = json.load(sys.stdin)['data']
print('Sidebar rules:')
print(data.get('public_description', ''))
print('---')
print(data.get('description', '')[:2000])
"
```

### Rule Checks (mandatory for each subreddit)

Verify ALL of the following before drafting:

- [ ] **Self-promotion rules:** Many subreddits ban or limit self-promotion. Check ratio rules (e.g. "90% of posts must not be your own content").
- [ ] **AI-generated content rules:** Some subreddits ban AI-generated images or AI-written content. Check explicitly.
- [ ] **Link post vs text post:** Some require text posts only.
- [ ] **Flair requirements:** Some require specific post flair.
- [ ] **Minimum karma/account age:** Some have minimum thresholds.
- [ ] **Posting format:** Some have strict title formats (e.g. "[D]" prefix for discussion in r/MachineLearning).

If a subreddit bans self-promotion or AI content, skip it. Don't try to sneak around rules.

## Step 2: Draft the Post

Save as `social/YYYY-MM-DD-slug/reddit.md` with metadata:

```markdown
# Reddit Draft

## Target Subreddits
- r/SubredditName — rules checked ✅, allows link posts, no AI image ban
- r/OtherSub — rules checked ✅, text post only, requires [D] flair

## Post for r/SubredditName
**Type:** link post
**Title:** [title here]
**URL:** [blog URL]

## Post for r/OtherSub
**Type:** text post
**Title:** [title here]
**Body:**
[summary text here]

[blog URL at the end]
```

## Step 3: Draft in Reddit (DO NOT PUBLISH)

Use the browser tool. Draft only — Kan reviews and publishes manually.

1. **Open Reddit:** `browser navigate` to `https://www.reddit.com/r/SUBREDDIT/submit` (use profile="openclaw", logged in as thellimist)
2. **Select post type:** Link or text based on subreddit rules
3. **Fill title and content**
4. **Add flair** if required
5. **DO NOT click Submit/Post** — leave as draft for Kan to review
6. **Take a screenshot** of the draft for review

## Checklist Before Drafting
- [ ] Subreddit rules fetched and reviewed
- [ ] Self-promotion policy allows this post
- [ ] AI-generated image policy checked (if post includes the blog header image)
- [ ] AI-written content policy checked
- [ ] Correct post type selected (link vs text)
- [ ] Title matches subreddit style and format requirements
- [ ] Flair set if required
- [ ] Draft saved — NOT published
