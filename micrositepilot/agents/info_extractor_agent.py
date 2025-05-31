from agno.agent import Agent
from agno.models.google import Gemini
from textwrap import dedent
from pydantic import BaseModel, Field
from typing import List


# Define the nested model for individual features demonstrated
class FeatureDemonstrated(BaseModel):
    name: str = Field(..., description="The name of the product feature demonstrated.")
    timestamp_start: str = Field(
        ...,
        description="Start timestamp of the feature demonstration (e.g., '00:05:10').",
    )
    timestamp_end: str = Field(
        ...,
        description="End timestamp of the feature demonstration (e.g., '00:08:45').",
    )


# Define the main model for the entire demo summary
class DemoSummary(BaseModel):
    product_name: str = Field(
        ..., description="The name of the product or solution demonstrated."
    )
    prospect_company: str = Field(
        ..., description="The name of the prospective customer's company."
    )
    sales_rep: str = Field(
        ..., description="The name of the sales representative who conducted the demo."
    )
    summary_points: List[str] = Field(
        ..., description="A list of high-level summary points from the demo call."
    )
    pain_points_discussed: List[str] = Field(
        ...,
        description="A list of specific pain points or challenges discussed by the prospect.",
    )
    features_demonstrated: List[FeatureDemonstrated] = Field(
        ...,
        description="A list of specific features demonstrated, including their start and end timestamps.",
    )
    next_steps: List[str] = Field(
        ...,
        description="A list of agreed-upon next steps or action items after the demo.",
    )
    unanswered_questions: List[str] = Field(
        ...,
        description="A list of questions from the prospect that were not fully answered during the call.",
    )


info_extractor = Agent(
    model=Gemini(id="gemini-2.0-flash-001", response_modalities=["text"]),
    description=dedent(
        """\
                Extracts key information from product demo call transcriptions.
                Analyzes conversation context to identify product details, prospect pain points,
                demonstrated features with timestamps, and actionable next steps, structuring
                the output for microsite generation."""
    ),
    instructions=dedent(
        """\
                Given a timestamped product demo call transcription, extract the following information.
                Format your response strictly as a JSON object validated by the `DemoSummary` Pydantic model.

                **Extraction Rules:**
                1.  **Product Name:** Identify the primary product or solution discussed.
                2.  **Prospect Company:** Determine the name of the prospective customer's organization.
                3.  **Sales Rep:** Identify the name of the sales representative.
                4.  **Summary Points:** Provide 3-5 concise, high-level bullet points summarizing the entire demo.
                5.  **Pain Points Discussed:** List specific challenges or problems the prospect mentioned.
                6.  **Features Demonstrated:** For each feature explicitly shown or discussed in detail, provide its name and the precise start and end timestamps from the transcription. If a feature is mentioned but not demonstrated, do not include timestamps.
                7.  **Next Steps:** List any clear action items or agreed-upon follow-ups for either party.
                8.  **Unanswered Questions:** List any specific questions posed by the prospect that were not fully resolved during the call.
                9.  **Strict JSON Output:** Ensure the output is valid JSON and perfectly matches the structure defined by the `DemoSummary` model. Do not include any extra text or conversational filler outside the JSON.
                """
    ),
    response_model=DemoSummary,
)
