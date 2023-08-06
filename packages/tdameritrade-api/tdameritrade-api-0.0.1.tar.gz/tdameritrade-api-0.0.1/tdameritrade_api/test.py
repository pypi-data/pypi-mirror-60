import asyncio
import aiohttp

from auth import Auth
from api import AmeritradeAPI
from token_manager import TokenManager
from helpers import Ameritrade


async def main():
    async with aiohttp.ClientSession() as session:
        token_manager = TokenManager(consumer_key="ROTH_TRADER2@AMER.OAUTHAP")
        await token_manager.fetch_access_token()

        auth = Auth(session, "https://api.tdameritrade.com/v1", token_manager)

        api = AmeritradeAPI(auth)

        amtd = Ameritrade(api)

        try:
            print(await api.async_get_accounts("789090218"))
            # print(await api.async_get_quote("SPMD"))
            # print(await api.async_get_market_hours("EQUITY"))
            # print(await amtd.async_is_market_open())
            # 782991644,789090218
            # print(await api.async_place_order(10.00, "BUY", 5, "SPMD", "789090218"))
        except Exception as e:
            print(e)

        # print(accounts)

        # lights = await api.async_get_lights()

        # Print light states
        # for light in lights:
        #    print(f"The light {light.name} is {light.is_on}")

        # Control a light.
        # light = lights[0]
        # await light.async_control(not light.is_on)


try:
    asyncio.run(main())
except RuntimeError:
    print("done")
