# Use this outside of the container, making REST calls to the running seldon container
import asyncio
import httpx
from queries import queries
import time

IN_FLIGHT=24
# vllm via https://github.com/kyuz0/amd-r9700-vllm-toolboxes
URL = 'http://127.0.0.1:8001/v1/chat/completions'






#        {"role": "system", "content": """You are a classifier used to determine if a word phrase is an employment skill or role that will be replaced by AI or not.  If it will be replaced by AI respond 1 . If it will not be replaced or is not related to an employment skill or role, respond 0.
#Example: 'executive assistant' respond 1
#Example: 'metal fabricator' respond 0
#Example: 'blue sky' respond 0"""},

async def get_decision(client, phrase):
    PAYLOAD = {
    "messages": [
        {"role": "system", "content": """You are a classifier used to determine if a word phrase is an employment skill or role that will be replaced by AI or not.  If it will be replaced by AI respond 'YES' . If it will not be replaced or is not related to an employment skill or role, respond 'NO'.
Example: 'executive assistant' respond 'YES'
Example: 'metal fabricator' respond 'NO'
Example: 'blue sky' respond 'NO'"""},
        {"role": "user", "content": phrase }
    ],
    "temperature": 0,
    "stream": False, # Set to True for streaming responses
    "max_tokens": 100
    }
    response = await client.post(url=URL, json=PAYLOAD)
    if response.status_code == 200:
        print('.',end='', flush=True)
        reesp = response.json()
        #print(reesp)
        #exit()
        return (reesp["usage"],reesp["choices"][0]["message"]["content"])
    else:
        print('X',end='', flush=True)
        return 'XXX'


  

async def bound_fetch(sem, client,phrase):
    async with sem:
        return await get_decision(client, phrase)


async def main():
    sem = asyncio.Semaphore(IN_FLIGHT)
    limits = httpx.Limits(max_keepalive_connections=IN_FLIGHT, max_connections=IN_FLIGHT, keepalive_expiry=10)
    client = httpx.AsyncClient(limits=limits, verify=False)
    results = []
    start_time = time.perf_counter()
    tokens = 0
    pp = 0
    iterations = 2
    tests = queries * iterations
#{'id': 'chatcmpl-88def5202e74d7a0', 'object': 'chat.completion', 'created': 1768775512, 'model': 'openai/gpt-oss-20b', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': None, 'refusal': None, 'annotations': None, 'audio': None, 'function_call': None, 'tool_calls': [], 'reasoning': 'We need', 'reasoning_content': 'We need'}, 'logprobs': None, 'finish_reason: 'length', 'stop_reason': None, 'token_ids': None}], 'service_tier': None, 'system_fingerprint': None, 'usage': {'prompt_tokens': 167, 'total_tokens': 172, 'completion_tokens': 5, 'prompt_tokens_details': None}, 'prompt_logprobs': None, 'prompt_token_ids': None, 'kv_transfer_params': None}

    for i in range(1):
        results = await asyncio.gather(*[asyncio.ensure_future(bound_fetch(sem,client,test)) for test in tests], return_exceptions=True)
        for item in results:
            tokens += item[0]['completion_tokens']
            pp += item[0]['prompt_tokens']
        #print(results)
    end_time = time.perf_counter()
    duration = end_time-start_time
    print('\n\n')
    print(f"{len(queries)*iterations} decisions made in {round(duration,2)} seconds.")
    print(f"{(len(queries)*iterations)/duration} Decisions per second")
    print(f"{tokens/duration} Tokens generated per second")
    print(f"{pp/duration} Tokens prompt processed per second")
    for item in results:
        print(item[1],end='', flush=True)
#wrong    print(f"{pp/pp_ms} server pp/s")
#wrong    print(f"{tokens/tokens_ms} server tg/s")


if __name__=='__main__':
    asyncio.run(main())
