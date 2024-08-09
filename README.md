
# Best Buy API application

Connects to best buy api.

[developer api document](https://developer.bestbuy.com/)

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

## start local function with vscode:

**`local.settings.json` file required**

resource: [quickstart: python function in azure with vscode](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-decorators)

### configure environment

* An Azure account with an active subscription. Create an account for free.
* Python version 3.10.
* Visual Studio Code on one of the supported platforms.
* The Python extension for Visual Studio Code.
* The Azure Functions extension for Visual Studio Code, version 1.8.1 or later.
* The Azurite V3 extension local storage emulator. While you can also use an actual Azure storage account, this article assumes you're using the Azurite emulator.

### configure emulator

resource: [ms learn: start the emulator](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-decorators#start-the-emulator)

1. In Visual Studio Code, press F1 to open the command palette. In the command palette, search for and select Azurite: Start.

1. Check the bottom bar and verify that Azurite emulation services are running. If so, you can now run your function locally.

### run locally with emulator

Visual Studio Code integrates with Azure Functions Core tools to let you run this project on your local development computer before you publish to Azure.

1. To start the function locally, press `F5` or the Run and Debug icon in the left-hand side Activity bar. The Terminal panel displays the Output from Core Tools. Your app starts in the Terminal panel. You can see the URL endpoint of your HTTP-triggered function running locally.

    1. If you have trouble running on Windows, make sure that the default terminal for Visual Studio Code isn't set to WSL Bash.

1. With Core Tools still running in Terminal, choose the Azure icon in the activity bar. In the Workspace area, expand Local Project > Functions. Right-click (Windows) or `Ctrl -` click (macOS) the new function and choose Execute Function Now....

1. In Enter request body you see the request message body value of { "name": "Azure" }. Press Enter to send this request message to your function.

1. When the function executes locally and returns a response, a notification is raised in Visual Studio Code. Information about the function execution is shown in Terminal panel.

1. With the Terminal panel focused, press `Ctrl + C` to stop Core Tools and disconnect the debugger.

## start local function with command line:

> **`local.settings.json` file required**
>
> resource: [quickstart: python function in azure with command line](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?tabs=windows%2Cbash%2Cazure-cli&pivots=python-mode-decorators)
> 
> This folder contains various files for the project, including configuration files named `local.settings.json` and `host.json`. Because *`local.settings.json`* can contain secrets downloaded from Azure, the file is excluded from source control by default in the *`.gitignore`* file.


1. Install the Azure Functions Core Tools

1. Create and activate virtual environment

    ```powershell
    py -m venv .venv
    ```

    ```powershell
    .venv\scripts\activate
    ```

1. Create local function

    v1  

    ```powershell
    func init --worker-runtime python
    ```

    ```powershell
    func start
    ```

    v2  

    ```powershell
    func init --worker-runtime python -m v2
    ```

    local.settings.json
    ```json
    {
    "IsEncrypted": false,
    "Values": {
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
        "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        ...
    }
    }
    ```

    > azurite: You can skip this step if the `AzureWebJobsStorage` setting in `local.settings.json` is set to the connection string for an Azure Storage account instead of `UseDevelopmentStorage=true`.

    ```powershell
    azurite
    ```

    ```powershell
    func start
    ```

1. Copy the URL of your HTTP function from this output to a browser and append the query string `?name=<YOUR_NAME>`, making the full URL like `http://localhost:7071/api/HttpExample?name=Functions`. The browser should display a response message that echoes back your query string value. The terminal in which you started your project also shows log output as you make requests.

1. When you're done, press `Ctrl + C` and type `y` to stop the functions host.

## http request

* [ms learn: azure function run local function](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Cnon-http-trigger%2Ccontainer-apps&pivots=programming-language-python#run-a-local-function)

* [stackoverflow: debug azure functions locally](https://stackoverflow.com/questions/55063821/debug-azure-functions-locally/55067597)

http trigger request example:

```cmd
http://localhost:<PORT>/api/<FUNCTION_NAME>
```

```cmd
curl --get http://localhost:7071/api/MyHttpTrigger?name=Azure%20Rocks
```

non-http trigger request example: 
[documentation](https://learn.microsoft.com/en-us/azure/azure-functions/functions-manually-run-non-http?tabs=azure-portal)

```cmd
curl --request POST -H "Content-Type:application/json" --data "{'input':'sample queue data'}" http://localhost:7071/admin/functions/QueueTrigger -v
```

## function binding 

[ms learn: function binding timers](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=python-v2%2Cin-process&pivots=programming-language-python)

### v1 - function.json

> **caution**:
> 
> runOnStartup: If true, the function is invoked when the runtime starts. For example, the runtime starts when the function app wakes up after going idle due to inactivity. when the function app restarts due to function changes, and when the function app scales out. Use with caution. runOnStartup should rarely if ever be set to true, especially in production.

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

> **caution**:
> 
> run_on_startup: If true, the function is invoked when the runtime starts. For example, the runtime starts when the function app wakes up after going idle due to inactivity. when the function app restarts due to function changes, and when the function app scales out. Use with caution. runOnStartup should rarely if ever be set to true, especially in production.
 
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

## changing python version

### Valid linuxFxVersion values
```powershell
az functionapp list-runtimes --os linux --query "[].{stack:join(' ', [runtime, version]), LinuxFxVersion:linux_fx_version, SupportedFunctionsVersions:to_string(supported_functions_versions[])}" --output table
```
output
```powershell
Stack              LinuxFxVersion       SupportedFunctionsVersions
-----------------  -------------------  ----------------------------
dotnet-isolated 8  DOTNET-ISOLATED|8.0  ["4"]
dotnet-isolated 7  DOTNET-ISOLATED|7.0  ["4"]
dotnet-isolated 6  DOTNET-ISOLATED|6.0  ["4"]
dotnet 6           DOTNET|6.0           ["4"]
node 20            Node|20              ["4"]
node 18            Node|18              ["4"]
node 16            Node|16              ["4"]
node 14            Node|14              ["4","3"]
python 3.11        Python|3.11          ["4"]
python 3.10        Python|3.10          ["4"]
python 3.9         Python|3.9           ["4","3"]
python 3.8         Python|3.8           ["4","3"]
python 3.7         Python|3.7           ["4","3"]
java 17.0          Java|17              ["4"]
java 11.0          Java|11              ["4","3"]
java 8.0           Java|8               ["4","3"]
powershell 7.2     PowerShell|7.2       ["4"]
custom                                  ["4","3"]
```
### view current runtime version
```powershell
az functionapp config show --name <function_app> \
--resource-group <my_resource_group> --query 'linuxFxVersion' -o tsv
```
output
```powershell
PYTHON|3.8
```

### update runtime version ("Python|3.10")
```powershell
az functionapp config set --name <FUNCTION_APP> \
--resource-group <RESOURCE_GROUP> \
--linux-fx-version <"LINUX_FX_VERSION">
```

## additional resources:

1. [ms learn: azure function python developer guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators)

1. [ms learn: azure function python developer guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators)

1. [ms learn: add dev/test function solution](https://learn.microsoft.com/en-us/answers/questions/1203593/azure-functions-in-dev-prod-enviroment)

1. [ms learn: add dev/test function solution](https://learn.microsoft.com/en-us/answers/questions/1203593/azure-functions-in-dev-prod-enviroment)

1. [ms learn: function binding](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=python-v2%2Cin-process&pivots=programming-language-python)

1. [ms learn: manually run non-http triggers](https://learn.microsoft.com/en-us/azure/azure-functions/functions-manually-run-non-http)

1. [ms learn: develop locally](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local)

1. [ms learn: azure functions run local](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Cnon-http-trigger%2Ccontainer-apps&pivots=programming-language-python#run-a-local-function)

1. [ms learn: functions reference python](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators)

1. [ms learn: how to pin a python version](https://learn.microsoft.com/en-us/azure/azure-functions/set-runtime-version?tabs=portal#manual-version-updates-on-linux)

1. [ms learn: app service site settings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings#app-service-site-settings)

1. [stackoverflow: debug azure functions locally](https://stackoverflow.com/questions/55063821/debug-azure-functions-locally/55067597)

1. [stackoverflow: azure functions trigger timer trigger locally](https://stackoverflow.com/questions/47541981/azure-functions-trigger-timer-trigger-locally)

1. [stackoverflow: curl to powershell](https://stackoverflow.com/questions/71168528/curl-to-powershell-command)

1. [stackoverflow: how to change python version of azure function](https://stackoverflow.com/questions/72000572/how-to-change-python-version-of-azure-function)