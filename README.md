# About the Project

My name's Aidan Andrews, and I solo-built **Animind**, a project I genuinely believe can change how people learn.

## Inspiration

Sometimes in class, even though the teacher's explaining, it just doesn't click. Everyone says "I'm a visual learner" and we all end up on YouTube. But YouTube isn't made for our class—it’s luck if 3Blue1Brown or OrganicChemistryTutor have a video on what we need. That's why I built **Animind**. A platform where teachers and students can create beautiful, custom Manim videos that actually match their coursework. Visual, intuitive, and specific—so no one gets left confused again.

## What it Does

**Animind** generates Manim-based educational animations that help explain concepts visually. Topics, ideas, entire lessons—brought to life with beautiful animations.

## How I Built It

At the core of \*\*Animind\*\* is a modular multi-agent system, fully powered by Google's AI ecosystem. Everything runs through \*\*FastAPI\*\*, with the AI heavy lifting handled by Gemini models accessed via \*\*OpenRouter\*\* and \*\*Vertex AI\*\*.



\### Agents Overview



\- \*\*Manim Agent\*\*

&#x20; \- Built using \*\*Google ADK\*\* and the \*\*Plan-ReAct\*\* framework.

&#x20; \- Takes a narration prompt.

&#x20; \- Researches using a \*\*RAG tool\*\* (powered by \*\*Vertex AI\*\*).

&#x20; \- Generates Python/Manim code.

&#x20; \- Runs and validates animations to ensure alignment with the narration.



\- \*\*Video Agent\*\*

&#x20; \- A \*\*SequentialAgent\*\* made up of three sub-agents:

&#x20;   1\. \*\*Plan Generator\*\*: Lays out the scene-by-scene plan.

&#x20;   2\. \*\*Scene Generator\*\*: Generates animation, voiceover, and media merging.

&#x20;   3\. \*\*Final Assembler\*\*: Stitches everything into a full video.



\- \*\*RAG Agent\*\*

&#x20; \- Lightweight but critical.

&#x20; \- Retrieves from a custom corpus of Manim documentation, example code, and community resources.

&#x20; \- Prevents hallucination and ensures factual accuracy.



\### System Design



\- Every agent runs inside an execution pipeline with built-in retries, validation, and error-recovery—especially for code generation and Manim rendering.

\- Frontend is intentionally kept lightweight (\*\*React / Vite / TypeScript\*\*).

\- Frontend only streams outputs and statuses from the backend—no direct LLM calls.

\- All components are modular: agents are interchangeable, and models are swappable just by flipping environment variables.Accomplishments I'm Proud Of

Built both the frontend and backend from scratch. Pulled an insane 12-hour work session, crashed for 4 hours, and then pushed another 15 straight. ([Proof here](https://www.youtube.com/@aidanandrews/streams))

Outside of my startup, this is easily the hardest I've worked in 36 hours. Hit a ton of brick walls with ADK but never quit. Got an MVP across the finish line—and honestly, I’m hyped about it.

## What I Learned

This was basically a crash course in Google's full AI ecosystem. I used Google for *everything* — Gemini LLM, Google ADK, TTS, Vertex, Cloud APIs. Learned a ton about how to build apps directly on top of Google's infrastructure.

Frontend? Agents? RAG? Already had lots of experience there. But now, I’m way sharper at navigating all of Google's cutting-edge AI tools.

## What's Next for Animind

I'm turning **Animind** into a full open-source platform—anyone will be able to use it to level up their learning or teaching. Once I get longer, richer, and even more accurate video generation—this thing’s going to be unstoppable.

