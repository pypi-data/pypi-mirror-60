import inspect
import traceback

from aiohttp import web
from inspect import getdoc

from ..parsing import RequestParser, ResponseSerializer, DictParser
from ..errors import HTTPError, ClientError, ErrorList


class Method():
    name = "Handler"
    description = ""

    def __init__(
        self,
        settings=None,
        statusCode=200,
        headers=None,
        cookies=None,
        deletedCookies=None,
        tests=[],
    ):
        self.statusCode = statusCode
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.deletedCookies = deletedCookies or {}
        self.settings = settings or {}
        self.tests = tests or getattr(self, "tests", [])

    class Parser(RequestParser):
        pass

    class Serializer(ResponseSerializer):
        pass

    async def parse(self, request):
        return await self.Parser(settings=self.settings).parse(request)

    async def process(self, **kwargs):
        return {}

    async def serialize(self, result):
        return await self.Serializer().serialize(
            result,
            statusCode=self.statusCode,
            headers=self.headers,
            cookies=self.cookies,
            deletedCookies=self.deletedCookies,
        )

    def setCookie(
        self,
        name,
        value,
        domain=None,
        secure=False,
        httpOnly=False,
        expires=None,
    ):
        self.cookies[name] = {
            "name": name,
            "value": value,
            "domain": domain,
            "secure": secure,
            "httpOnly": httpOnly,
            "expires": expires,
        }

    def unsetCookie(
        self,
        name,
        domain=None,
    ):
        self.deletedCookies[name] = {
            "name": name,
            "domain": domain,
        }

    def setHeader(self, name, value):
        if name in self.headers:
            self.headers[name].append(value)
        else:
            self.headers[name] = [value]

    async def handle(self, request: web.Request) -> web.Response:
        try:
            parsedData = await self.parse(request)
            parameters = inspect.signature(self.process).parameters
            if "currentUser" in parameters:
                # if the process function wants the current user, fill it
                # in from the authentication middleware
                currentUser = getattr(
                    request,
                    "currentUser",
                    None,
                )
                if all([
                    currentUser == None,
                    parameters["currentUser"].default ==
                    inspect.Parameter.empty,
                ]):
                    raise ClientError(
                        statusCode=401,
                        message="Unauthorized",
                        errorType="AuthenticationError",
                    )

                parsedData["currentUser"] = currentUser
            result = await self.process(**parsedData)
            return await self.serialize(result, )
        except ErrorList as errors:
            return web.json_response(
                {"errors": [e.toJSON() for e in errors.errors]},
                status=errors.errors[0].statusCode,
            )
        except web.HTTPException as err:
            raise err
        except HTTPError as e:
            return web.json_response(
                {"errors": [e.toJSON()]},
                status=e.statusCode,
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return web.json_response(
                {
                    "errors": [{
                        "message": "Server Error",
                        "errorType": "Unknown",
                    }]
                },
                status=500,
            )

    def describe(self):
        return {
            "name": self.name,
            "description": getattr(self, "description", getdoc(self)),
            "requestParameters": self.Parser().describe(),
            "response": self.Serializer().describe(),
            "examples": [{
                "request": test.request,
                "response": test.response,
            } for test in self.getTests()]
        }

    def getTests(self):
        return self.tests or []


def newMethod(
    name,
    httpMethod,
    description,
    process,
    urlParameters=None,
    queryParameters=None,
    cookieParameters=None,
    headerParameters=None,
    bodyParameters=None,
    responseFields=None,
    tests=None,
):
    """
    Create a new class for the given http method, filling in the
    parsers and the serializer with the given values.
    """
    classMap = {
        "UrlParser": urlParameters,
        "QueryParser": queryParameters,
        "CookieParser": cookieParameters,
        "HeaderParser": headerParameters,
        "BodyParser": bodyParameters,
    }

    parserAttributes = {}
    for key, params in classMap.items():
        if params:
            parserAttributes[key] = type(
                key,
                (DictParser, ),
                params,
            )

    attributes = {
        "name": name,
        "process": process,
        "__doc__": description,
        "description": description,
        "Parser": type(
            "Parser",
            (RequestParser, ),
            parserAttributes,
        ),
        "Serializer": type(
            "Serializer",
            (ResponseSerializer, ),
            responseFields or {},  # Can't be None
        ),
        "tests": tests or [],
    }

    return type(
        httpMethod,
        (Method, ),
        attributes,
    )
