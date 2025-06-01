from agno.agent import Agent
from agno.models.google import Gemini
from textwrap import dedent
from pydantic import BaseModel, Field
import json


# Re-using the Transcription model as a generic string wrapper for HTML output
class HtmlContent(BaseModel):
    content: str = Field(
        ..., description="The generated HTML content for the microsite."
    )


microsite_builder_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-001", response_modalities=["text"]),
    description=dedent(
        """\
                Generates a personalized, interactive HTML microsite from demo call data.
                It combines structured extracted information with raw transcription details
                to create a visually appealing and informative recap page for prospects."""
    ),
    instructions=dedent(
        f"""\
                You are an expert web developer specializing in creating concise, engaging, and personalized microsites for product demo recaps.

                **Your Task:**
                Generate a complete, single-page HTML document for a product demo recap microsite.
                The HTML should be fully self-contained (no external CSS files, use Tailwind CSS CDN).
                It must be responsive, visually appealing, and **have clean, minimal formatting (avoid excessive newlines or unnecessary whitespace)**.

                **Inputs:**
                -   `extracted_info_json`: A JSON string containing structured data about the demo (product, prospect, features, pain points, next steps, etc.).
                -   `raw_transcription`: The full, verbatim transcription of the demo call, including timestamps and speaker identification. This is crucial for creating "Watch this moment" links.

                **Microsite Structure & Content Requirements:**

                1.  **HTML Boilerplate:** Include `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`.
                2.  **Meta Tags:** Include `viewport` for responsiveness.
                3.  **Title:** Use the `product_name` and `prospect_company` for the page title.
                4.  **Tailwind CSS:** Load from CDN: `<script src="https://cdn.tailwindcss.com"></script>`.
                5.  **Font:** Load Inter font via Google Fonts CDN in `<head>` and apply `font-family: 'Inter', sans-serif;` via a `<style>` block.
                6.  **Overall Styling:**
                    * Use a clean, modern design with `bg-gray-100` for the body.
                    * Content should be in a white card (`bg-white rounded-lg shadow-md`) with good padding.
                    * Apply rounded corners to elements.
                    * Ensure appropriate spacing (padding, margin classes).
                    * Center text for headers and CTAs.
                7.  **Header Section:**
                    * Prominent `<h1>` for the recap title (e.g., "Recap for [Prospect Company] - [Product Name] Demo").
                    * `<p>` tag for "Presented by [Sales Rep's Name] ([Product Name])".
                8.  **Summary Section (`<section>`):**
                    * `<h2>` title: "Key Summary Points".
                    * Unordered list (`<ul>`) with `list-disc list-inside` for `summary_points`.
                9.  **Pain Points Discussed Section (`<section>`):**
                    * `<h2>` title: "Pain Points Discussed".
                    * Unordered list (`<ul>`) with `list-disc list-inside` for `pain_points_discussed`.
                10. **Features Demonstrated Section (`<section>`):**
                    * `<h2>` title: "Features Demonstrated".
                    * If `features_demonstrated` is empty, use a `<p>` tag: "No features were explicitly demonstrated in this call."
                    * If features exist, use an unordered list (`<ul>`). For each feature:
                        * Display `name`.
                        * Create a button/link `<a>` with Tailwind classes (e.g., `inline-block bg-blue-500 hover:bg-blue-600 text-white text-xs font-semibold py-1 px-2 rounded ml-2`) labeled "Watch this moment".
                        * The `href` for this link MUST be `{{demo_recording_url}}#t={{timestamp_start_in_seconds}}`. Convert `HH:MM:SS` to total seconds for the hash (e.g., 00:00:30 becomes 30).
                11. **Next Steps Section (`<section>`):**
                    * `<h2>` title: "Next Steps".
                    * Unordered list (`<ul>`) with `list-disc list-inside` for `next_steps`.
                12. **Call to Action (CTA) (`<div>`):**
                    * Centered `<div>`.
                    * A prominent button `<a>` with Tailwind classes (e.g., `bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded`) labeled "Schedule a Follow-Up". This can point to a placeholder link (`#`).
                13. **Strict HTML Output:** Output ONLY the complete HTML document. Do not include any other text, preambles, explanations, or conversational filler outside the HTML. **Ensure minimal newlines and whitespace within the HTML for a compact output.**
                """
    ),
    response_model=HtmlContent,  # Agent will return an HtmlContent object containing the raw HTML string
)
