# Best Buy API application
Connects to best buy api.

## progression:
1. use regular request package and save local files
2. add sqlite database integration
3. experiment with azure databases (cosmosdb and sql server db)
4. convert request functions to asyncio functions
5. combine aiohttp with asyncio
6. add email notification when complete
7. async requests
8. publish azure function app on http trigger
9. publish azure function on timer trigger

## http request
[ms learn: azure function run local function](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Cnon-http-trigger%2Ccontainer-apps&pivots=programming-language-python#run-a-local-function)
[stackoverflow: debug azure functions locally](https://stackoverflow.com/questions/55063821/debug-azure-functions-locally/55067597)

non-http trigger request example: 
``` cmd
curl --request POST -H "Content-Type:application/json" --data "{'input':'sample queue data'}" http://localhost:7071/admin/functions/QueueTrigger -v
```


## function binding 
[ms learn: function binding timers](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=python-v2%2Cin-process&pivots=programming-language-python)

### v1 - function.json
caution:
* runOnStartup: If true, the function is invoked when the runtime starts. For example, the runtime starts when the function app wakes up after going idle due to inactivity. when the function app restarts due to function changes, and when the function app scales out. Use with caution. runOnStartup should rarely if ever be set to true, especially in production.

```json
{
    "schedule": "0 */5 * * * *",
    "name": "myTimer",
    "type": "timerTrigger",
    "direction": "in",
    "runOnStartup": true
}
```

### v2 - decorators
caution:
* run_on_startup: If true, the function is invoked when the runtime starts. For example, the runtime starts when the function app wakes up after going idle due to inactivity. when the function app restarts due to function changes, and when the function app scales out. Use with caution. runOnStartup should rarely if ever be set to true, especially in production.
* 
```python
import datetime
import logging
import azure.functions as func

app = func.FunctionApp()

@app.function_name(name="TimerTrigger1")
@app.schedule(schedule="0 */5 * * * *", 
              arg_name="TimerTrigger1",
              run_on_startup=True) 
def test_function(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
```

## resources:
1. [ms learn: azure function python developer guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators)
2. [ms learn: azure function python developer guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators)
3. [ms learn: add dev/test function solution](https://learn.microsoft.com/en-us/answers/questions/1203593/azure-functions-in-dev-prod-enviroment)
4. [ms learn: add dev/test function solution](https://learn.microsoft.com/en-us/answers/questions/1203593/azure-functions-in-dev-prod-enviroment)
5. [ms learn: function binding](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=python-v2%2Cin-process&pivots=programming-language-python)
6. [ms learn: manually run non-http triggers](https://learn.microsoft.com/en-us/azure/azure-functions/functions-manually-run-non-http)
7. [ms learn: develop locally](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local)
8. [ms learn: azure functions run local](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Cnon-http-trigger%2Ccontainer-apps&pivots=programming-language-python#run-a-local-function)
9. [stackoverflow: debug azure functions locally](https://stackoverflow.com/questions/55063821/debug-azure-functions-locally/55067597)
10. [stackoverflow: azure functions trigger timer trigger locally](https://stackoverflow.com/questions/47541981/azure-functions-trigger-timer-trigger-locally)
11. [stackoverflow: curl to powershell](https://stackoverflow.com/questions/71168528/curl-to-powershell-command)
