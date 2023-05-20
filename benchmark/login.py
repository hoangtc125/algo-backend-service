from locust import HttpUser, between, task


class MyUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def login(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"username": "trconghoangg@gmail.com", "password": "string"}
        response = self.client.post("/account/login", data=data, headers=headers)
        if response.status_code == 200:
            print("Login successful")
        else:
            print("Login failed")
