import chainlit as cl
from langchain_aws import ChatBedrockConverse
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from typing import cast
from langchain.schema.runnable import RunnableConfig, Runnable

import aioboto3
import json

from dotenv import load_dotenv

load_dotenv()

# @cl.password_auth_callback
# def auth_callback(username: str, password: str):
#     # Fetch the user matching username from your database
#     # and compare the hashed password with the value stored in the database
#     if (username, password) == ("admin", "admin"):
#         return cl.User(
#             identifier="admin", metadata={"role": "admin", "provider": "credentials"}
#         )
#     else:
#         return None

@cl.on_chat_start
async def on_chat_start():
    llm = ChatBedrockConverse(
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        region_name="us-west-2",
        temperature=0,
        max_tokens=None
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "IDK IA wish you a good day."),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | llm | StrOutputParser()
    cl.user_session.set("runnable", runnable)

    await cl.Message(content="You'r connected to Chainlit!").send()

@cl.on_message
async def on_message(message: cl.Message):
    # Check if the message contains any attached elements
    if message.elements:
        # Processing images exclusively
        images = [file for file in message.elements if "image" in file.mime]
        if images:
            # Add logic to handle images
            await cl.Message(content=f"Received {len(images)} image(s)").send()
        else:
            # Add logic for a file traitment
            await cl.Message(content="Received a file").send()
    else:
        # Text message processing
        runnable = cast(Runnable, cl.user_session.get("runnable"))
        msg = cl.Message(content="", elements=message.elements)
        
        async for chunk in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            await msg.stream_token(chunk)

        await msg.send()

async def call_aws_lambda(content):
    async with aioboto3.client('lambda', region_name='us-west-2') as lambda_client:
        response = await lambda_client.invoke(
            FunctionName='LambdaF',
            InvocationType='RequestResponse',
            Payload=json.dumps({"content": content})
        )
        response_payload = json.loads(await response['Payload'].read().decode('utf-8'))
        return response_payload.get('response', 'No response received from AWS Lambda.')
