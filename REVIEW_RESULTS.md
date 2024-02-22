> After careful consideration, we have decided to move forward with other candidates who more closely fit the current needs of the team. This is the feedback I have received from the engineering team:

> Poor naming in the models. It is not clear at all which is used for what - i.e, Error and Error1 or SearchGetResponse and SearchGetResponse1. I would recommend to invest a little time to identify properly the models and give them a clear name. Besides, the modeling proposed is quite coupled to the external provider.

**My answer**: naming for models came from documentation (Swagger/OpenAPI spec file), I didn't touch the specification and took it as is because of the challenge requirement _"The Open API specification should be respected."_ In fact, models code was automatically generated with [fastapi-codegen](https://github.com/koxudaxi/fastapi-code-generator). And using code generation is well-established approach for production ready apps where your OpenAPI spec is the single source of truth and some code often re-generated from it.

> The storage part looks good, put an abstraction in the middle to give the autonomy to implement it as needed. We would expect the same for the parsing components, but it is coupled to XML. To integrate another data format, like JSON, we will need to implement a new parser and change the class that uses it.

**My answer**: First, I wouldn't implement next monolith that would parse all possible formats, partners, etc. I would stick to microservices approach. Second, I would apply incremental development approach and would solve architectural issues on terms of their business demands.

> Also, is good to use background tasks to fetch the events, making the response faster but I find this approach very problematic. What will we response to the first customer? How can we decide how often we want to update the events we have stored? How will we retry to fetch if the background task raises a timeout error or similars applying a backoff? The solution delegates all these responsabilities out of our control.

**My answer**: I utilised eventual consistency pattern with background tasks to reach the sub-ms response time and decouple the request processing from returning response. I don't think we may need here exponential back-off taking in mind number of expected requests.

> The tests are good, but the lack of the dependency injection is some of the classes/functions make them harder, requiring to patch some of them. This is a problem well-solved by FastAPI.

**My answer**: There's nothing wrong with patching in tests.

> In my opinion the solution has good points, like the use of background tasks and is more or less tested but is not good enough, mainly because the lack of extensibility and scalability in the real scenario of have to integrate several providers with different casuistics, besides the poorly named and the coupling with the provider increases the lack mentioned before.

**My answer**: I see your incline toward using SOLID and Clean Code here and there, but we shouldn't overly re-apply them if the only thing they add is code complexity. It may work though on codebase growing. Having all the possible Design and Architectural patterns implemented for MVP would just bloat it without added value.

> Thanks to you to take the time to complete the test, but it is not good enough to fulfill the requirements we need to ensure.

**My answer**: There is no ideal solution. In fact, nobody able implement it from the first approach and most of the time teams working incrementally on it, adding new features, changing and evolving software over time.

Software Engineering is an open-ended process and most things in the solution are discussable, that's why I put some thoughts in NOTES.md; What is production (a bare metal, cloud platform), what platform (is it a virtual machine, Kubernetes cluster, a Lambda function), what team and even budget we have? Even business model may impact on how would we design and implement our code.