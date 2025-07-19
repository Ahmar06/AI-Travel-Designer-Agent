from agents import Agent,Runner,OpenAIChatCompletionsModel,AsyncOpenAI,function_tool
from agents.run import RunConfig
from dotenv import load_dotenv
import os
import asyncio
import chainlit as cl

load_dotenv()

async def main():
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    externalclient = AsyncOpenAI(
        api_key = GEMINI_API_KEY,
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    model = OpenAIChatCompletionsModel(
        model = "gemini-2.0-flash",
        openai_client = externalclient   
    )
    config = RunConfig(
        model_provider = externalclient,
        model = model,
        tracing_disabled = True
    )
    @function_tool
    async def suggest_hotel():
            """
            You Suggest hotels to user
            """
            suggest_hotels = [
                {"name": "Sunshine", "location": "Downtown", "price": "$120 per night"},
                {"name": "Ocean View Resort", "location": "Beachfront", "price": "$200 per night"},
                {"name": "Mountain Retreat", "location": "Hillside", "price": "$150 per night"},
            ]
            hotel_list = "\n".join([f"{hotel['name']} - {hotel['location']} - {hotel['price']}" for hotel in suggest_hotels])

            return f"Here are some hotel suggestions:\n{hotel_list}\nYou can book any of these hotels based on your preferences."

    # Define the agents
    destination_Agent = Agent(
        name = "Destination Agent",
        instructions = "You are a destination agent. You suggest the user to find the best destination for their travel based on their mood and interests then suggest them hotel for their stay,You have a tool for suggesting hotels",
        tools = [suggest_hotel],
        model = model,
    ) 
    @function_tool
    async def get_flights(location,destination,date):
        """
         Get flights data name,from,to,price.
        """
        flights = [
            # {f"flight_number": "AI202", "from": {location}, "to": {destination}, "price": "[300$]","date": {date}},
            {"flight_number": "BA303", "from": "[London]", "to": "[New York]", "price": "[500]","date": "[2023-10-02]"},
            {"flight_number": "CA404", "from": "[Tokyo]", "to": "[Sydney]", "price": "[700]","date": "[2023-10-03]"},
        ]
        return f"Your flight is booked successfully! Here are the details:{flights}"
    booking_agent = Agent(
        name = "Booking Agent", 
        instructions = "You are a booking agent You help user to book flights based on their preferences you have tool for booking flight",
        tools = [get_flights],
        model = model,
    )
    explore_agent  = Agent(
        name = "Explore Agent",
        instructions = "You are a explore agent You suggest user about foods and activities to do in the destination they are visiting",
        model = model,
    )
    agent = Agent(
        name = "Triage Agent",
        instructions = """you are a triage agent,You deligate the user's questions to the appropriate agent based on the topic. If the question is about explore, delegate to the Explore Agent. If it is about booking, delegate to the Booking Agent. If it is about destination, delegate to the Destination Agent,if answer is not related to any agent polietly decline to answer.""",
        handoffs = [
            destination_Agent,
            booking_agent,
            explore_agent,
        ],
        model = model,
    )
    

    @cl.on_chat_start
    async def on_chat_start():
        cl.user_session.set("history",[])
    
    @cl.on_message
    async def on_message(message: cl.Message):
        history = cl.user_session.get("history",[])
        history.append({"role":"user","content":message.content})
        result = await Runner.run(
            starting_agent = agent,
            input = history,
            run_config = config
        )
        history.append({"role":"assistant","content":result.final_output})
        await cl.Message(result.final_output).send()
        # print(history)
        print(result)

asyncio.run(main())
