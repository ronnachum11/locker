from locust import HttpUser, task, between

class WebsiteTestUser(HttpUser):
    wait_time = between(0.5, 3.0)

    def on_start(self):
        pass    

    @task(1)
    def hello_world(self):
        self.client.post("/login", {"username":"ronnachum13@gmail.com", "password":"password"})
        self.client.get("/logout")