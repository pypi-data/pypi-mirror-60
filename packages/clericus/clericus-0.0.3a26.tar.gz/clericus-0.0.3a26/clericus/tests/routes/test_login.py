import unittest
import faker

from aiohttp.test_utils import unittest_run_loop

from ..test_case import AuthenticatedClericusTestCase

fake = faker.Faker()


class LoginTestCase(AuthenticatedClericusTestCase):
    @unittest_run_loop
    async def testLogin(self):
        resp = await self.client.request("GET", "/me/")
        # not logged in
        self.assertEqual(resp.status, 401)
        data = await resp.json()

        user = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),
        }
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        # sign up
        self.assertEqual(resp.status, 200)

        resp = await self.client.request("GET", "/me/")
        # logged in from signup
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data["currentUser"]["username"], user["username"])

        resp = await self.client.request("GET", "/log-out/")
        # log out
        self.assertEqual(resp.status, 200)
        data = await resp.json()

        # logged out from log-out
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)

        resp = await self.client.request(
            "POST",
            "/log-in/",
            json={
                "email": user["email"],
                "password": user["password"],
            },
        )
        # log in
        self.assertEqual(resp.status, 200)
        data = await resp.json()

        # logged in successfully
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 200)

    @unittest_run_loop
    async def testInvalidPassword(self):
        user = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),
        }
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        # sign up
        self.assertEqual(resp.status, 200)

        resp = await self.client.request("GET", "/log-out/")
        # log out
        self.assertEqual(resp.status, 200)

        resp = await self.client.request(
            "POST",
            "/log-in/",
            json={
                "email": user["email"],
                "password": user["password"] + "moo",
            },
        )
        # log in
        self.assertEqual(resp.status, 401)
        data = await resp.json()

        # logged in successfully
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)

    @unittest_run_loop
    async def testInvalidEmail(self):
        user = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),
        }
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        # sign up
        self.assertEqual(resp.status, 200)

        resp = await self.client.request("GET", "/log-out/")
        # log out
        self.assertEqual(resp.status, 200)

        resp = await self.client.request(
            "POST",
            "/log-in/",
            json={
                "email": fake.email(),
                "password": user["password"],
            },
        )
        # log in
        self.assertEqual(resp.status, 401)
        data = await resp.json()

        # logged in successfully
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)

    @unittest_run_loop
    async def testEmptyBody(self):

        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json={},
        )
        # sign up
        self.assertEqual(resp.status, 422)
        body = await resp.json()
        self.assertEqual(len(body["errors"]), 3)


if __name__ == '__main__':
    unittest.main()