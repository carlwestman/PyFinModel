import os
import asyncio
from typing import List, Optional
from ..core.company import Company
from ..core.financial_item import FinancialItem
from ..agent.agent import AnalystAgentContext, run_analyst_agent

class AgenticForecast:
    def __init__(self, assistant_id: str):
        """
        Initialize the AgenticForecast with OpenAI API key and assistant ID.

        Args:
            open_ai_api_key (str): OpenAI API key.
            assistant_id (str): Assistant ID for the agent.
        """
        self.assistant_id = assistant_id
        self.transcripts: List[str] = []
        self.company: Optional[Company] = None
        self.target_item: Optional[str] = None

    def add_transcript(self, transcript_file: str) -> None:
        """
        Add a transcript file to the list of transcripts.

        Args:
            transcript_file (str): Path to the transcript file.
        """
        with open(transcript_file, "r") as file:
            self.transcripts.append(file.read())

    def set_company(self, company: Company) -> None:
        """
        Set the company object.

        Args:
            company (Company): The company object.
        """
        self.company = company

    def set_target_item(self, target_item: str) -> None:
        """
        Set the target financial item for forecasting.

        Args:
            target_item (str): The name of the target financial item.
        """
        self.target_item = target_item

    async def run(self) -> None:
        """
        Run the agent to generate forecasts and add them to the forecasted values of the target item.

        Raises:
            ValueError: If the company, target item, or transcripts are not set.
        """
        if not self.company:
            raise ValueError("Company object is not set.")
        if not self.target_item:
            raise ValueError("Target item is not set.")
        if not self.transcripts:
            raise ValueError("No transcripts have been added.")

        # Prepare the context for the agent
        context: AnalystAgentContext = {
            "company": self.company.to_dict(),
            "transcripts": self.transcripts,
            "target_item": self.target_item,
        }

        # Run the agent
        output = await run_analyst_agent(context, self.assistant_id)

        # Extract the "next_4_qs" forecast and add it to the target item's forecasted values
        target_item = self._find_target_item()
        if not target_item:
            raise ValueError(f"Target item '{self.target_item}' not found in the company's financial statements.")

        for period, value in output["next_4_qs"].items():
            target_item.add_forecasted(period, value)

    def _find_target_item(self) -> Optional[FinancialItem]:
        """
        Find the target financial item in the company's financial statements.

        Returns:
            FinancialItem or None: The target financial item if found, otherwise None.
        """
        return (
            self.company.income_statement.get_item(self.target_item)
            or self.company.balance_sheet.get_item(self.target_item)
            or self.company.cash_flow_statement.get_item(self.target_item)
            or self.company.kpi_statement.get_item(self.target_item)
            or self.company.other_financials_statement.get_item(self.target_item)
        )