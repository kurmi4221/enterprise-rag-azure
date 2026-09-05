from typing import Any, Optional

from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient

from deepeval.models.base_model import DeepEvalBaseLLM

from backend.app.core.config import settings


class AzureDeepEvalModel(DeepEvalBaseLLM):
    """
    DeepEval model adapter using Microsoft Foundry.

    Authentication:
        Azure CLI / Microsoft Entra ID

    Endpoint:
        Microsoft Foundry project endpoint

    Model:
        Azure AI Foundry deployment configured in settings.chat_deployment_name
    """

    def __init__(
        self,
        model: Optional[str] = None,
    ):
        self.model_name = model or settings.chat_deployment_name

        # ---------------------------------------------------------
        # Azure authentication
        # ---------------------------------------------------------
        self.credential = AzureCliCredential(
            process_timeout=60
        )

        # ---------------------------------------------------------
        # Microsoft Foundry project client
        # ---------------------------------------------------------
        self.project_client = AIProjectClient(
            endpoint=settings.azure_ai_project_endpoint,
            credential=self.credential,
        )

        # ---------------------------------------------------------
        # Authenticated OpenAI-compatible client
        #
        # AIProjectClient handles:
        #   - project endpoint
        #   - bearer token provider
        #   - OpenAI-compatible base URL
        #
        # The SDK appends /openai/v1 to the project endpoint.
        # ---------------------------------------------------------
        self.client = self.project_client.get_openai_client()

        # DeepEval may call the async method.
        #
        # We intentionally do NOT use:
        #
        #     AsyncAzureOpenAI(...)
        #
        # here because AIProjectClient.get_openai_client()
        # returns the authenticated synchronous OpenAI client.
        self.async_client = None

    # ============================================================
    # DeepEval model interface
    # ============================================================

    def load_model(self):
        return self.client

    # ============================================================
    # Synchronous generation
    # ============================================================

    def generate(
        self,
        prompt: str,
        schema: Optional[Any] = None,
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content or ""

    # ============================================================
    # Asynchronous generation
    # ============================================================

    async def a_generate(
        self,
        prompt: str,
        schema: Optional[Any] = None,
    ) -> str:
        """
        DeepEval's async metric execution.

        Since AIProjectClient.get_openai_client() gives us a
        synchronous OpenAI client, execute the synchronous call
        in a worker thread.

        This avoids the previous error:

            TypeError:
            object ChatCompletion can't be used in 'await' expression
        """

        import asyncio

        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content or ""

    # ============================================================
    # DeepEval metadata
    # ============================================================

    def get_model_name(self) -> str:
        return self.model_name