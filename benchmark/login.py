from locust import HttpUser, between, task


class MyUser(HttpUser):
    wait_time = between(1, 3)
    access_token = None
    logged_in = False

    @task(1)
    def login(self):
        if self.logged_in:
            return
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"username": "trconghoangg@gmail.com", "password": "string"}
        response = self.client.post("/account/login", data=data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.access_token = f"{data['token_type']} {data['access_token']}"
            self.logged_in = True
        else:
            print("Login failed")

    @task
    def get_about_me(self):
        if self.access_token is None:
            return
        headers = {"Authorization": self.access_token}
        response = self.client.get("/account/me", headers=headers)
        if response.status_code == 200:
            print("About Me API called successfully")
        else:
            print("Failed to call About Me API")

    @task
    def get_all(self):
        if self.access_token is None:
            return
        headers = {"Authorization": self.access_token}
        response = self.client.post(
            "/account/get-all?page_size=20&orderby=created_at&sort=-1", headers=headers
        )
        if response.status_code == 200:
            print("Get all API called successfully")
        else:
            print("Failed to call Get all API")
