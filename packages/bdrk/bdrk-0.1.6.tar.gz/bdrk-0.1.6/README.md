[Bedrock](https://bedrock.basis-ai.com) helps data scientists own the end-to-end deployment of machine learning workflows. `bdrk` is the official client library for interacting with APIs on Bedrock platform.

## Usage

In order to use `bdrk`, you need to register an account with Basis AI. Please email `contact@basis-ai.com` to get started. Once an account is created, you will be issued a personal API token that you can use to authenticate with Bedrock.

### Installing Bedrock client

You can install Bedrock client library from PyPi with the following command. We recommend running it in a virtual environment to prevent potential dependency conflicts.

```bash
pip install bdrk
```

Note that the client library is officially supported for python 3.7 and above.

#### Installing optional dependencies

The following optional dependencies can be installed to enable additional featues.

Command line support:

```bash
pip install bdrk[cli]
```

Prediction store support:

```bash
pip install bdrk[prediction-store]
```

### Setting up your environment

Once installed, you need to add a well formed `bedrock.hcl` configuration file in your project's root directory. The configuration file specifies which script to run for training and deployment as well as their respective base Docker images. You can find an example directory layout [here](https://github.com/basisai/churn_prediction).

When using the module locally, you may need to define the following environment variables for `bedrock_client` and lab runs to make API calls to Bedrock. These variables will be automatically set on your workload container when running in cluster.

```bash
export BEDROCK_API_DOMAIN=https://api.bdrk.ai
export BEDROCK_API_TOKEN=<your personal API token>
```

### bedrock_client library

The `bedrock_client` library provides utility functions for your training runs.

#### Logging training metrics

You can easily export training metrics to Bedrock by adding logging code to `train.py`. The example below demonstrates logging charts and metrics for visualisation on Bedrock platform.

```python
import logging

from bedrock_client.bedrock.api import BedrockApi

logger = logging.getLogger(__name__)
bedrock = BedrockApi(logger)
bedrock.log_metric("Accuracy", 0.97)
bedrock.log_chart_data([0, 1, 1], [0.1, 0.7, 0.9])
```

### bdrk library

The `bdrk` library provides APIs for interacting with the Bedrock platform.

```python
from bdrk.v1 import ApiClient, Configuration, PipelineApi
from bdrk.v1.models import (
    PipelineResourcesSchema,
    TrainingPipelineRunSchema,
)

configuration = Configuration()
configuration.api_key["X-Bedrock-Access-Token"] = "MY-TOKEN"
configuration.host = "https://api.bdrk.ai"

api_client = ApiClient(configuration)
pipeline_api = PipelineApi(api_client)

pipeline = pipeline_api.get_training_pipeline_by_id(pipeline_id="MY-PIPELINE")
run_schema = TrainingPipelineRunSchema(
    environment_public_id="MY-ENVIRONMENT",
    resources=PipelineResourcesSchema(cpu="500m", memory="200M"),
    script_parameters={"MYPARAM": "1.23"},
)
run = pipeline_api.run_training_pipeline(
    pipeline_id=pipeline.public_id, training_pipeline_run_schema=run_schema
)

```

### Lab run

The `labrun` command can be used to launch test runs of local training code on the Bedrock platform.

```sh
  # Set environment variables with credentials for this session
  $ unset HISTFILE # Don't save history for this session
  $ export BEDROCK_API_DOMAIN=https://api.bdrk.ai
  $ export BEDROCK_API_TOKEN=<your personal API token>

  $ bdrk labrun --help

  $ bdrk labrun --verbose --domain $BEDROCK_API_DOMAIN submit \
        $HOME/basis/span-example-colourtest \
        bedrock.hcl \
        canary-dev \
        --cpu 0.6 \
        --memory 1.1G \
        -p ALPHA=0.9 \
        -p L5_RATIO=0.1 \
        -s DUMMY_SECRET_A=foo \
        -s DUMMY_SECRET_B=bar

  $ bdrk labrun logs <run_id> <run_token>

  $ bdrk labrun artefact <run_id> <run_token>
```

### Logging predictions at serving time

The prediction store can be used at serving time to log model predictions for offline analysis. All predictions are persisted in low cost blob store in the workload cluster with a maximum TTL of 1 month. The blob store is partitioned by the endpoint id and the event timestamp according to the following structure: `models/predictions/{endpoint_id}/2020-01-22/1415_{logger_id}-{replica_id}.txt`.

- The endpoint id is the first portion of your domain name hosted on Bedrock
- The replica id is the name of your model server pod
- The logger id is a Bedrock generated name that's unique to the log collector pod

Both properties are injected automatically into your model server container as environment variables.

All prediction logging are performed asynchronously in the background to minimize overhead along the request handling critical path. We measured the additional latency to be less than 1 ms per request.

```python
from bedrock_client.bedrock.prediction_store import PredictionStore

store = PredictionStore()
store.log_prediction(request_body='{"event_id": "123"}', features=[0, 2, 1], output=0.921)
```
