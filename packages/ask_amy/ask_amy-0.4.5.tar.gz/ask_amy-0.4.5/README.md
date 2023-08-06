[![Build Status](https://travis-ci.org/dphiggs01/Ask_Amy.svg?branch=master)](https://travis-ci.org/dphiggs01/Ask_Amy)

<img src="sphinx/_static/header.png"/>

#

<img src="sphinx/_static/interaction_diagram.png" height="214" width="300"/>

**ASK Amy** is a fun and easy to use framework for developing Alexa Skills. We hope you will like the design approaches
we have taken to help simplify many of the complexities of developing Alexa Skills. The framework helps new skills
developers with many *sample applications* that can be deployed in minutes and then modified to meet specific use cases.
Advanced developers will find that although the framework provides many best practice patterns and guardrails the full
Alex Request JSON is always available for interrogation for niche cases.


### Ask Amy Features

* The **Template Skill Code Generator** creates a deploy-able skill template from an Alexa Intent Schema JSON file.
* A **AWS CLI Wrapper** simplifies Lambda function creation, deployment, and CloudWatch log file dumps.
* The **No Code Persistence** provides automatic saving and restoration of session state attributes across skill invocations.
* **Multiple Data Scopes** supports encapsulation of attributes at the Request, Intent, Session, and Application scopes which enhances data visibility and minimizes the use of session scope attributes when it is not required or desired.
* The **JSON to Object Marshalling** feature, automatically converts Alex JSON Events into Python Objects and Converts Python Reply Objects into Alex JSON format for return to the Alexa Service.
* The **State Manager** provides a simple yet powerful finite state machine that manages *expected intents* and *required field processing*.
* Numerous **Sample Applications** are provided, demonstrating Amazon's blueprint samples from their Java and Node.JS GitHub repos.
* Comprehensive **Logging and log level throttling** is provided to support development, debug, & production monitoring.


<img src="sphinx/_static/ask_amy_framework.png" height="450" width="600"/>

#

<img src="sphinx/_static/event_model.png" height="450" width="600"/>

### Check Out Ask Amy Website for more details

*  https://dphiggs01.github.io/ask_amy/

