# AI Gave Birth to the 100X Engineer

> 8,471 commits. 48 repositories. 72 days. One engineer.

Peter Steinberger built OpenClaw, the fastest-growing open source project in GitHub history. 228,000 stars in under three months - 18x faster than Kubernetes. Then OpenAI hired him.

I reverse-engineered how he works. Not his opinions or philosophy. His systems and his output.

## Sharpening the axe

> Give me six hours to chop down a tree, and I will spend the first four sharpening the axe.
>
> — Abraham Lincoln

Peter spent a lot of time building tools. Not products. Tools that make his AI agents better at building products.

He's building a macOS app. Agents can't test UI. He built Peekaboo and AXorcist so agents can take screenshots, read UI elements, and test any macOS application.

He's building a Swift app. Build times are slow. He built Poltergeist - it watches for file changes and rebuilds in the background automatically.

Agents get stuck. No one course-corrects. He built Oracle - it sends your code to a different AI model for review. A fresh set of eyes that catches what the first model won't.

Agents can't reach the outside world. He built imsg for iMessage, wacli for WhatsApp, gogcli for Gmail, summarize for digesting any URL.

> I don't design codebases to be easy to navigate for me. I engineer them so agents can work in them efficiently.
>
> — Peter Steinberger

Every tool compounds into the next.

## The output

[IMAGE: table_output_comparison.png]

On any given day, Peter has agents running simultaneously across different repositories. Each agent works on a task for up to 2 hours. One refactors the OAuth module in mcporter while another writes tests for Peekaboo. Peter moves between them, reviewing output, adjusting prompts, queuing the next task.

This is what a single Sunday looks like:

[IMAGE: gantt_chart.png]

These aren't toy projects.

[IMAGE: table_projects.png]

## The team you build

A 10X engineer is about talent. Some people are just faster and think clearer.

A 100X engineer is about systems. Peter manages 5-10 AI agents at any given moment - each one capable of doing the work of a 10X engineer. He built the tools that make each agent effective, and the systems that let him run many of them at once.

In the AI age, every engineer can have their own team. The ones who build the best agent systems are on the path to 100X.
