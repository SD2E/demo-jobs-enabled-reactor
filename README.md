PIPELINE JOBS MANAGER
=====================

Ssupports a stateful job tracking service for SD2 Data Catalog. This actor can
process messages to accomplish the following goals. Behavior is determined by
which JSON schema the incoming message validates to.

Actions:
* create - Create a new job for a given pipeline_uuid. Schema: `create.json`
* event - Send a state-change event to a given job by its UUID. Schema: `event.jsonschema`
* delete - Delete a job (actually hides it unless forced)

The actor can also respond to POST callbacks, for instance from the Agave jobs
service. In this case, it can process the the message body as job "data" and
reads the job UUID and event from url parameters. A jobs callback is detected
using the `agavejobs.jsonschema`.

Actor Messages
--------------

A Pipelines actor may update the status of its own job by sending an event
message status to this actor with the following schema:

```json
{
	"$schema": "http://json-schema.org/draft-04/schema#",
	"title": "PipelinesJobStateEvent",
	"description": "Directly send a state-change event to a Pipelines Job",
	"type": "object",
	"properties": {
		"uuid": {
			"description": "a UUID referring to a known Pipeline Job",
			"type": "string"
		},
		"event": {
			"description": "a valid Pipeline Job state-change event",
			"type": "string",
			"enum": ["run", "fail", "finish", "validate", "validated", "reject", "finalize", "retire"]
		},
		"details": {
			"description": "an object containing additional context about the event (optional)",
			"type": "object"
		},
		"__options": {
			"type": "object",
			"description": "an object used to pass runtime options to a pipeline (private, optional)"
		}
	},
	"required": ["uuid", "event"],
	"additionalProperties": false
}
```

Agave Job Notifications
-----------------------

When this actor creates a job, it returns a webook, which must be incorporated
into the notifications stanza for Agave jobs that it launches.

https://api.sd2e.org/actors/v2/<THISACTOR>/messages?x-nonce=<Nonce>&event=<Event>&uuid=<JobId>
