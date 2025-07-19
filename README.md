from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
from agents.run import RunConfig

# Mock tool: get_flights
def get_flights(destination, dates):
    # Mocked flight data
    return [
        {"flight": "AI101", "from": "NYC", "to": destination, "date": dates[0], "price": 500},
        {"flight": "BA202", "from": "NYC", "to": destination, "date": dates[0], "price": 550},
    ]

# Mock tool: suggest_hotels
def suggest_hotels(destination, preferences=None):
    # Mocked hotel data
    return [
        {"hotel": "Grand Plaza", "location": destination, "stars": 5, "price_per_night": 200},
        {"hotel": "Budget Inn", "location": destination, "stars": 3, "price_per_night": 80},
    ]

# Tool wrappers for agent SDK
class TravelInfoGenerator:
    def get_flights(self, destination, dates):
        return get_flights(destination, dates)

class HotelPicker:
    def suggest_hotels(self, destination, preferences=None):
        return suggest_hotels(destination, preferences)

# Specialized Agents
destination_agent = Agent(
    name="DestinationAgent",
    instructions="Suggest destinations based on user's mood or interests.",
    tools=[TravelInfoGenerator()],
)

booking_agent = Agent(
    name="BookingAgent",
    instructions="Simulate booking flights and hotels for the user.",
    tools=[TravelInfoGenerator(), HotelPicker()],
)

explore_agent = Agent(
    name="ExploreAgent",
    instructions="Suggest local attractions and food at the destination.",
)

# Triage agent to coordinate handoffs
triage_agent = Agent(
    name="TravelTriageAgent",
    instructions=(
        "You are a travel planner. "
        "If the user wants destination suggestions, hand off to DestinationAgent. "
        "If the user wants to book travel, hand off to BookingAgent. "
        "If the user wants to explore attractions or food, hand off to ExploreAgent. "
        "If the request doesn't fit, politely decline."
    ),
    handoffs=[destination_agent, booking_agent, explore_agent],
)

# Runner setup
def plan_travel_experience(user_input, dates, preferences=None):
    # This function simulates a full travel experience
    runner = Runner(
        agent=triage_agent,
        config=RunConfig(
            model_provider=None,  # Set up as needed
            model=None,           # Set up as needed
            tracing_disabled=True
        )
    )
    # Simulate the agent flow
    result = runner.run(
        input=user_input,
        
    return result

# Example usage (would be called from main or an async context)
if __name__ == "__main__":
    # Example: user wants a relaxing beach vacation
    user_input = "I want a relaxing beach vacation in July. Can you help me plan?"
    dates = ["2024-07-10", "2024-07-20"]
    preferences = {"mood": "relaxing", "interests": ["beach", "spa"]}
    experience = plan_travel_experience(user_input, dates, preferences)
    print(experience)
